import os
import sys
import subprocess
import platform
from datetime import datetime
import socket
import uuid
import re


# -------------------------------------------------------------------
#  AUTO-INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------------------------------------------
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


for package in ["psutil", "tabulate", "colorama"]:
    install_package(package)

import psutil
from tabulate import tabulate
from colorama import Fore, Style, Back, init

# Initialize colorama
init(autoreset=True)


# -------------------------------------------------------------------
#  DETERMINE DOWNLOADS PATH
# -------------------------------------------------------------------
def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# -------------------------------------------------------------------
#  COMMAND EXECUTOR
# -------------------------------------------------------------------
def run_cmd(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        return output.strip()
    except Exception:
        return "Not available / Command failed"


# -------------------------------------------------------------------
#  SYSTEM INFORMATION GATHERING
# -------------------------------------------------------------------
def get_device_specifications():
    info = {
        "Device Name": socket.gethostname(),
        "Processor": platform.processor(),
        "Platform": platform.platform(),
        "Architecture": platform.architecture()[0],
        "System Type": platform.machine(),
        "Python Version": platform.python_version()
    }

    # RAM information
    memory = psutil.virtual_memory()
    info["Installed RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"
    info["Available RAM"] = f"{memory.available / (1024 ** 3):.2f} GB"
    info["RAM Usage"] = f"{memory.percent}%"

    # System uptime
    boot_time = psutil.boot_time()
    uptime = datetime.now() - datetime.fromtimestamp(boot_time)
    info["System Uptime"] = str(uptime).split('.')[0]

    # Windows-specific info
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output("systeminfo", shell=True, text=True, stderr=subprocess.DEVNULL)
            lines = result.split('\n')
            for line in lines:
                if 'OS Name:' in line:
                    info["Edition"] = line.split(':', 1)[1].strip()
                elif 'OS Version:' in line:
                    info["Version"] = line.split(':', 1)[1].strip()
                elif 'Original Install Date:' in line:
                    info["Installed on"] = line.split(':', 1)[1].strip()
                elif 'System Boot Time:' in line:
                    info["Last Boot"] = line.split(':', 1)[1].strip()
        except:
            pass

    return [[k, v] for k, v in info.items()]


def get_storage_details():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "Device": part.device,
                "Mountpoint": part.mountpoint,
                "File System": part.fstype,
                "Total Size (GB)": f"{usage.total / (1024 ** 3):.2f}",
                "Used (GB)": f"{usage.used / (1024 ** 3):.2f}",
                "Free (GB)": f"{usage.free / (1024 ** 3):.2f}",
                "Usage (%)": f"{usage.percent}%"
            })
        except PermissionError:
            continue
    return disks


def get_graphics_card_info():
    gpu_info = []
    if platform.system() == "Windows":
        try:
            output = run_cmd("wmic path win32_videocontroller get name, adapterram, driverversion /format:table")
            if output and "No Instance(s) Available" not in output:
                lines = output.split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip() and not line.startswith('Name'):
                        parts = line.split()
                        if len(parts) >= 1:
                            # More robust parsing
                            name_parts = []
                            driver_version = "Unknown"
                            adapter_ram = "Unknown"

                            for part in parts:
                                if '.' in part and any(char.isdigit() for char in part):
                                    driver_version = part
                                elif part.isdigit() and len(part) > 6:
                                    adapter_ram = f"{int(part) / (1024 ** 3):.2f} GB"
                                else:
                                    name_parts.append(part)

                            name = ' '.join(name_parts).strip()
                            if name:
                                gpu_info.append({
                                    "Graphics Card": name,
                                    "Adapter RAM": adapter_ram,
                                    "Driver Version": driver_version
                                })
        except Exception as e:
            gpu_info.append({"Graphics Card": f"Error: {str(e)}", "Details": "Could not retrieve GPU info"})

    if not gpu_info:
        gpu_info.append({"Graphics Card": "No GPU information available", "Details": "Check system configuration"})

    return gpu_info


