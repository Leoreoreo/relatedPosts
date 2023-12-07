import subprocess
import requests
import math
import json
import re
import random
import argparse
from time import sleep
import openpyn

GOOGLE_API_KEY = 'AIzaSyAIfPKA2KYccYTg-AzJ1aKR1e1iK_slCHM' 


def geocode(address_or_zipcode):
    lat, lng = None, None
    api_key = GOOGLE_API_KEY
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={address_or_zipcode}&key={api_key}"
    # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None, None
    try:
        '''
        This try block incase any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
    except:
        pass
    return lat, lng


def haversine(lat1, lon1, lat2, lon2):
    r = 6371  # radius of Earth in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    res = r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
    return res


def get_all_us_servers():
    command = "openpyn -l us" 
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()

    pattern = r"Server = (\w+)\s*,\s*Load = (\d+)"
    matches = re.findall(pattern, output)
    result = [[server, int(load)] for server, load in matches]

    # Save result as JSON file
    with open('servers.json', 'w') as file:
        json.dump(result, file)

    print("Result saved as servers.json")


def get_ip_location_from_servers():
    #format: location (city): {server, ip, load}
    # loc_servers = {}

    with open('servers_completed.json', 'r') as file:
        loc_servers = json.load(file)

    with open('servers.json', 'r') as file:
        servers = json.load(file)

    num_save = 10
    cnt = 0

    for server in servers:
        if int(server[0][2:])<=6945:
            continue
        cnt+=1
        proc = subprocess.Popen(['openpyn', '-s', server[0]], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT,
                                text=True)
        
        while True:
            # Read line from stdout
            line = proc.stdout.readline().strip()

            # Break loop if subprocess is done
            if not line and proc.poll() is not None:
                break

            # Check if line contains the specified text
            if "PUSH: Received control message:" in line:
                # Now we can check your IP and location
                response = requests.get('http://ip-api.com/json/')
                data = json.loads(response.text)
                break  # if you want to terminate the process after getting the IP and location

            sleep(1)  # Optional: Sleep for a short time to reduce CPU usage

        # response = requests.get('http://ip-api.com/json/')
        # data = json.loads(response.text)

        print(server[0])
        print("IP:", data["query"])
        print("Location:", data["city"])

        if data["city"] in loc_servers.keys():
            loc_servers[data["city"]].append({"server": server[0], "ip":data["query"], "load":server[1]})
        else:
            loc_servers[data["city"]] = []
            loc_servers[data["city"]].append({"server": server[0], "ip":data["query"], "load":server[1]})
        
        print(loc_servers[data["city"]])
        print("--------------------------")

        # Terminate the subprocess
        proc.terminate()
    
        if cnt == num_save:
            with open('servers_completed.json', 'w') as file:
                json.dump(loc_servers, file)
            cnt=0

    with open('servers_completed.json', 'w') as file:
        json.dump(loc_servers, file)


def get_closest_ip_loc(pos):
    '''
    location: {server: {ip, load}}
    '''

    with open('../Generator/servers_completed.json', 'r') as file:
        servers_completed = json.load(file)

    with open('../Generator/servers_loc.json', 'r') as file:
        servers_loc = json.load(file)

    lat, lng = None, None
    while lat is None and lng is None:
        lat, lng = geocode(pos)

    min_distance = math.inf
    final_ip_loc = None
    for ip_loc in servers_loc:
        lat2 = servers_loc[ip_loc]["lat"]
        lng2 = servers_loc[ip_loc]["lng"]
        distance = haversine(lat, lng, lat2, lng2)
        if distance < min_distance:
            min_distance = distance
            final_ip_loc = ip_loc

    result = random.choice(servers_completed[final_ip_loc])

    return(final_ip_loc, result)


# def connect_to_vpn(pos):
#     loc, vpn = get_closest_ip_loc(pos)
#     print(loc," ", vpn)
#     server_name = vpn["server"]
#     ip = vpn["ip"]
#     load = vpn['load']
#     try:
#         print(f"***Connect to server {server_name} in {loc}, ip: {ip}, load: {load}***")
#         p = subprocess.Popen(['sudo', 'openpyn', '-s', server_name],
#                                 stdout=subprocess.PIPE,
#                                 stderr=subprocess.STDOUT,
#                                 text=True)
#         # p.communicate(pwd)
#
#     except subprocess.CalledProcessError as e:
#         print("Failed to connect to NordVPN:", e)
def connect_to_vpn(pos):
    loc, vpn = get_closest_ip_loc(pos)
    print(loc," ", vpn)
    server_name = vpn["server"]
    ip = vpn["ip"]
    load = vpn['load']
    try:
        # print(f"***Connect to server {server_name} in {loc}, ip: {ip}, load: {load}***")
        print([ip, loc])
        return ip, loc
        # p = subprocess.Popen(['openpyn', '-s', server_name],
        #                      stdout=subprocess.PIPE,
        #                      stderr=subprocess.STDOUT,
        #                      text=True)
        # p.communicate(pwd)

    except subprocess.CalledProcessError as e:
        print("Failed to connect to NordVPN:", e)

def disconnect_to_vpn():
    subprocess.check_call(["openpyn", "-k"])


def main():
    parser = argparse.ArgumentParser(description='use -c to connect to the nearest server at your input location, use -d to disconnect')
    parser.add_argument('-c', '--connect', type=str, help='connect to the nearest server at your input location')
    parser.add_argument('-d', '--disconnect', action='store_true', help='disconnect to the server')

    args = parser.parse_args()

    if args.connect and args.disconnect:
        parser.error("arguments -c and -d are mutually exclusive")

    if args.connect:
        connect_to_vpn(args.connect)
    
    if args.disconnect:
        disconnect_to_vpn()


if __name__ == "__main__":
    connect_to_vpn("San Francisco")
    # main()


