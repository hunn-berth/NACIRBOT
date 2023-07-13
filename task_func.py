import pandas as pd 
import os
import re
from netmiko import ConnectHandler
import requests
from requests.auth import HTTPBasicAuth
import json

def format_cvs(df):
    df = df.drop_duplicates(subset="IP address")
    return df


def testReachability(df):
    
    df['Reachability'] = ''
    df['OS type'] = ''

    version = re.compile(r'Cisco IOS Software.*,.*, Version (.*),')
    pid = re.compile(r'[C|c]isco\s+([A-Z]+[/-]?[A-Z0-9]{1,}[-/][A-Z0-9]{1,}).*bytes of memory')
    for index, row in df.iterrows():
        ip_address = row['IP address']
        device = {
        'device_type': 'cisco_ios',
        'ip': ip_address,
        'username': 'admin',
        'password': 'cisco!123',
        'secret': 'cisco!123'
        }   
        #ping_reply = os.system(f"ping -c 1 -W 1 {ip_address} > /dev/null 2>&1")
        # For windows users:
        ping_reply = os.system(f"ping -n 1 -w 1 {ip_address}")
        #ping_reply = os.system(f"ping -n 1 -w 1 {ip_address}")
        # Please keep in mind that for windows users, they may need to run this block of code twice
        if ping_reply == 0:
            df.at[index, 'Reachability'] = 'Reachable'
            try:
                connection = ConnectHandler(**device)
                output = connection.send_command('show version')
                version_output = version.search(output).group(1)
                pid_output = pid.search(output).group(1)
                if "Cisco IOS-XE" in output:
                    df.at[index, 'OS type'] = "IOS-XE"
                else:
                    df.at[index, 'OS type'] = "IOS"
                #print (output)
                #print (version_output)
                #print (pid_output)
                df.at[index, 'Version'] = version_output
                df.at[index, 'PID'] = pid_output
                connection.disconnect()
            except Exception as e:
                print(f"Failed to retrieve info from {ip_address}: {str(e)}")
        else:
            df.at[index, 'Reachability'] = 'Unreachable'       
    #df.to_csv(csv_file, index = False)
    return df 

def checkNetconf(df):
    config_line = 'restconf'
    for index, row in df.iterrows():
        ip_address = row['IP address']
        device = {
            'device_type': 'cisco_ios',
            'ip': ip_address,
            'username': 'admin',
            'password': 'cisco!123',
            'secret': 'cisco!123'
        }
        if row['OS type']== 'IOS-XE':  
            try:
                connection = ConnectHandler(**device)
                output = connection.send_command('show run')
                if config_line in output:
                    df.at[index, 'Configured restconf'] = "Restconf enabled"
                else:
                    connection.send_command('restconf')
                    #df.at[index, 'Configured restconf'] = "No Restconf"
                    df.at[index, 'Configured restconf'] = "Restconf was enabled"
                connection.disconnect()
            except Exception as e:
                print(f"Failed to retrieve info from {ip_address}: {str(e)}")
        elif row['OS type']== 'IOS':
            df.at[index, 'Configured restconf'] = "Not supported"
        else:
            df.at[index, 'Configured restconf'] = "Unreachable/Unknown"
    return df

def retriveWithRestconf(df):
    df['Total_proc_mem'] = ''
    df['Used_proc_mem'] = ''
    df['Serial'] = ''
    df['Part_ID_restconf'] = ''
    
    for index, row in df.iterrows():
        ip_address = row['IP address']
        
        if row['OS type']== 'IOS-XE' and row['Configured restconf'] == "Restconf enabled":
            device = {
                'ip': ip_address,
                'username': 'admin',
                'password': 'cisco!123',
                    }
            headers = {
                'Accept': 'application/yang-data+json',
                    }
            # Check the memory usage with restconf
            # Find the correct yang model in: https://github.com/YangModels/yang/tree/main/vendor/cisco/xe
            url_mem = f"https://{ip_address}/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics"
            response = requests.get(url_mem, headers=headers, verify=False, auth=HTTPBasicAuth(device['username'], device['password']))
            
            if response.status_code == 200:
                response = response.json()
                # Parse the response to only get the Processor total and used memory information
                memory_statistics = response['Cisco-IOS-XE-memory-oper:memory-statistics']['memory-statistic']
                # print(response)
                for element in memory_statistics:
                    if element['name'] == 'Processor':
                        total_memory = element['total-memory']
                        used_memory = element['used-memory']
                        df.at[index, 'Total_proc_mem'] = total_memory
                        df.at[index, 'Used_proc_mem'] = used_memory
                #print (memory_statistics)
            else:
                print (f"Received response ccode: {response.status_code}")
            
            # Check for Serial Number and Part ID with restconf - you can use the UDI license path.
            url_lic = f"https://{ip_address}/restconf/data/Cisco-IOS-XE-native:native/license/udi"
            response = requests.get(url_lic, headers=headers, verify=False, auth=HTTPBasicAuth(device['username'], device['password']))
            
            if response.status_code == 200:
                response = response.json()
                sn_value = response['Cisco-IOS-XE-native:udi']['sn']
                pid_value = response['Cisco-IOS-XE-native:udi']['pid']
                df.at[index, 'Serial'] = sn_value
                df.at[index, 'Part_ID_restconf'] = pid_value
                #print (response)

            else:
                print (f"Received response code: {response.status_code}")
                df.at[index, 'Serial'] = "Can't retrieve SN"
                df.at[index, 'Part_ID_restconf'] = "Can't retrieve PID"

    return df