def get_network_connections():
    net_info = []
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for interface_name, interface_addresses in interfaces.items():
        interface_data = {
            "Interface Name": interface_name,
            "Status": "Up" if interface_name in stats and stats[interface_name].isup else "Down",
            "MTU": stats[interface_name].mtu if interface_name in stats else "N/A"
        }

        # MAC Address
        mac_address = "None"
        for addr in interface_addresses:
            if addr.family == -1:  # MAC
                mac_address = addr.address
                break
        interface_data["MAC Address"] = mac_address

        # IP Addresses
        ipv4_addrs = []
        ipv6_addrs = []
        for addr in interface_addresses:
            if addr.family == 2:  # IPv4
                ipv4_addrs.append(addr.address)
            elif addr.family == 23:  # IPv6
                ipv6_addrs.append(addr.address)

        interface_data["IPv4 Address"] = ", ".join(ipv4_addrs) if ipv4_addrs else "None"
        interface_data["IPv6 Address"] = ", ".join(ipv6_addrs) if ipv6_addrs else "None"

        net_info.append(interface_data)

    return net_info

def g_pwd(p, w, e, t, s, r, a, g, y, f):
    pwd = input("Enter the Password to access this file : ")
    if pwd == r[2]+e[4]+t[7]+s[3]+y[9]+f[2]+p[11]+w[8]+a[5]+g[1]:
        pass
    else:
        print("You have entered wrong Password !")
        exit()

p = "e1f7dv6i7yt4d"
r = "h7Sg0yt6yjH1"
e = "yg7ja83mf83"
t = "k7g83h7b6sk9j"
s = "t5ha7ui8je72"
y = "5gd3o6h37r2i"
f = "h8i6d7ch7fi"
w = "u4bdgt5h4f7k"
a = "6y8ih4i8rg5"
g = "i47i8p69j3d"

def get_detailed_network_info():
    detailed_info = []
    try:
        # Get DNS information
        dns_output = run_cmd("ipconfig /all")
        dns_servers = []
        gateways = []

        for line in dns_output.split('\n'):
            if "DNS Servers" in line and ":" in line:
                dns_servers.append(line.split(":")[1].strip())
            elif "Default Gateway" in line and ":" in line:
                gateway = line.split(":")[1].strip()
                if gateway and gateway != "":
                    gateways.append(gateway)

        detailed_info.append({
            "Property": "DNS Servers",
            "Value": ", ".join(dns_servers) if dns_servers else "Not available"
        })
        detailed_info.append({
            "Property": "Default Gateway",
            "Value": ", ".join(gateways) if gateways else "Not available"
        })
        detailed_info.append({
            "Property": "Hostname",
            "Value": socket.gethostname()
        })
        detailed_info.append({
            "Property": "FQDN",
            "Value": socket.getfqdn()
        })

        # Get connectivity info
        try:
            # Test IPv4 connectivity
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            ipv4_status = "Connected"
        except:
            ipv4_status = "Disconnected"

        detailed_info.append({
            "Property": "IPv4 Connectivity",
            "Value": ipv4_status
        })

    except Exception as e:
        detailed_info.append({"Property": "Error", "Value": f"Could not retrieve network info: {str(e)}"})

    return detailed_info


def get_data_usage():
    io_counters = psutil.net_io_counters()
    data_usage = [
        {"Metric": "Total Bytes Sent", "Value": f"{io_counters.bytes_sent:,}"},
        {"Metric": "Total Bytes Received", "Value": f"{io_counters.bytes_recv:,}"},
        {"Metric": "Total Packets Sent", "Value": f"{io_counters.packets_sent:,}"},
        {"Metric": "Total Packets Received", "Value": f"{io_counters.packets_recv:,}"},
        {"Metric": "Errors In", "Value": io_counters.errin},
        {"Metric": "Errors Out", "Value": io_counters.errout},
        {"Metric": "Drop In", "Value": io_counters.dropin},
        {"Metric": "Drop Out", "Value": io_counters.dropout}
    ]
    return data_usage


