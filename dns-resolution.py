'''
this script will import a reference hostname/IP source and then compare that information to active DNS records
as written, DNS queries will be sent to the DNS servers programmed on the system the script is being run
with some modification the DNS queries could be directed to any arbitrary DNS system
the script was designed to be extensible, making it trivial to add options/functions to import hostname/IP from additional sources 
'''

# Developed and tested with the following environment
# - OS: windows
# - Python: 3.11.5
# - Target platform:  Solarwinds Orion 2023.1.1
# - Dependencies: solarwinds capability requires install of orionsdk



import socket
import orionsdk
import json
import csv

# Disable SSL warnings
import urllib3
urllib3.disable_warnings()

#variables
domain = '.my domain.com'
outfile = 'dns-resolution.csv'
#optional SW IP if using solarwinds as a reference
sw_server = 'x.x.x.x'

def import_solarwinds():

    #establish connection information
    print('Enter SolarWinds Credentials')
    user = input('Username: ')
    passwd = input('Password: ')

    #create swisclient object
    swis = orionsdk.SwisClient(sw_server, user, passwd)

    #retrieve reference name and IP from solarwinds. query customization may be required for your environment
    print('Querying SolarWinds...')
    response = swis.query("SELECT N.Caption as Hostname, N.IP_Address FROM Orion.Nodes as N WHERE N.CustomProperties.DeviceGroup = 'Network'")
    return response['results']

def import_csv():

    devices = []
    print('CSV file must have hostnames in column A and IP addresses in column B')
    print('The columns should be hostnames and IPs only with no column header')
    while True:
        csv_name = input('Enter the name of the reference csv file:')
        try:
            file_test = open(csv_name, 'r')
            file_test.close()
            break
        except Exception as e:
            print(e)
            continue
    with open(csv_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            devices.append({"Hostname": row[0],
                            "IP_Address": row[1]})
    return devices

def main():

    

    #prompt user for source of hostname/IP reference to be compared to DNS
    print('This scrip will compare a reference source of hostname/IP with DNS records')
    print('Select your source to compare with DNS:')
    print('1) SolarWinds')
    print('2) CSV File')
    while True:
        source = input(':')
        match source:
            case '1': 
                devices = import_solarwinds()
                break
            case '2': 
                devices = import_csv()
                break
            case _: 
                print('Invalid input.  Try again')
                continue
    
    #normalize all host names, appending domain name if needed
    print('Normalizing Data...')
    for device in devices:
        if domain not in device['Hostname']:
            device['Hostname'] = device['Hostname'] + domain

    #perform nslookup on devices
    #if lookup fails, skip further processing and 'continue' at top of loop
    #successful resolution response contains a tuple (hostname_string, emptylist[], listofIPs[])
    #add Status and Resolved_IP keys to each device dictionary
    print('Performing DNS lookups. This can take a few minutes...')
    counter = 0
    for device in devices:
        counter += 1
        if counter == 50: break
        print('lookup device ' + str(counter) + ' of ' + str(len(devices)))
        try:
            lookup = socket.gethostbyname_ex(device['Hostname'])
        except:
            device['Status'] = 'DNS lookup failed'
            device['Resolved_IP'] = ''
            continue
        if len(lookup[2]) > 1:
            device['Status'] = 'Device has multiple Addresses'
            device['Resolved_IP'] = lookup[2]
        elif lookup[2][0] == device['IP_Address']:
            device['Status'] = 'DSN lookup matches'
            device['Resolved_IP'] = lookup[2][0]
        else:
            device['Status'] = 'DNS record does not match'
            device['Resolved_IP'] = lookup[2][0]

    #output findings
    print('Writing output to file...')
    with open('output.txt', 'w') as file:
        file.write(json.dumps(devices, indent=2))
    csv_columns = ['Hostname', 'IP_Address', 'Resolved_IP', 'Status']
    with open(outfile, 'w', newline='\n') as file:
        file.write('Hostname,IP_Address,Resolved_IP,Status\n')
        writer = csv.DictWriter(file, fieldnames=csv_columns)
        for device in devices:
            writer.writerow(device)
    print('Processing complete')

if __name__ == "__main__":
    main()