def getToken():
    token = ''
    url = 'https://id.cisco.com/oauth2/default/v1/token'
    data = {
        'client_id': '63ed3gpqg5jbrrmbdch6zd4d',
        'client_secret': 'fTrzZVVTAMP9AdcRTXPvbSyS',
        'grant_type': 'client_credentials',
    }
    response = requests.post(url, data=data)
    # Validate we are getting a 200 status code
    if response.status_code == 200:
        # Parse the response in json format
        token = response.json().get('access_token')
        # Print your token
        print(f'Access token: {token}')
        return token
    else:
        print(f'Request failed with status code {response.status_code}')
        return False



def get_potentialBugs(df):

    token = getToken()
    if token == False:
        print("bug en bug")
        return df
    else:
        df['Potential_bugs'] = ''
        
        headers = {
            'Authorization': f'Bearer {token}',
            }

        for index, row in df.iterrows():
            # Read the column that contains the Part ID of the device
            device_id = row['PID']
            if device_id:
                try:
                    url = f"https://apix.cisco.com/bug/v3.0/bugs/products/product_id/{device_id}?page_index=1&modified_date=5"
                    response = requests.get(url, headers=headers)
                    
                    # Validate the status code as 200
                    if response.status_code == 200:
                        # Parse the response in json format
                        response_data = (response.json())
                        #Print the response_data so you can see how to filter it to just keep the bug ID
                        print (response_data)
                        
                        # List comprehension in python: https://realpython.com/list-comprehension-python/
                        bug_id = [bug['bug_id'] for bug in response_data['bugs']]
                        # Update the bug_id information in the proper column/row
                        df.at[index, 'Potential_bugs'] = bug_id
                    else:
                        print(f'Request failed with status code {response.status_code}')
                        df.at[index, 'Potential_bugs'] = 'Wrong API access'
                except Exception as e:
                    print(f"Failed to retrieve info from {device_id}: {str(e)}")
        
            # Now, let's filter the response, and just get the bug_id, everything else, even though is important information
            # will not be relevant for this task

            # Save the result in a new file named task_3_1
        return df


def get_PSIRT(df):
    token = getToken()
    if token == False:
        return df
    else:
        df['PSIRT'] = ''
        df['CRITICAL_PSIRT'] = ''

        # Define the proper authorization in the headers field
        headers = {
            'Authorization': f'Bearer {token}',
        }

        for index, row in df.iterrows():
            # Read the column that contains the Part ID of the device
            version = row['Version']
            if version:
                try:
                    url = f"https://apix.cisco.com/security/advisories/v2/OSType/iosxe?version={version}"
                    response = requests.get(url, headers=headers)
                    
                    # Validate the status code as 200
                    if response.status_code == 200:
                        # Parse the response in json format
                        response_data = (response.json())
                        #Print the response_data so you can see how to filter it to just keep the bug ID
                        print (response_data)
                        
                        
                        # List comprehension in python: https://realpython.com/list-comprehension-python/
                        advisoryId = [bug['advisoryId'] for bug in response_data['advisories']]
                        # Update the bug_id information in the proper column/row
                        df.at[index, 'PSIRT'] = advisoryId
                        

                        list_critical=[]
                        for bug in response_data['advisories']:
                            if float(bug['cvssBaseScore']) >= 7.5:
                                list_critical.append(bug['advisoryId'])

                        df.at[index, 'CRITICAL_PSIRT'] = list_critical

                    else:
                        print(f'Request failed with status code {response.status_code}')
                        df.at[index, 'PSIRT'] = 'Wrong API access'
                        df.at[index, 'CRITICAL_PSIRT'] = 'Wrong API access'
                except Exception as e:
                    print(f"Failed to retrieve info from {version}: {str(e)}")
        
        return df