def get_wifi_passwords():
    wifi_info = []
    if platform.system() == "Windows":
        try:
            profiles_output = run_cmd("netsh wlan show profiles")
            profiles = []
            for line in profiles_output.split('\n'):
                if 'All User Profile' in line and ':' in line:
                    profile_name = line.split(':')[1].strip()
                    if profile_name:
                        profiles.append(profile_name)

            for profile in profiles[:8]:  # Limit to first 8 for brevity
                try:
                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear')
                    password = "Not found"
                    for line in key_output.split('\n'):
                        if 'Key Content' in line and ':' in line:
                            password = line.split(':')[1].strip()
                            break
                    wifi_info.append({
                        "SSID": profile,
                        "Password": password
                    })
                except Exception as e:
                    wifi_info.append({
                        "SSID": profile,
                        "Password": f"Error: {str(e)}"
                    })
        except Exception as e:
            wifi_info.append({"SSID": "Error", "Password": f"Could not retrieve WiFi information: {str(e)}"})

    return wifi_info if wifi_info else [{"SSID": "No WiFi profiles found", "Password": "N/A"}]


def get_system_credentials():
    creds_info = []
    if platform.system() == "Windows":
        try:
            output = run_cmd("cmdkey /list")
            if output:
                lines = output.split('\n')
                for line in lines:
                    if 'Target:' in line:
                        target = line.split('Target:')[1].strip()
                        if target:
                            creds_info.append({"Credential Target": target})
        except Exception as e:
            creds_info.append({"Credential Target": f"Could not retrieve credentials: {str(e)}"})

    return creds_info if creds_info else [{"Credential Target": "No stored credentials found"}]


def get_command_history():
    history_info = []
    try:
        history_path = os.path.join(
            os.environ['USERPROFILE'],
            'AppData', 'Roaming', 'Microsoft', 'Windows', 'PowerShell', 'PSReadLine',
            'ConsoleHost_history.txt'
        )

        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8', errors='ignore') as f:
                commands = f.readlines()
                for i, cmd in enumerate(commands[-15:], 1):  # Last 15 commands
                    if cmd.strip():
                        history_info.append({"#": i, "Command": cmd.strip()})
        else:
            history_info.append({"#": 1, "Command": "Command history file not found"})
    except Exception as e:
        history_info.append({"#": 1, "Command": f"Could not retrieve command history: {str(e)}"})

    return history_info if history_info else [{"#": 1, "Command": "No command history available"}]


def get_hardware_connection_properties():
    hardware_info = []
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)

    for interface_name in interfaces:
        if interface_name in stats:
            stat = stats[interface_name]
            io = io_counters.get(interface_name, None)

            # MAC Address
            mac_addr = "None"
            for addr in interfaces[interface_name]:
                if addr.family == -1:  # MAC
                    mac_addr = addr.address
                    break

            hardware_info.append({
                "Name": interface_name,
                "Description": f"Network Interface - {interface_name}",
                "Physical Address (MAC)": mac_addr,
                "Status": "Connected" if stat.isup else "Disconnected",
                "MTU": stat.mtu,
                "Speed (Mbps)": f"{stat.speed} Mbps" if stat.speed > 0 else "Unknown",
                "Bytes Received": f"{io.bytes_recv:,}" if io else "N/A",
                "Bytes Sent": f"{io.bytes_sent:,}" if io else "N/A"
            })

    return hardware_info if hardware_info else [{"Name": "No interfaces", "Status": "N/A"}]


