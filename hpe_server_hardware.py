import requests
import pandas as pd
from getpass import getpass

# Step 1: Get Session ID (auth token)
def authenticate_oneview(base_url, username, password):
    auth_url = f"{base_url}/rest/login-sessions"
    headers = {'Content-Type': 'application/json'}
    data = {
        "userName": username,
        "password": password
    }
    response = requests.post(auth_url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()['sessionID']

# Step 2: Get server hardware details
def get_server_hardware(session_id, base_url):
    headers = {
        'Content-Type': 'application/json',
        'Auth': session_id
    }
    url = f"{base_url}/rest/server-hardware"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['members']

# Step 3: Extract relevant information
def parse_hardware_data(hardware_list):
    hardware_data = []
    for hardware in hardware_list:
        model = hardware.get('model', 'N/A')
        model_num = hardware.get('modelNumber', 'N/A')
        cpu = hardware.get('processorCoreCount', 'N/A')
        processor_type = hardware.get('processorType', 'N/A')
        memory = hardware.get('memoryMb', 0) / 1024  # Convert to GB
        memory_sticks = hardware.get('memorySlotCount', 'N/A')
        storage_controller = hardware.get('storage', {}).get('controller', 'N/A')
        hdds = hardware.get('storage', {}).get('numberOfHardDrives', 'N/A')
        storage_capacity = hardware.get('storage', {}).get('totalCapacityGB', 'N/A')

        hardware_data.append({
            'Model': model,
            'Model Number': model_num,
            'CPU Core Count': cpu,
            'Processor Type': processor_type,
            'Memory (GB)': memory,
            'Memory Sticks': memory_sticks,
            'Storage Controller': storage_controller,
            'Number of HDDs': hdds,
            'Total Storage Capacity (GB)': storage_capacity
        })
    
    return hardware_data

# Step 4: Save to spreadsheet
def save_to_spreadsheet(data, filename='server_hardware_info.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

# Main function to tie everything together
def main():
    base_url = input("Enter the OneView base URL (e.g., https://oneview.example.com): ")
    username = input("Enter OneView Username: ")
    password = getpass("Enter OneView Password: ")

    try:
        # Authenticate and get session token
        session_id = authenticate_oneview(base_url, username, password)

        # Retrieve hardware details
        hardware_list = get_server_hardware(session_id, base_url)

        # Parse the data
        hardware_data = parse_hardware_data(hardware_list)

        # Save to spreadsheet
        save_to_spreadsheet(hardware_data)

        print(f"Data saved to 'server_hardware_info.xlsx'.")
    except requests.HTTPError as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
