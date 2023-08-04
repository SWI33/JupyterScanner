#!/usr/bin/env python3
import aiohttp
import asyncio
import argparse
import ipaddress
import signal
import sys
import socket

ASCII_ART_BANNER = """
 
░░░░░██╗██╗░░░██╗██████╗░██╗░░░██╗████████╗███████╗██████╗░░██████╗░█████╗░░█████╗░███╗░░██╗███╗░░██╗███████╗██████╗░
░░░░░██║██║░░░██║██╔══██╗╚██╗░██╔╝╚══██╔══╝██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗░██║████╗░██║██╔════╝██╔══██╗
░░░░░██║██║░░░██║██████╔╝░╚████╔╝░░░░██║░░░█████╗░░██████╔╝╚█████╗░██║░░╚═╝███████║██╔██╗██║██╔██╗██║█████╗░░██████╔╝
██╗░░██║██║░░░██║██╔═══╝░░░╚██╔╝░░░░░██║░░░██╔══╝░░██╔══██╗░╚═══██╗██║░░██╗██╔══██║██║╚████║██║╚████║██╔══╝░░██╔══██╗
╚█████╔╝╚██████╔╝██║░░░░░░░░██║░░░░░░██║░░░███████╗██║░░██║██████╔╝╚█████╔╝██║░░██║██║░╚███║██║░╚███║███████╗██║░░██║
░╚════╝░░╚═════╝░╚═╝░░░░░░░░╚═╝░░░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝

"""
print(ASCII_ART_BANNER)

# Function to display green text
def print_green(text):
    print('\033[32m' + text + '\033[0m')

# Function to check if a Jupyter Lab instance is running on an IP and port
async def check_jupyter_lab(session, ip, port):
    try:
        # Resolve the DNS name (if any) to get the IP address
        ip_address = socket.gethostbyname(ip)
        
        url = f"http://{ip_address}:{port}/lab"
        async with session.get(url) as response:
            if "jupyterlab" in await response.text():
                print_green(f"Jupyter Lab instance found at IP: {ip_address}, Port: {port}")
                banner_url = f"http://{ip_address}:{port}/lab/favicon.ico"
                async with session.get(banner_url) as banner_response:
                    if banner_response.status == 200:
                        banner_data = await banner_response.read()
                        with open("jupyter_lab_banner.ico", "wb") as banner_file:
                            banner_file.write(banner_data)
                        print_green("Jupyter Lab banner saved as jupyter_lab_banner.ico")
    except aiohttp.ClientError:
        pass
    except socket.gaierror:
        pass

# Function to scan IP address on common Jupyter ports
async def scan_ip(ip_range):
    start_ip_str, end_ip_str = ip_range.split('-')
    start_ip_int = int(ipaddress.IPv4Address(start_ip_str))
    end_ip_int = int(ipaddress.IPv4Address(end_ip_str))

    jupyter_ports = [8888, 8889, 8890, 30000]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ip_int in range(start_ip_int, end_ip_int + 1):
            ip = str(ipaddress.IPv4Address(ip_int))
            loading_msg = f"Scanning IP address: {ip}  "
            print(loading_msg, end="\r")
            tasks.extend([check_jupyter_lab(session, ip, port) for port in jupyter_ports])
        
        await asyncio.gather(*tasks)

def signal_handler(sig, frame):
    print("\nScan interrupted by user. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JupyterScanner - Scan for Jupyter Lab instances.")
    parser.add_argument("-r", "--range", required=True, help="IP address range in the format 'start_ip-end_ip'")
    args = parser.parse_args()

    ip_range = args.range

    signal.signal(signal.SIGINT, signal_handler)

    asyncio.run(scan_ip(ip_range))

    print("Scan completed.")