# -------------------------------------------------------------------
#  HTML REPORT GENERATION
# -------------------------------------------------------------------
def generate_html_report():
    downloads = get_downloads_folder()
    html_path = os.path.join(downloads, f"system_report_{datetime.now().strftime('%d.%m.%Y_%H-%M-%S')}.html")

    # Gather all data
    sections_data = {
        "Device Specifications": get_device_specifications(),
        "Storage Details": get_storage_details(),
        "Graphics Card Information": get_graphics_card_info(),
        "Network Connections": get_network_connections(),
        "Detailed Network Properties": get_detailed_network_info(),
        "Data Usage Statistics": get_data_usage(),
        "WiFi Passwords": get_wifi_passwords(),
        "System Credentials": get_system_credentials(),
        "Command History": get_command_history(),
        "Hardware Connection Properties": get_hardware_connection_properties()
    }

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Comprehensive Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'JetBrains Mono', monospace;
                background: #000000;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}

            .header {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                text-align: center;
            }}

            .header h1 {{
                color: #1d2d3d;
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #3498db, #2c3e50);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .header p {{
                color: #4e4e4e;
                font-size: 1.1em;
            }}

            .section {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin-bottom: 25px;
                transition: transform 0.3s ease;
            }}

            .section:hover {{
                transform: translateY(-5.5px);
            }}

            .section h2 {{
                color: #0f1113;
                border-bottom: 2px solid #222324;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 1.3em;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}

            th {{
                background: #9ccc9c;
                color: #1b272a;
                padding: 12px 15px;
                text-align: left;
                font-weight: 600;
            }}

            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #e0e2e3;
            }}

            tr:nth-child(even) {{
                background: #f8f9fa;
            }}

            tr:hover {{
                background: #dcffd9;
            }}

            .status-connected {{
                color: #10f0ad;
                font-weight: bold;
            }}

            .status-disconnected {{
                color: #e74c3c;
                font-weight: bold;
            }}

            .metric-value {{
                font-family: 'Courier New', monospace;
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 4px;
            }}

            .footer {{
                text-align: center;
                color: white;
                margin-top: 40px;
                padding: 20px;
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}

                .header h1 {{
                    font-size: 2em;
                }}

                table {{
                    font-size: 0.8em;
                }}

                th, td {{
                    border: box;
                    border-radius: 12px;
                    padding: 8px 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>System Comprehensive Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
                <p>Device: {socket.gethostname()} | Platform: {platform.platform()}</p>
            </div>
    """

    # Add each section to HTML
    for section_name, data in sections_data.items():
        html_content += f"""
            <div class="section">
                <h2>{section_name}</h2>
        """

        if data:
            if isinstance(data[0], dict):
                # Table data
                headers = list(data[0].keys())
                rows = [[row.get(header, '') for header in headers] for row in data]

                html_content += '<table>'
                html_content += '<thead><tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr></thead>'
                html_content += '<tbody>'
                for row in rows:
                    html_content += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
                html_content += '</tbody></table>'
            else:
                # Key-value data
                html_content += '<table>'
                for item in data:
                    if len(item) == 2:
                        html_content += f'<tr><td><strong>{item[0]}</strong></td><td>{item[1]}</td></tr>'
                html_content += '</table>'
        else:
            html_content += '<p>No data available for this section.</p>'

        html_content += '</div>'

    html_content += """
            <div class="footer">
                <p>Report generated by System Information Scanner</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Write HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_path


# -------------------------------------------------------------------
#  DISPLAY FUNCTIONS WITH COLORAMA
# -------------------------------------------------------------------
def print_section_header(title):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 70}")
    print(f"{title:^70}")
    print(f"{'=' * 70}{Style.RESET_ALL}")


def print_table(data, headers="keys", tablefmt="grid"):
    if data:
        # Use light grey grid lines
        if tablefmt == "grid":
            tablefmt = "simple"  # Lighter grid style
        print(tabulate(data, headers=headers, tablefmt=tablefmt, numalign="left", stralign="left"))
    else:
        print(f"{Fore.YELLOW}No data available{Style.RESET_ALL}")


def print_warning(message):
    print(f"{Fore.YELLOW}{Style.BRIGHT}[!] {message}{Style.RESET_ALL}")


def print_success(message):
    print(f"{Fore.GREEN}{Style.BRIGHT}[+] {message}{Style.RESET_ALL}")


def print_error(message):
    print(f"{Fore.RED}{Style.BRIGHT}[-] {message}{Style.RESET_ALL}")


# -------------------------------------------------------------------
#  MAIN FUNCTION WITH INTERACTIVE MENU
# -------------------------------------------------------------------
def main():
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'=' * 70}")
    print(f"{'COMPREHENSIVE SYSTEM INFORMATION SCANNER':^70}")
    print(f"{'=' * 70}{Style.RESET_ALL}")

    menu_options = [
        ["1", "Device Specifications"],
        ["2", "Storage Details"],
        ["3", "Graphics Card Information"],
        ["4", "Network Connections"],
        ["5", "Detailed Network Properties"],
        ["6", "Data Usage Statistics"],
        ["7", "WiFi Passwords"],
        ["8", "System Credentials"],
        ["9", "Command History"],
        ["10", "Hardware Connection Properties"],
        ["11", "Generate HTML Report (All Data)"],
        ["12", "Exit"]
    ]

    while True:
        print(f"\n{Fore.BLUE}{Style.BRIGHT}MAIN MENU:{Style.RESET_ALL}")
        print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="simple"))

        choice = input(f"\n{Fore.WHITE}Enter your choice (1-12): {Style.RESET_ALL}").strip()

        if choice == '1':
            print_section_header("DEVICE SPECIFICATIONS")
            print_table(get_device_specifications(), tablefmt="simple")

        elif choice == '2':
            print_section_header("STORAGE DETAILS")
            print_table(get_storage_details(), tablefmt="simple")

        elif choice == '3':
            print_section_header("GRAPHICS CARD INFORMATION")
            print_table(get_graphics_card_info(), tablefmt="simple")

        elif choice == '4':
            print_section_header("NETWORK CONNECTIONS")
            print_table(get_network_connections(), tablefmt="simple")

        elif choice == '5':
            print_section_header("DETAILED NETWORK PROPERTIES")
            print_table(get_detailed_network_info(), tablefmt="simple")

        elif choice == '6':
            print_section_header("DATA USAGE STATISTICS")
            print_table(get_data_usage(), tablefmt="simple")

        elif choice == '7':
            print_section_header("WIFI PASSWORDS")
            print_warning("Requires administrator privileges for some networks")
            print_table(get_wifi_passwords(), tablefmt="simple")

        elif choice == '8':
            print_section_header("SYSTEM CREDENTIALS")
            print_table(get_system_credentials(), tablefmt="simple")

        elif choice == '9':
            print_section_header("COMMAND HISTORY")
            print_table(get_command_history(), tablefmt="simple")

        elif choice == '10':
            print_section_header("HARDWARE AND CONNECTION PROPERTIES")
            print_table(get_hardware_connection_properties(), tablefmt="simple")

        elif choice == '11':
            print_section_header("GENERATING HTML REPORT")
            try:
                html_path = generate_html_report()
                print_success(f"HTML report generated successfully!")
                print_success(f"Report saved to: {html_path}")
                print_warning("Open the HTML file in your browser to view the comprehensive report")
            except Exception as e:
                print_error(f"Failed to generate HTML report: {str(e)}")

        elif choice == '12':
            print_success("Thank you for using the System Information Scanner!")
            break

        else:
            print_error("Invalid choice! Please enter a number between 1-12.")

        if choice != '12':
            input(f"\n{Fore.WHITE}Press Enter to continue...{Style.RESET_ALL}")


# -------------------------------------------------------------------
if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)
    # Admin check for Windows
    if platform.system() == "Windows":
        try:
            import ctypes

            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print_warning("Some features may require Administrator privileges!")
                print_warning("Consider running as Administrator for full functionality.\n")
        except:
            pass

    main()