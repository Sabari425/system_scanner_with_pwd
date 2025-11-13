import os
import sys
import subprocess
import platform
from datetime import datetime
import socket
import json
import time
from collections import OrderedDict


# -------------------------------------------------------------------
#  AUTO-INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------------------------------------------
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


for package in ["psutil", "tabulate", "colorama"]:
    install_package(package)

import psutil
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


# -------------------------------------------------------------------
#  GLOBAL CONFIGURATION
# -------------------------------------------------------------------
class Config:
    SCAN_DEPTH = "COMPREHENSIVE"
    ENABLE_REAL_TIME_MONITORING = True
    MAX_LOG_ENTRIES = 1000
    SECURITY_LEVEL = "HIGH"
    REPORT_FORMATS = ["HTML", "JSON", "TXT"]


# -------------------------------------------------------------------
#  ADVANCED SYSTEM MONITORING
# -------------------------------------------------------------------
class SystemMonitor:
    def __init__(self):
        self.performance_log = []
        self.security_events = []
        self.start_time = datetime.now()

    def log_performance(self, metric, value):
        entry = {
            "timestamp": datetime.now(),
            "metric": metric,
            "value": value
        }
        self.performance_log.append(entry)
        if len(self.performance_log) > Config.MAX_LOG_ENTRIES:
            self.performance_log.pop(0)

    def log_security_event(self, event_type, description):
        event = {
            "timestamp": datetime.now(),
            "type": event_type,
            "description": description,
            "severity": "MEDIUM"
        }
        self.security_events.append(event)


monitor = SystemMonitor()


# -------------------------------------------------------------------
#  DETERMINE DOWNLOADS PATH
# -------------------------------------------------------------------
def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# -------------------------------------------------------------------
#  ENHANCED COMMAND EXECUTOR WITH ENCODING FIX
# -------------------------------------------------------------------
command_cache = {}
CACHE_DURATION = 300  # 5 minutes


def run_cmd(cmd, use_cache=True):
    cache_key = f"{cmd}_{platform.system()}"

    if use_cache and cache_key in command_cache:
        cached_time, output = command_cache[cache_key]
        if (datetime.now() - cached_time).seconds < CACHE_DURATION:
            return output

    try:
        # Handle encoding issues by using UTF-8 and ignoring errors
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )

        execution_time = 0
        output = result.stdout.strip()

        if use_cache:
            command_cache[cache_key] = (datetime.now(), output)

        return output

    except subprocess.TimeoutExpired:
        monitor.log_security_event("COMMAND_TIMEOUT", f"Command timed out: {cmd}")
        return "Command execution timeout"
    except UnicodeDecodeError as e:
        monitor.log_security_event("ENCODING_ERROR", f"Unicode decode error: {str(e)}")
        return "Encoding error - cannot decode command output"
    except Exception as e:
        return f"Command failed: {str(e)}"

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

# -------------------------------------------------------------------
#  USERS AND ACCOUNTS INFORMATION
# -------------------------------------------------------------------
def get_users_information():
    users_info = []

    if platform.system() == "Windows":
        try:
            # Get local users
            output = run_cmd("net user")
            if "User accounts for" not in output:
                return [{"Username": "Error retrieving users", "Details": "Command failed"}]

            lines = output.split('\n')
            users = []

            # Parse user accounts
            for line in lines:
                if 'User accounts for' not in line and '-----' not in line and 'command completed' not in line and line.strip():
                    # Extract usernames from the output
                    potential_users = [user.strip() for user in line.split() if user.strip()]
                    for user in potential_users:
                        if user and user not in ['The', 'command', 'completed', 'successfully.']:
                            users.append(user)

            for user in users[:10]:  # Limit to first 10 users for performance
                try:
                    user_details = run_cmd(f'net user "{user}"')
                    user_data = {
                        "Username": user,
                        "Full Name": "N/A",
                        "Account Active": "Yes",
                        "Last Logon": "N/A",
                        "Password Last Set": "N/A",
                        "Account Expires": "Never",
                        "Local Group Memberships": "N/A"
                    }

                    for detail_line in user_details.split('\n'):
                        detail_line_lower = detail_line.lower()
                        if 'full name' in detail_line_lower and 'n/a' not in detail_line_lower:
                            user_data["Full Name"] = detail_line.split('Full Name')[1].strip()
                        elif 'account active' in detail_line_lower:
                            user_data["Account Active"] = "Yes" if "yes" in detail_line_lower else "No"
                        elif 'last logon' in detail_line_lower and 'n/a' not in detail_line_lower:
                            user_data["Last Logon"] = detail_line.split('Last logon')[1].strip()
                        elif 'password last set' in detail_line_lower and 'n/a' not in detail_line_lower:
                            user_data["Password Last Set"] = detail_line.split('Password last set')[1].strip()
                        elif 'account expires' in detail_line_lower:
                            user_data["Account Expires"] = detail_line.split('Account expires')[1].strip()
                        elif 'local group memberships' in detail_line_lower:
                            user_data["Local Group Memberships"] = detail_line.split('Local Group Memberships')[
                                1].strip()

                    users_info.append(user_data)
                except Exception as e:
                    users_info.append({
                        "Username": user,
                        "Full Name": f"Error: {str(e)}",
                        "Account Active": "Unknown",
                        "Last Logon": "N/A",
                        "Password Last Set": "N/A",
                        "Account Expires": "N/A",
                        "Local Group Memberships": "N/A"
                    })
        except Exception as e:
            users_info.append({
                "Username": f"Error: {str(e)}",
                "Full Name": "N/A",
                "Account Active": "N/A",
                "Last Logon": "N/A",
                "Password Last Set": "N/A",
                "Account Expires": "N/A",
                "Local Group Memberships": "N/A"
            })
    else:
        # Linux implementation
        try:
            with open('/etc/passwd', 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if ':/bin/' in line or ':/usr/bin/' in line:
                        parts = line.split(':')
                        if len(parts) >= 7:
                            users_info.append({
                                "Username": parts[0],
                                "User ID": parts[2],
                                "Group ID": parts[3],
                                "Full Name": parts[4],
                                "Home Directory": parts[5],
                                "Shell": parts[6].strip()
                            })
        except:
            users_info.append({
                "Username": "Linux users - requires root access",
                "Details": "Run with sudo for full user list"
            })

    return users_info if users_info else [{"Username": "No user information available", "Details": "N/A"}]


def get_logged_in_users():
    logged_users = []
    try:
        users = psutil.users()
        for user in users:
            logged_users.append({
                "Username": user.name,
                "Terminal": user.terminal or "N/A",
                "Host": user.host or "Local",
                "Started": datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S'),
                "PID": user.pid
            })
    except:
        logged_users.append({"Username": "No logged in users data", "Status": "N/A"})

    return logged_users


# -------------------------------------------------------------------
#  ADVANCED SYSTEM DETAILS
# -------------------------------------------------------------------
def get_advanced_system_details():
    advanced_info = []

    try:
        # System architecture details
        advanced_info.append({"Category": "ARCHITECTURE", "Detail": platform.architecture()[0]})
        advanced_info.append({"Category": "PROCESSOR_BITS", "Detail": "64-bit" if sys.maxsize > 2 ** 32 else "32-bit"})
        advanced_info.append({"Category": "PYTHON_BUILD", "Detail": platform.python_build()[0]})
        advanced_info.append({"Category": "PYTHON_COMPILER", "Detail": platform.python_compiler()})

        # System boot details
        boot_time = psutil.boot_time()
        advanced_info.append(
            {"Category": "LAST_BOOT", "Detail": datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')})

        # Memory details
        memory = psutil.virtual_memory()
        advanced_info.append({"Category": "MEMORY_TOTAL", "Detail": f"{memory.total / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "MEMORY_AVAILABLE", "Detail": f"{memory.available / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "MEMORY_USED", "Detail": f"{memory.used / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "MEMORY_PERCENT", "Detail": f"{memory.percent}%"})

        # CPU details
        advanced_info.append({"Category": "CPU_PHYSICAL_CORES", "Detail": psutil.cpu_count(logical=False)})
        advanced_info.append({"Category": "CPU_LOGICAL_CORES", "Detail": psutil.cpu_count(logical=True)})
        advanced_info.append({"Category": "CPU_USAGE", "Detail": f"{psutil.cpu_percent(interval=1)}%"})

        # Disk details
        disk_io = psutil.disk_io_counters()
        if disk_io:
            advanced_info.append(
                {"Category": "DISK_READ_BYTES", "Detail": f"{disk_io.read_bytes / (1024 ** 3):.2f} GB"})
            advanced_info.append(
                {"Category": "DISK_WRITE_BYTES", "Detail": f"{disk_io.write_bytes / (1024 ** 3):.2f} GB"})
            advanced_info.append({"Category": "DISK_READ_COUNT", "Detail": disk_io.read_count})
            advanced_info.append({"Category": "DISK_WRITE_COUNT", "Detail": disk_io.write_count})

        # Network details
        net_io = psutil.net_io_counters()
        advanced_info.append({"Category": "NET_BYTES_SENT", "Detail": f"{net_io.bytes_sent / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "NET_BYTES_RECV", "Detail": f"{net_io.bytes_recv / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "NET_PACKETS_SENT", "Detail": net_io.packets_sent})
        advanced_info.append({"Category": "NET_PACKETS_RECV", "Detail": net_io.packets_recv})

        # Process information
        processes = len(psutil.pids())
        advanced_info.append({"Category": "RUNNING_PROCESSES", "Detail": processes})

        # Battery information (if available)
        try:
            battery = psutil.sensors_battery()
            if battery:
                advanced_info.append({"Category": "BATTERY_PERCENT", "Detail": f"{battery.percent}%"})
                advanced_info.append({"Category": "POWER_PLUGGED", "Detail": "Yes" if battery.power_plugged else "No"})
        except:
            pass

        # System load (Unix-like systems)
        try:
            load = os.getloadavg()
            advanced_info.append({"Category": "LOAD_1MIN", "Detail": f"{load[0]:.2f}"})
            advanced_info.append({"Category": "LOAD_5MIN", "Detail": f"{load[1]:.2f}"})
            advanced_info.append({"Category": "LOAD_15MIN", "Detail": f"{load[2]:.2f}"})
        except:
            pass

        # Windows-specific advanced details
        if platform.system() == "Windows":
            try:
                # Get system UUID with encoding handling
                output = run_cmd("wmic csproduct get uuid")
                if "UUID" in output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip() and 'UUID' not in line:
                            uuid_value = line.strip()
                            if uuid_value:
                                advanced_info.append({"Category": "SYSTEM_UUID", "Detail": uuid_value})
                                break

                # Get BIOS information with better parsing
                bios_info = run_cmd("wmic bios get serialnumber,version,manufacturer /format:csv")
                for line in bios_info.split('\n'):
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            advanced_info.append({"Category": "BIOS_MANUFACTURER", "Detail": parts[1]})
                            advanced_info.append({"Category": "BIOS_VERSION", "Detail": parts[3]})
                            if len(parts) >= 5:
                                advanced_info.append({"Category": "BIOS_SERIAL", "Detail": parts[4]})
                            break

            except Exception as e:
                advanced_info.append({"Category": "WINDOWS_ADVANCED_ERROR", "Detail": str(e)})

    except Exception as e:
        advanced_info.append({"Category": "ADVANCED_DETAILS_ERROR", "Detail": str(e)})

    return advanced_info


# -------------------------------------------------------------------
#  SYSTEM INFORMATION GATHERING
# -------------------------------------------------------------------
def get_system_health_score():
    score = 100
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 80:
            score -= 20
        elif cpu_usage > 60:
            score -= 10

        memory = psutil.virtual_memory()
        if memory.percent > 85:
            score -= 20
        elif memory.percent > 70:
            score -= 10

        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                if usage.percent > 90:
                    score -= 15
                elif usage.percent > 80:
                    score -= 8
            except:
                continue
    except:
        pass

    return max(score, 0)


def get_device_specifications():
    info = OrderedDict()
    info["Device Name"] = socket.gethostname()
    info["Processor"] = platform.processor()
    info["Platform"] = platform.platform()
    info["Architecture"] = platform.architecture()[0]
    info["System Type"] = platform.machine()
    info["Python Version"] = platform.python_version()

    try:
        memory = psutil.virtual_memory()
        info["Installed RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"
        info["Available RAM"] = f"{memory.available / (1024 ** 3):.2f} GB"
        info["RAM Usage"] = f"{memory.percent}%"

        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        info["System Uptime"] = str(uptime).split('.')[0]
        info["System Health Score"] = f"{get_system_health_score()}/100"
    except:
        info["System Health Score"] = "N/A"

    return [[k, v] for k, v in info.items()]


def get_advanced_storage_details():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "Device": part.device, "Mountpoint": part.mountpoint,
                "File System": part.fstype, "Total Size (GB)": f"{usage.total / (1024 ** 3):.2f}",
                "Used (GB)": f"{usage.used / (1024 ** 3):.2f}", "Free (GB)": f"{usage.free / (1024 ** 3):.2f}",
                "Usage (%)": f"{usage.percent}%", "Status": "Healthy" if usage.percent < 90 else "Warning"
            })
        except:
            continue
    return disks


def get_comprehensive_graphics_info():
    gpu_info = []
    if platform.system() == "Windows":
        try:
            output = run_cmd("wmic path win32_videocontroller get name, adapterram /format:csv")
            if output and "No Instance" not in output:
                lines = output.split('\n')
                for line in lines:
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 3:
                            gpu_info.append({
                                "Graphics Card": parts[2],
                                "Adapter RAM (GB)": f"{int(parts[3]) / (1024 ** 3):.2f}" if parts[
                                    3].strip().isdigit() else "Unknown"
                            })
        except:
            pass
    return gpu_info if gpu_info else [
        {"Graphics Card": "No GPU information available", "Details": "Check system configuration"}]


def get_network_analysis():
    net_info = []
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for interface_name, interface_addresses in interfaces.items():
            if interface_name in stats:
                stat = stats[interface_name]
                interface_data = {
                    "Interface": interface_name, "Status": "ACTIVE" if stat.isup else "INACTIVE",
                    "MTU": stat.mtu, "Speed (Mbps)": f"{stat.speed}" if stat.speed > 0 else "UNKNOWN"
                }
                mac_address = "NONE"
                for addr in interface_addresses:
                    if addr.family == -1:
                        mac_address = addr.address
                        break
                interface_data["MAC Address"] = mac_address
                net_info.append(interface_data)
    except:
        pass
    return net_info


def display_network_analysis_with_scroll():
    net_info = get_network_analysis()
    if not net_info:
        print(f"{Fore.YELLOW}No network interfaces found{Style.RESET_ALL}")
        return
    table_data = []
    for interface in net_info:
        row = [interface.get("Interface", "N/A"), interface.get("Status", "N/A"),
               interface.get("MAC Address", "N/A"), interface.get("MTU", "N/A"),
               interface.get("Speed (Mbps)", "N/A")]
        table_data.append(row)
    headers = ["Interface", "Status", "MAC Address", "MTU", "Speed"]
    print(f"{Fore.CYAN}Network Analysis - Scroll horizontally to view all columns{Style.RESET_ALL}")
    print(tabulate(table_data, headers=headers, tablefmt="simple", numalign="left", stralign="left"))


def get_advanced_network_properties():
    detailed_info = []
    try:
        connectivity_tests = [("Google DNS", "8.8.8.8"), ("Cloudflare DNS", "1.1.1.1")]
        for name, host in connectivity_tests:
            try:
                socket.create_connection((host, 53), timeout=3)
                status = "REACHABLE"
            except:
                status = "UNREACHABLE"
            detailed_info.append({"Property": f"Ping {name}", "Value": status})
        detailed_info.extend([
            {"Property": "Hostname", "Value": socket.gethostname()},
            {"Property": "FQDN", "Value": socket.getfqdn()},
            {"Property": "Host IP", "Value": socket.gethostbyname(socket.gethostname())}
        ])
    except Exception as e:
        detailed_info.append({"Property": "Analysis Error", "Value": f"Network analysis failed: {str(e)}"})
    return detailed_info


def get_real_time_data_usage():
    io_counters = psutil.net_io_counters()
    return [
        {"Metric": "Total Bytes Sent", "Value": f"{io_counters.bytes_sent / (1024 ** 3):.2f} GB"},
        {"Metric": "Total Bytes Received", "Value": f"{io_counters.bytes_recv / (1024 ** 3):.2f} GB"},
        {"Metric": "Total Packets Sent", "Value": f"{io_counters.packets_sent:,}"},
        {"Metric": "Total Packets Received", "Value": f"{io_counters.packets_recv:,}"}
    ]


def get_comprehensive_wifi_analysis():
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

            print(f"{Fore.GREEN}Found {len(profiles)} WiFi profiles{Style.RESET_ALL}")

            for profile in profiles:
                try:
                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear')
                    password = "Not stored or encrypted"
                    for line in key_output.split('\n'):
                        if 'Key Content' in line and ':' in line:
                            password_value = line.split(':')[1].strip()
                            if password_value:
                                password = password_value
                                break
                    wifi_info.append({"SSID": profile, "Password": password})
                except:
                    wifi_info.append({"SSID": profile, "Password": "Error retrieving"})
        except Exception as e:
            wifi_info.append({"SSID": "Error", "Password": f"Failed: {str(e)}"})
    return wifi_info if wifi_info else [{"SSID": "No WiFi profiles found", "Password": "N/A"}]


def get_security_credentials():
    creds_info = []
    if platform.system() == "Windows":
        try:
            output = run_cmd("cmdkey /list")
            if output and "Currently stored credentials" in output:
                for line in output.split('\n'):
                    if 'Target:' in line:
                        target = line.split('Target:')[1].strip()
                        if target and not target.startswith('LegacyGeneric:'):
                            creds_info.append({"Credential Target": target, "Type": "Windows Credential"})
        except:
            pass
    return creds_info if creds_info else [{"Credential Target": "No stored credentials found", "Type": "Info"}]


def get_enhanced_command_history():
    history_info = []
    try:
        history_path = os.path.join(
            os.environ['USERPROFILE'],
            'AppData', 'Roaming', 'Microsoft', 'Windows', 'PowerShell', 'PSReadLine',
            'ConsoleHost_history.txt'
        )
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8', errors='ignore') as f:
                commands = f.readlines()[-10:]
                for i, cmd in enumerate(commands, 1):
                    if cmd.strip():
                        history_info.append({"#": i, "Command": cmd.strip()})
    except:
        pass
    return history_info if history_info else [{"#": 1, "Command": "No command history available"}]


def get_hardware_connection_analysis():
    hardware_info = []
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for interface_name in interfaces:
            if interface_name in stats:
                stat = stats[interface_name]
                hardware_info.append({
                    "Interface Name": interface_name,
                    "Status": "Connected" if stat.isup else "Disconnected",
                    "MTU": stat.mtu,
                    "Speed": f"{stat.speed} Mbps" if stat.speed > 0 else "Unknown"
                })
    except:
        pass
    return hardware_info if hardware_info else [{"Interface Name": "No interfaces", "Status": "N/A"}]


# -------------------------------------------------------------------
#  MULTI-FORMAT REPORT GENERATION
# -------------------------------------------------------------------
def generate_comprehensive_reports():
    downloads = get_downloads_folder()
    reports_generated = []

    try:
        html_path = generate_html_report()
        reports_generated.append(("HTML", html_path))
    except Exception as e:
        print(f"{Fore.RED}HTML report failed: {e}{Style.RESET_ALL}")

    try:
        json_path = generate_json_report()
        reports_generated.append(("JSON", json_path))
    except Exception as e:
        print(f"{Fore.RED}JSON report failed: {e}{Style.RESET_ALL}")

    try:
        txt_path = generate_text_report()
        reports_generated.append(("TXT", txt_path))
    except Exception as e:
        print(f"{Fore.RED}TXT report failed: {e}{Style.RESET_ALL}")

    return reports_generated


def generate_json_report():
    downloads = get_downloads_folder()
    json_path = os.path.join(downloads, f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    report_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "device_name": socket.gethostname(),
            "platform": platform.platform(),
            "scanner_version": "3.1"
        },
        "sections": {
            "device_specifications": get_device_specifications(),
            "storage_details": get_advanced_storage_details(),
            "users_information": get_users_information(),
            "logged_in_users": get_logged_in_users(),
            "advanced_system_details": get_advanced_system_details(),
            "network_analysis": get_network_analysis(),
            "wifi_analysis": get_comprehensive_wifi_analysis()
        }
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, default=str)
    return json_path


def generate_text_report():
    downloads = get_downloads_folder()
    txt_path = os.path.join(downloads, f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"COMPREHENSIVE SYSTEM REPORT\n{'=' * 50}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Device: {socket.gethostname()}\n\n")

        sections = [
            ("DEVICE SPECIFICATIONS", get_device_specifications()),
            ("USERS INFORMATION", get_users_information()),
            ("LOGGED IN USERS", get_logged_in_users()),
            ("ADVANCED SYSTEM DETAILS", get_advanced_system_details()),
            ("NETWORK ANALYSIS", get_network_analysis()),
            ("WIFI ANALYSIS", get_comprehensive_wifi_analysis())
        ]

        for section_name, data in sections:
            f.write(f"\n{section_name}\n{'-' * len(section_name)}\n")
            if data:
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    f.write(tabulate(data, headers=headers, tablefmt="simple"))
                else:
                    for item in data:
                        if len(item) == 2:
                            f.write(f"{item[0]}: {item[1]}\n")
            f.write("\n")
    return txt_path


def generate_html_report():
    downloads = get_downloads_folder()
    html_path = os.path.join(downloads, f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    sections_data = {
        "Device Specifications": get_device_specifications(),
        "Storage Details": get_advanced_storage_details(),
        "Graphics Card Information": get_comprehensive_graphics_info(),
        "Network Analysis": get_network_analysis(),
        "Detailed Network Properties": get_advanced_network_properties(),
        "Data Usage Statistics": get_real_time_data_usage(),
        "WiFi Security Analysis": get_comprehensive_wifi_analysis(),
        "System Credentials": get_security_credentials(),
        "Command History Analysis": get_enhanced_command_history(),
        "Hardware Connection Properties": get_hardware_connection_analysis(),
        "Users Information": get_users_information(),
        "Currently Logged In Users": get_logged_in_users(),
        "Advanced System Details": get_advanced_system_details()
    }

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced System Comprehensive Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                background: #0a0a0a;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                color: #00ff00;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}

            .header {{
                background: #001a00;
                padding: 25px;
                border-radius: 10px;
                margin-bottom: 25px;
                text-align: center;
                border: 1px solid #004400;
            }}

            .header h1 {{
                color: #00cc00;
                font-size: 2.2em;
                margin-bottom: 8px;
                font-weight: bold;
            }}

            .header p {{
                color: #00aa00;
                font-size: 1em;
            }}

            .section {{
                background: #001a00;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border: 1px solid #004400;
            }}

            .section:hover {{
                background: #002200;
            }}

            .section h2 {{
                color: #00cc00;
                border-bottom: 1px solid #004400;
                padding-bottom: 8px;
                margin-bottom: 15px;
                font-size: 1.2em;
                font-weight: bold;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
            }}

            th {{
                background: #003300;
                color: #00ff00;
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
                border: 1px solid #004400;
            }}

            td {{
                padding: 10px 12px;
                border: 1px solid #004400;
                color: #00cc00;
            }}

            tr:nth-child(even) {{
                background: #001a00;
            }}

            tr:hover {{
                background: #002200;
            }}

            .status-connected {{
                color: #00ff00;
                font-weight: bold;
            }}

            .status-disconnected {{
                color: #ff4444;
                font-weight: bold;
            }}

            .metric-value {{
                font-family: 'Courier New', monospace;
                background: #002200;
                padding: 2px 6px;
                border-radius: 3px;
                color: #00ff00;
            }}

            .footer {{
                text-align: center;
                color: #00aa00;
                margin-top: 30px;
                padding: 15px;
                font-size: 0.9em;
            }}

            .network-scroll-container {{
                overflow-x: auto;
                margin: 15px 0;
                border: 1px solid #004400;
                border-radius: 6px;
                padding: 8px;
            }}

            .network-table {{
                min-width: 1000px;
            }}

            .advanced-details {{
                background: #001100;
                border: 1px solid #005500;
            }}

            .user-section {{
                background: #001500;
                border: 1px solid #003300;
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 8px;
                }}

                .header h1 {{
                    font-size: 1.8em;
                }}

                table {{
                    font-size: 0.8em;
                }}

                th, td {{
                    padding: 6px 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SYSTEM COMPREHENSIVE REPORT</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
                <p>Device: {socket.gethostname()} | Platform: {platform.platform()} | Health Score: {get_system_health_score()}/100</p>
            </div>
    """

    for section_name, data in sections_data.items():
        section_class = ""
        if "Advanced" in section_name:
            section_class = "advanced-details"
        elif "User" in section_name:
            section_class = "user-section"

        html_content += f"""
            <div class="section {section_class}">
                <h2>{section_name}</h2>
        """

        if data:
            if section_name == "Network Analysis":
                html_content += '<div class="network-scroll-container">'
                html_content += '<table class="network-table">'
            else:
                html_content += '<table>'

            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                rows = [[row.get(header, '') for header in headers] for row in data]

                html_content += '<thead><tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr></thead>'
                html_content += '<tbody>'
                for row in rows:
                    html_content += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
                html_content += '</tbody></table>'
            else:
                for item in data:
                    if len(item) == 2:
                        html_content += f'<tr><td><strong>{item[0]}</strong></td><td>{item[1]}</td></tr>'
                html_content += '</table>'

            if section_name == "Network Analysis":
                html_content += '</div>'
        else:
            html_content += '<p>No data available for this section.</p>'

        html_content += '</div>'

    html_content += """
            <div class="footer">
                <p>Report generated by Advanced System Information Scanner v3.1 | Deep System Analysis</p>
            </div>
        </div>
    </body>
    </html>
    """

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_path


# -------------------------------------------------------------------
#  DISPLAY FUNCTIONS
# -------------------------------------------------------------------
def print_section_header(title):
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{'=' * 80}")
    print(f"{title:^80}")
    print(f"{'=' * 80}{Style.RESET_ALL}")


def print_table(data, headers="keys", tablefmt="simple"):
    if data:
        print(tabulate(data, headers=headers, tablefmt=tablefmt, numalign="left", stralign="left"))
    else:
        print(f"{Fore.YELLOW}No data available{Style.RESET_ALL}")


def print_warning(message):
    print(f"{Fore.YELLOW}{Style.BRIGHT}[WARNING] {message}{Style.RESET_ALL}")


def print_success(message):
    print(f"{Fore.GREEN}{Style.BRIGHT}[SUCCESS] {message}{Style.RESET_ALL}")


def print_error(message):
    print(f"{Fore.RED}{Style.BRIGHT}[ERROR] {message}{Style.RESET_ALL}")


# -------------------------------------------------------------------
#  MAIN FUNCTION WITH INTERACTIVE MENU
# -------------------------------------------------------------------
def main():
    print(f"{Fore.GREEN}{Style.BRIGHT}{'=' * 80}")
    print(f"{'COMPREHENSIVE SYSTEM INFORMATION SCANNER':^80}")
    print(f"{'=' * 80}{Style.RESET_ALL}")

    menu_options = [
        ["1", "Device Specifications"],
        ["2", "Storage Details"],
        ["3", "Graphics Card Information"],
        ["4", "Network Analysis (Scrollable)"],
        ["5", "Detailed Network Properties"],
        ["6", "Data Usage Statistics"],
        ["7", "WiFi Passwords (ALL NETWORKS)"],
        ["8", "System Credentials"],
        ["9", "Command History"],
        ["10", "Hardware Connection Properties"],
        ["11", "Users Information"],
        ["12", "Currently Logged In Users"],
        ["13", "Advanced System Details"],
        ["14", "Generate HTML Report (All Data)"],
        ["15", "Generate All Reports (HTML, JSON, TXT)"],
        ["16", "Exit"]
    ]

    while True:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}MAIN MENU:{Style.RESET_ALL}")
        print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="simple"))

        choice = input(f"\n{Fore.WHITE}Enter your choice (1-16): {Style.RESET_ALL}").strip()

        if choice == '1':
            print_section_header("DEVICE SPECIFICATIONS")
            print_table(get_device_specifications(), tablefmt="simple")
        elif choice == '2':
            print_section_header("STORAGE DETAILS")
            print_table(get_advanced_storage_details(), tablefmt="simple")
        elif choice == '3':
            print_section_header("GRAPHICS CARD INFORMATION")
            print_table(get_comprehensive_graphics_info(), tablefmt="simple")
        elif choice == '4':
            print_section_header("NETWORK ANALYSIS - SCROLLABLE")
            display_network_analysis_with_scroll()
        elif choice == '5':
            print_section_header("DETAILED NETWORK PROPERTIES")
            print_table(get_advanced_network_properties(), tablefmt="simple")
        elif choice == '6':
            print_section_header("DATA USAGE STATISTICS")
            print_table(get_real_time_data_usage(), tablefmt="simple")
        elif choice == '7':
            print_section_header("WIFI PASSWORDS - ALL NETWORKS")
            print_table(get_comprehensive_wifi_analysis(), tablefmt="simple")
        elif choice == '8':
            print_section_header("SYSTEM CREDENTIALS")
            print_table(get_security_credentials(), tablefmt="simple")
        elif choice == '9':
            print_section_header("COMMAND HISTORY")
            print_table(get_enhanced_command_history(), tablefmt="simple")
        elif choice == '10':
            print_section_header("HARDWARE AND CONNECTION PROPERTIES")
            print_table(get_hardware_connection_analysis(), tablefmt="simple")
        elif choice == '11':
            print_section_header("USERS INFORMATION")
            print_table(get_users_information(), tablefmt="simple")
        elif choice == '12':
            print_section_header("CURRENTLY LOGGED IN USERS")
            print_table(get_logged_in_users(), tablefmt="simple")
        elif choice == '13':
            print_section_header("ADVANCED SYSTEM DETAILS")
            print_table(get_advanced_system_details(), tablefmt="simple")
        elif choice == '14':
            print_section_header("GENERATING HTML REPORT")
            try:
                html_path = generate_html_report()
                print_success(f"HTML report generated successfully!")
                print_success(f"Report saved to: {html_path}")
            except Exception as e:
                print_error(f"Failed to generate HTML report: {str(e)}")
        elif choice == '15':
            print_section_header("GENERATING ALL REPORTS")
            try:
                reports = generate_comprehensive_reports()
                print_success("All reports generated successfully!")
                for report_type, report_path in reports:
                    print_success(f"{report_type} report: {report_path}")
            except Exception as e:
                print_error(f"Failed to generate reports: {str(e)}")
        elif choice == '16':
            print_success("Thank you for using the System Information Scanner!")
            break
        else:
            print_error("Invalid choice! Please enter a number between 1-16.")

        if choice != '16':
            input(f"\n{Fore.WHITE}Press Enter to continue...{Style.RESET_ALL}")


# -------------------------------------------------------------------
if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)
    if platform.system() == "Windows":
        try:
            import ctypes

            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print_warning("Some features may require Administrator privileges!")
        except:
            pass

    main()