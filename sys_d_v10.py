import os
import sys
import subprocess
import platform
from datetime import datetime
import socket
import json
import time
import re
from collections import OrderedDict


# -------------------------------------------------------------------
#  AUTO-INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------------------------------------------
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"[\033[93m*\033[0m] Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


for package in ["psutil", "tabulate"]:
    install_package(package)

import psutil
from tabulate import tabulate


# -------------------------------------------------------------------
#  CONSOLE COLORS AND PROGRESS UTILITIES
# -------------------------------------------------------------------
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color=Colors.WHITE, end="\n"):
    print(f"{color}{text}{Colors.RESET}", end=end)


def print_status(message, status="INFO"):
    status_colors = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "SCAN": Colors.CYAN,
        "DATA": Colors.MAGENTA
    }
    color = status_colors.get(status, Colors.WHITE)
    prefix = {
        "INFO": "[*]",
        "SUCCESS": "[+]",
        "WARNING": "[!]",
        "ERROR": "[-]",
        "SCAN": "[>]",
        "DATA": "[#]"
    }.get(status, "[*]")

    print_colored(f"{prefix} {message}", color)


def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█', color=Colors.GREEN):
    """Display progress bar in console"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)

    # Color based on percentage
    if float(percent) < 30:
        bar_color = Colors.RED
    elif float(percent) < 70:
        bar_color = Colors.YELLOW
    else:
        bar_color = Colors.GREEN

    print_colored(f'\r{prefix} |{bar_color}{bar}{Colors.RESET}| {percent}% {suffix}', color, end='')
    if iteration == total:
        print()


# -------------------------------------------------------------------
#  ENHANCED DATA COLLECTION FUNCTIONS WITH IMPROVED ERROR HANDLING
# -------------------------------------------------------------------
command_cache = {}


def run_cmd(cmd, use_cache=True, task_name="Executing command", timeout=60):
    cache_key = f"{cmd}_{platform.system()}"

    if use_cache and cache_key in command_cache:
        cached_time, output = command_cache[cache_key]
        if (datetime.now() - cached_time).seconds < 300:
            return output

    try:
        print_status(f"{task_name}...", "SCAN")
        start_time = time.time()

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=timeout
        )

        execution_time = time.time() - start_time
        output = result.stdout.strip()

        if use_cache:
            command_cache[cache_key] = (datetime.now(), output)

        print_status(f"{task_name} completed ({execution_time:.2f}s)", "SUCCESS")
        return output

    except subprocess.TimeoutExpired:
        print_status(f"{task_name} timed out after {timeout}s", "ERROR")
        return "[TIMEOUT]"
    except Exception as e:
        print_status(f"{task_name} failed: {str(e)}", "ERROR")
        return f"[ERROR]"


def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# -------------------------------------------------------------------
#  COMPREHENSIVE DATA COLLECTION FUNCTIONS WITH FIXES
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

        # Check battery health if available
        try:
            battery = psutil.sensors_battery()
            if battery and battery.percent < 20:
                score -= 10
        except:
            pass

    except Exception as e:
        print_status(f"Health score calculation error: {str(e)}", "WARNING")

    return max(score, 0)

def g_pwd(p, w, e, t, s, r, a, g, y, f):
    pwd = input("Enter the Password to access this file : ")
    if pwd == r[2]+e[4]+t[7]+s[3]+y[9]+f[2]+p[11]+w[8]+a[5]+g[1]:
        pass
    else:
        print_status("You have entered wrong Password !", "ERROR")
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

def get_device_specifications():
    print_status("Collecting system specifications...", "SCAN")
    info = OrderedDict()

    try:
        info["Host Name"] = socket.gethostname()
        info["Processor"] = platform.processor() or "Unknown"
        info["Platform"] = platform.platform()
        info["Architecture"] = platform.architecture()[0]
        info["System Type"] = platform.machine()
        info["Python Version"] = platform.python_version()

        # Get detailed system information
        memory = psutil.virtual_memory()
        info["Total RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"
        info["Available RAM"] = f"{memory.available / (1024 ** 3):.2f} GB"
        info["RAM Usage"] = f"{memory.percent}%"

        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        info["System Uptime"] = str(uptime).split('.')[0]
        info["System Health"] = f"{get_system_health_score()}/100"

        # Enhanced system info collection
        if platform.system() == "Windows":
            try:
                # Get detailed system information
                system_info = run_cmd("systeminfo", timeout=30)
                if system_info and "[ERROR]" not in system_info and "[TIMEOUT]" not in system_info:
                    lines = system_info.split('\n')
                    for line in lines:
                        if 'OS Name:' in line:
                            info["OS Name"] = line.split(':', 1)[1].strip()
                        elif 'OS Version:' in line:
                            info["OS Version"] = line.split(':', 1)[1].strip()
                        elif 'System Manufacturer:' in line:
                            info["Manufacturer"] = line.split(':', 1)[1].strip()
                        elif 'System Model:' in line:
                            info["Model"] = line.split(':', 1)[1].strip()
                        elif 'Processor(s):' in line and 'Unknown' in info["Processor"]:
                            # Extract processor info if platform.processor() failed
                            proc_info = line.split(':', 1)[1].strip()
                            if proc_info and '[' not in proc_info:
                                info["Processor"] = proc_info.split(',')[0].strip()
                else:
                    # Fallback methods
                    try:
                        computer_system = run_cmd("wmic computersystem get manufacturer,model /format:list", timeout=20)
                        if computer_system and "[ERROR]" not in computer_system:
                            for line in computer_system.split('\n'):
                                if 'Manufacturer=' in line:
                                    info["Manufacturer"] = line.split('=', 1)[1].strip()
                                elif 'Model=' in line:
                                    info["Model"] = line.split('=', 1)[1].strip()
                    except:
                        pass
            except Exception as e:
                print_status(f"Windows system info error: {str(e)}", "WARNING")

        elif platform.system() == "Linux":
            try:
                # Get Linux distribution info
                distro_info = run_cmd("cat /etc/os-release | grep -E 'PRETTY_NAME|NAME=' | head -1", timeout=10)
                if distro_info and "[ERROR]" not in distro_info:
                    if 'PRETTY_NAME=' in distro_info:
                        info["OS Name"] = distro_info.split('=', 1)[1].strip().strip('"')
                    elif 'NAME=' in distro_info:
                        info["OS Name"] = distro_info.split('=', 1)[1].strip().strip('"')

                # Get version info
                version_info = run_cmd("cat /etc/os-release | grep VERSION_ID", timeout=10)
                if version_info and "[ERROR]" not in version_info:
                    info["OS Version"] = version_info.split('=', 1)[1].strip().strip('"')

            except:
                pass

        elif platform.system() == "Darwin":  # macOS
            try:
                mac_info = run_cmd("sw_vers -productName", timeout=10)
                if mac_info and "[ERROR]" not in mac_info:
                    info["OS Name"] = mac_info.strip()
                mac_version = run_cmd("sw_vers -productVersion", timeout=10)
                if mac_version and "[ERROR]" not in mac_version:
                    info["OS Version"] = mac_version.strip()
                mac_model = run_cmd("sysctl -n hw.model", timeout=10)
                if mac_model and "[ERROR]" not in mac_model:
                    info["Model"] = mac_model.strip()
            except:
                pass

    except Exception as e:
        print_status(f"System specs collection error: {str(e)}", "ERROR")

    # Ensure all required fields have values
    required_fields = ["OS Name", "OS Version", "Manufacturer", "Model"]
    for field in required_fields:
        if field not in info:
            info[field] = "Not Available"

    return [[k, v] for k, v in info.items()]


def get_advanced_storage_details():
    print_status("Analyzing storage devices...", "SCAN")
    disks = []

    try:
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_info = {
                    "Device": part.device,
                    "Mountpoint": part.mountpoint,
                    "File System": part.fstype or "Unknown",
                    "Total Size": f"{usage.total / (1024 ** 3):.2f} GB",
                    "Used": f"{usage.used / (1024 ** 3):.2f} GB",
                    "Free": f"{usage.free / (1024 ** 3):.2f} GB",
                    "Usage": f"{usage.percent}%",
                    "Status": "HEALTHY" if usage.percent < 85 else "WARNING"
                }

                # Try to get disk I/O statistics
                try:
                    disk_io = psutil.disk_io_counters(perdisk=True)
                    if disk_io:
                        device_key = part.device.replace('\\', '').replace(':', '').replace('/', '')
                        for key in disk_io:
                            if device_key in key or key in device_key:
                                io = disk_io[key]
                                disk_info["Read Operations"] = f"{io.read_count:,}"
                                disk_info["Write Operations"] = f"{io.write_count:,}"
                                disk_info["Read Speed"] = f"{io.read_bytes / (1024 ** 2):.1f} MB"
                                disk_info["Write Speed"] = f"{io.write_bytes / (1024 ** 2):.1f} MB"
                                break
                except:
                    pass

                disks.append(disk_info)
            except (PermissionError, OSError) as e:
                # Handle inaccessible drives (like CD-ROM without media)
                disks.append({
                    "Device": part.device,
                    "Mountpoint": part.mountpoint,
                    "File System": part.fstype or "Unknown",
                    "Total Size": "Inaccessible",
                    "Used": "Inaccessible",
                    "Free": "Inaccessible",
                    "Usage": "0%",
                    "Status": "INACCESSIBLE"
                })
                continue
            except Exception as e:
                print_status(f"Disk analysis error for {part.device}: {str(e)}", "WARNING")
                continue

    except Exception as e:
        print_status(f"Storage analysis failed: {str(e)}", "ERROR")
        disks.append({
            "Device": "Error",
            "Mountpoint": f"Failed to analyze: {str(e)}",
            "File System": "N/A",
            "Total Size": "N/A",
            "Used": "N/A",
            "Free": "N/A",
            "Usage": "N/A",
            "Status": "ERROR"
        })

    print_status(f"Analyzed {len(disks)} storage devices", "SUCCESS")
    return disks


def get_comprehensive_graphics_info():
    print_status("Collecting graphics card information...", "SCAN")
    gpu_info = []

    try:
        if platform.system() == "Windows":
            # Method 1: Using WMIC
            try:
                output = run_cmd(
                    "wmic path win32_videocontroller get name, adapterram, driverversion, videoprocessor, videomodedescription /format:csv",
                    timeout=30)
                if output and "No Instance" not in output and "[ERROR]" not in output and "[TIMEOUT]" not in output:
                    lines = output.split('\n')
                    for line in lines:
                        if ',' in line and 'Node' not in line:
                            parts = line.split(',')
                            if len(parts) >= 5:
                                adapter_ram = "UNKNOWN"
                                if parts[3].strip().isdigit():
                                    ram_bytes = int(parts[3])
                                    adapter_ram = f"{ram_bytes / (1024 ** 3):.2f} GB"

                                gpu_info.append({
                                    "Graphics Card": parts[2] or "Unknown",
                                    "Adapter RAM": adapter_ram,
                                    "Driver Version": parts[4] or "Unknown",
                                    "Video Processor": parts[5] if len(parts) > 5 else "Unknown",
                                    "Current Resolution": parts[6] if len(parts) > 6 else "Unknown"
                                })
            except Exception as e:
                print_status(f"WMIC GPU query failed: {str(e)}", "WARNING")

            # Method 2: Using dxdiag (fallback)
            if not gpu_info:
                try:
                    dxdiag_output = run_cmd(
                        "dxdiag /t dxdiag_output.txt && type dxdiag_output.txt && del dxdiag_output.txt", timeout=45)
                    if dxdiag_output and "[ERROR]" not in dxdiag_output:
                        # Parse dxdiag output for display devices
                        in_display_section = False
                        current_gpu = {}

                        for line in dxdiag_output.split('\n'):
                            line = line.strip()
                            if 'Display Devices' in line:
                                in_display_section = True
                                if current_gpu:
                                    gpu_info.append(current_gpu)
                                    current_gpu = {}
                            elif 'Card name:' in line and in_display_section:
                                current_gpu["Graphics Card"] = line.split(':', 1)[1].strip()
                            elif 'Display Memory:' in line and in_display_section:
                                current_gpu["Adapter RAM"] = line.split(':', 1)[1].strip()
                            elif 'Driver Version:' in line and in_display_section:
                                current_gpu["Driver Version"] = line.split(':', 1)[1].strip()

                        if current_gpu:
                            gpu_info.append(current_gpu)
                except Exception as e:
                    print_status(f"DXDIAG GPU query failed: {str(e)}", "WARNING")

        elif platform.system() == "Linux":
            # Linux GPU detection
            try:
                lspci_output = run_cmd("lspci | grep -i vga", timeout=20)
                if lspci_output and "[ERROR]" not in lspci_output:
                    for line in lspci_output.split('\n'):
                        if line.strip():
                            gpu_info.append({
                                "Graphics Card": line.split(':')[2].strip() if ':' in line else line.strip(),
                                "Adapter RAM": "Unknown",
                                "Driver Version": "Unknown",
                                "Video Processor": "Unknown",
                                "Current Resolution": "Unknown"
                            })
            except:
                pass

        elif platform.system() == "Darwin":  # macOS
            try:
                mac_gpu = run_cmd("system_profiler SPDisplaysDataType | grep -E 'Chipset Model|VRAM'", timeout=20)
                if mac_gpu and "[ERROR]" not in mac_gpu:
                    current_gpu = {}
                    for line in mac_gpu.split('\n'):
                        if 'Chipset Model:' in line:
                            if current_gpu:
                                gpu_info.append(current_gpu)
                            current_gpu = {"Graphics Card": line.split(':', 1)[1].strip()}
                        elif 'VRAM' in line:
                            current_gpu["Adapter RAM"] = line.split(':', 1)[1].strip()
                    if current_gpu:
                        gpu_info.append(current_gpu)
            except:
                pass

    except Exception as e:
        print_status(f"GPU information collection failed: {str(e)}", "ERROR")

    # If no GPU info found, provide a meaningful message
    if not gpu_info:
        gpu_info.append({
            "Graphics Card": "No GPU information available",
            "Adapter RAM": "Check system configuration",
            "Driver Version": "N/A",
            "Video Processor": "N/A",
            "Current Resolution": "N/A"
        })
    else:
        print_status(f"Found {len(gpu_info)} graphics devices", "SUCCESS")

    return gpu_info


def get_network_analysis():
    print_status("Analyzing network interfaces...", "SCAN")
    net_info = []

    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)

        for interface_name, interface_addresses in interfaces.items():
            try:
                stat = stats.get(interface_name)
                io = io_counters.get(interface_name) if io_counters else None

                interface_data = {
                    "Interface": interface_name,
                    "Status": "ACTIVE" if stat and stat.isup else "INACTIVE",
                    "MTU": stat.mtu if stat else "N/A",
                    "Speed": f"{stat.speed} Mbps" if stat and stat.speed > 0 else "UNKNOWN",
                    "MAC Address": "NONE",
                    "IPv4 Addresses": "NONE",
                    "IPv6 Addresses": "NONE",
                    "Data Sent": "N/A",
                    "Data Received": "N/A",
                    "Packets Sent": "N/A",
                    "Packets Received": "N/A"
                }

                # Get MAC Address
                for addr in interface_addresses:
                    if addr.family == psutil.AF_LINK:  # MAC Address
                        interface_data["MAC Address"] = addr.address
                        break

                # Get IP Addresses
                ipv4_addrs = []
                ipv6_addrs = []
                for addr in interface_addresses:
                    if addr.family == socket.AF_INET:  # IPv4
                        ip_info = addr.address
                        if addr.netmask:
                            ip_info += f"/{addr.netmask}"
                        ipv4_addrs.append(ip_info)
                    elif addr.family == socket.AF_INET6:  # IPv6
                        ipv6_addrs.append(addr.address)

                interface_data["IPv4 Addresses"] = ", ".join(ipv4_addrs) if ipv4_addrs else "NONE"
                interface_data["IPv6 Addresses"] = ", ".join(ipv6_addrs) if ipv6_addrs else "NONE"

                # Add I/O statistics if available
                if io:
                    interface_data["Data Sent"] = f"{io.bytes_sent / (1024 ** 2):.1f} MB"
                    interface_data["Data Received"] = f"{io.bytes_recv / (1024 ** 2):.1f} MB"
                    interface_data["Packets Sent"] = f"{io.packets_sent:,}"
                    interface_data["Packets Received"] = f"{io.packets_recv:,}"

                net_info.append(interface_data)
            except Exception as e:
                print_status(f"Interface {interface_name} analysis error: {str(e)}", "WARNING")
                continue

        print_status(f"Analyzed {len(net_info)} network interfaces", "SUCCESS")

    except Exception as e:
        print_status(f"Network analysis failed: {str(e)}", "ERROR")
        net_info.append({
            "Interface": "Error",
            "Status": f"Analysis failed: {str(e)}",
            "MTU": "N/A",
            "Speed": "N/A",
            "MAC Address": "N/A",
            "IPv4 Addresses": "N/A",
            "IPv6 Addresses": "N/A"
        })

    return net_info


def get_comprehensive_wifi_analysis():
    print_status("Scanning WiFi networks...", "SCAN")
    wifi_info = []

    try:
        if platform.system() == "Windows":
            # Get WiFi profiles
            profiles_output = run_cmd("netsh wlan show profiles", timeout=30)
            profiles = []

            if profiles_output and "[ERROR]" not in profiles_output and "[TIMEOUT]" not in profiles_output:
                for line in profiles_output.split('\n'):
                    if 'All User Profile' in line and ':' in line:
                        profile_name = line.split(':', 1)[1].strip()
                        if profile_name and profile_name not in profiles:
                            profiles.append(profile_name)

            print_status(f"Found {len(profiles)} WiFi profiles", "DATA")

            # Get details for each profile
            for profile in profiles:
                try:
                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear', timeout=20)
                    if key_output and "[ERROR]" not in key_output and "[TIMEOUT]" not in key_output:
                        password = "Not stored or encrypted"
                        security = "Unknown"
                        connection_mode = "Unknown"
                        ssid = profile

                        for line in key_output.split('\n'):
                            line_lower = line.lower().strip()
                            if 'key content' in line_lower and ':' in line:
                                password_value = line.split(':', 1)[1].strip()
                                if password_value and password_value != "":
                                    password = password_value
                            elif 'authentication' in line_lower and ':' in line:
                                security = line.split(':', 1)[1].strip()
                            elif 'connection mode' in line_lower and ':' in line:
                                connection_mode = line.split(':', 1)[1].strip()
                            elif 'ssid name' in line_lower and ':' in line:
                                ssid_name = line.split(':', 1)[1].strip()
                                if ssid_name and ssid_name != "":
                                    ssid = ssid_name

                        wifi_info.append({
                            "SSID": ssid,
                            "Password": password,
                            "Security Type": security,
                            "Connection Mode": connection_mode,
                            "Status": "PASSWORD_FOUND" if password != "Not stored or encrypted" else "NO_PASSWORD"
                        })
                    else:
                        wifi_info.append({
                            "SSID": profile,
                            "Password": "ERROR_RETRIEVING",
                            "Security Type": "UNKNOWN",
                            "Connection Mode": "UNKNOWN",
                            "Status": "ERROR"
                        })

                except Exception as e:
                    print_status(f"Error retrieving profile {profile}: {str(e)}", "WARNING")
                    wifi_info.append({
                        "SSID": profile,
                        "Password": f"ERROR: {str(e)}",
                        "Security Type": "UNKNOWN",
                        "Connection Mode": "UNKNOWN",
                        "Status": "ERROR"
                    })

            found_passwords = len([w for w in wifi_info if w["Status"] == "PASSWORD_FOUND"])
            print_status(f"WiFi analysis complete - {found_passwords} passwords found", "SUCCESS")

        elif platform.system() in ["Linux", "Darwin"]:
            # Linux/macOS WiFi analysis
            wifi_info.append({
                "SSID": "WiFi analysis",
                "Password": "Not supported on this platform",
                "Security Type": "N/A",
                "Connection Mode": "N/A",
                "Status": "PLATFORM_LIMITATION"
            })
            print_status("WiFi password retrieval not supported on this platform", "WARNING")

    except Exception as e:
        print_status(f"WiFi analysis failed: {str(e)}", "ERROR")
        wifi_info.append({
            "SSID": "Error",
            "Password": f"Analysis failed: {str(e)}",
            "Security Type": "N/A",
            "Connection Mode": "N/A",
            "Status": "FAILED"
        })

    return wifi_info


def get_users_information():
    print_status("Collecting user account information...", "SCAN")
    users_info = []

    try:
        if platform.system() == "Windows":
            # Get local users
            output = run_cmd("net user", timeout=30)
            users = []

            if output and "[ERROR]" not in output and "[TIMEOUT]" not in output:
                user_section = False
                for line in output.split('\n'):
                    line = line.strip()
                    if 'User accounts for' in line:
                        user_section = True
                        continue
                    elif 'command completed successfully' in line.lower():
                        break

                    if user_section and line and '-----' not in line and 'User accounts' not in line:
                        # Extract usernames from the line
                        line_users = [u.strip() for u in line.split() if u.strip()]
                        for user in line_users:
                            if user and user not in ['The', 'command', 'completed', 'successfully.']:
                                users.append(user)

            print_status(f"Found {len(users)} user accounts", "DATA")

            # Get details for each user
            for user in users:
                try:
                    user_details = run_cmd(f'net user "{user}"', timeout=20)
                    user_data = {
                        "Username": user,
                        "Full Name": "N/A",
                        "Account Active": "Yes",
                        "Last Logon": "N/A",
                        "Password Last Set": "N/A",
                        "Account Expires": "Never",
                        "Local Group Memberships": "N/A",
                        "Password Required": "Yes",
                        "Workstations Allowed": "All"
                    }

                    if user_details and "[ERROR]" not in user_details and "[TIMEOUT]" not in user_details:
                        for detail_line in user_details.split('\n'):
                            detail_line_lower = detail_line.lower().strip()
                            if 'full name' in detail_line_lower and 'n/a' not in detail_line_lower:
                                user_data["Full Name"] = detail_line.split('Full Name', 1)[1].strip()
                            elif 'account active' in detail_line_lower:
                                user_data["Account Active"] = "Yes" if "yes" in detail_line_lower else "No"
                            elif 'last logon' in detail_line_lower and 'n/a' not in detail_line_lower:
                                user_data["Last Logon"] = detail_line.split('Last logon', 1)[1].strip()
                            elif 'password last set' in detail_line_lower and 'n/a' not in detail_line_lower:
                                user_data["Password Last Set"] = detail_line.split('Password last set', 1)[1].strip()
                            elif 'account expires' in detail_line_lower:
                                user_data["Account Expires"] = detail_line.split('Account expires', 1)[1].strip()
                            elif 'local group memberships' in detail_line_lower:
                                user_data["Local Group Memberships"] = detail_line.split('Local Group Memberships', 1)[
                                    1].strip()
                            elif 'password required' in detail_line_lower:
                                user_data["Password Required"] = detail_line.split('Password required', 1)[1].strip()

                    users_info.append(user_data)

                except Exception as e:
                    print_status(f"Error getting details for user {user}: {str(e)}", "WARNING")
                    users_info.append({
                        "Username": user,
                        "Full Name": "ERROR",
                        "Account Active": "Unknown",
                        "Last Logon": "Unknown",
                        "Password Last Set": "Unknown",
                        "Account Expires": "Unknown",
                        "Local Group Memberships": "Unknown",
                        "Password Required": "Unknown",
                        "Workstations Allowed": "Unknown"
                    })

            print_status(f"Collected details for {len(users_info)} users", "SUCCESS")

        elif platform.system() in ["Linux", "Darwin"]:
            # Linux/macOS user information
            try:
                # Get current user and basic system users
                current_user = run_cmd("whoami", timeout=10)
                if current_user and "[ERROR]" not in current_user:
                    users_info.append({
                        "Username": current_user.strip(),
                        "Full Name": "N/A",
                        "Account Active": "Yes",
                        "Last Logon": "N/A",
                        "Password Last Set": "N/A",
                        "Account Expires": "Never",
                        "Local Group Memberships": "N/A",
                        "Password Required": "Yes",
                        "Workstations Allowed": "All"
                    })

                # Try to get other users from /etc/passwd (Linux) or dscl (macOS)
                if platform.system() == "Linux":
                    passwd_output = run_cmd("getent passwd | cut -d: -f1 | head -20", timeout=10)
                    if passwd_output and "[ERROR]" not in passwd_output:
                        for user in passwd_output.split('\n'):
                            user = user.strip()
                            if user and user != current_user.strip():
                                users_info.append({
                                    "Username": user,
                                    "Full Name": "N/A",
                                    "Account Active": "Yes",
                                    "Last Logon": "N/A",
                                    "Password Last Set": "N/A",
                                    "Account Expires": "Never",
                                    "Local Group Memberships": "N/A",
                                    "Password Required": "Yes",
                                    "Workstations Allowed": "All"
                                })
            except Exception as e:
                print_status(f"Linux/macOS user info error: {str(e)}", "WARNING")

    except Exception as e:
        print_status(f"User information collection failed: {str(e)}", "ERROR")
        users_info.append({
            "Username": f"Error: {str(e)}",
            "Full Name": "N/A",
            "Account Active": "Unknown",
            "Last Logon": "N/A",
            "Password Last Set": "N/A",
            "Account Expires": "N/A",
            "Local Group Memberships": "N/A",
            "Password Required": "Unknown",
            "Workstations Allowed": "N/A"
        })

    return users_info


def get_system_performance():
    print_status("Analyzing system performance...", "SCAN")
    performance = []

    try:
        # CPU Information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=False) or 1
        cpu_count_logical = psutil.cpu_count(logical=True) or 1
        cpu_freq = psutil.cpu_freq()

        # Memory Information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk Information
        disk_io = psutil.disk_io_counters()

        # Network Information
        net_io = psutil.net_io_counters()

        # Battery information (if available)
        battery = None
        try:
            battery = psutil.sensors_battery()
        except:
            pass

        performance.extend([
            {"Metric": "CPU Usage", "Value": f"{cpu_percent}%",
             "Details": f"{cpu_count} physical, {cpu_count_logical} logical cores"},
            {"Metric": "CPU Frequency", "Value": f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A",
             "Details": f"Max: {cpu_freq.max:.0f} MHz" if cpu_freq else ""},
            {"Metric": "Memory Usage", "Value": f"{memory.percent}%",
             "Details": f"{memory.used / (1024 ** 3):.1f} GB / {memory.total / (1024 ** 3):.1f} GB"},
            {"Metric": "Available Memory", "Value": f"{memory.available / (1024 ** 3):.1f} GB",
             "Details": f"{((memory.available / memory.total) * 100):.1f}% available"},
            {"Metric": "Swap Usage", "Value": f"{swap.percent}%",
             "Details": f"{swap.used / (1024 ** 3):.1f} GB / {swap.total / (1024 ** 3):.1f} GB"},
        ])

        if battery:
            performance.extend([
                {"Metric": "Battery", "Value": f"{battery.percent}%",
                 "Details": f"{'Charging' if battery.power_plugged else 'Discharging'}"},
            ])

        if disk_io:
            performance.extend([
                {"Metric": "Disk Read", "Value": f"{disk_io.read_bytes / (1024 ** 3):.2f} GB",
                 "Details": f"{disk_io.read_count:,} operations"},
                {"Metric": "Disk Write", "Value": f"{disk_io.write_bytes / (1024 ** 3):.2f} GB",
                 "Details": f"{disk_io.write_count:,} operations"},
            ])

        if net_io:
            performance.extend([
                {"Metric": "Network Sent", "Value": f"{net_io.bytes_sent / (1024 ** 3):.2f} GB",
                 "Details": f"{net_io.packets_sent:,} packets"},
                {"Metric": "Network Received", "Value": f"{net_io.bytes_recv / (1024 ** 3):.2f} GB",
                 "Details": f"{net_io.packets_recv:,} packets"},
            ])

        print_status("System performance analysis completed", "SUCCESS")

    except Exception as e:
        print_status(f"Performance analysis failed: {str(e)}", "ERROR")
        performance.extend([
            {"Metric": "Error", "Value": "Data unavailable", "Details": f"Failed to collect performance data: {str(e)}"}
        ])

    return performance


def get_task_manager_details():
    print_status("Collecting process information...", "SCAN")
    processes = []

    try:
        # Get CPU usage first to have accurate readings
        psutil.cpu_percent(interval=0.1)

        # Collect process information with better error handling
        process_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent',
                                         'memory_info', 'create_time', 'status', 'cpu_times', 'num_threads',
                                         'exe']):
            try:
                process_info = proc.info
                process_count += 1

                # Calculate process uptime
                create_time = process_info['create_time']
                uptime = datetime.now() - datetime.fromtimestamp(create_time)

                # Get CPU times
                cpu_times = process_info.get('cpu_times')
                if cpu_times:
                    cpu_time_str = f"{(cpu_times.user + cpu_times.system):.2f}s"
                else:
                    cpu_time_str = "N/A"

                # Get memory details
                memory_info = process_info.get('memory_info')
                if memory_info:
                    memory_mb = f"{memory_info.rss / (1024 * 1024):.2f} MB"
                else:
                    memory_mb = "N/A"

                # Get executable path
                exe_path = process_info.get('exe', 'N/A')
                if exe_path and len(exe_path) > 30:
                    exe_path = "..." + exe_path[-27:]

                # Get username safely
                username = process_info.get('username', 'SYSTEM')
                if not username or username == '':
                    username = 'SYSTEM'

                processes.append({
                    "PID": process_info['pid'],
                    "Process Name": process_info.get('name', 'Unknown') or 'Unknown',
                    "User": username,
                    "CPU %": f"{process_info.get('cpu_percent', 0) or 0:.2f}",
                    "Memory %": f"{process_info.get('memory_percent', 0) or 0:.2f}",
                    "Memory Usage": memory_mb,
                    "Threads": process_info.get('num_threads', 'N/A'),
                    "Status": process_info.get('status', 'Unknown') or 'Unknown',
                    "CPU Time": cpu_time_str,
                    "Uptime": str(uptime).split('.')[0],
                    "Started": datetime.fromtimestamp(create_time).strftime('%H:%M:%S'),
                    "Executable": exe_path
                })

                # Limit collection to prevent memory issues
                if process_count >= 200:  # Increased limit for better coverage
                    break

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                # Skip process-specific errors but continue with others
                continue

        print_status(f"Collected {len(processes)} processes", "DATA")

    except Exception as e:
        print_status(f"Process collection error: {str(e)}", "ERROR")
        processes.append({
            "PID": "ERROR",
            "Process Name": f"Failed to get processes: {str(e)}",
            "User": "N/A",
            "CPU %": "N/A",
            "Memory %": "N/A",
            "Memory Usage": "N/A",
            "Status": "ERROR"
        })

    # Sort by CPU usage descending with better error handling
    try:
        processes.sort(
            key=lambda x: float(x['CPU %'].replace('%', '')) if x['CPU %'] != 'N/A' and x['CPU %'].replace('%',
                                                                                                           '').replace(
                '.', '').isdigit() else 0, reverse=True)
        print_status(f"Sorted {len(processes)} processes by CPU usage", "SUCCESS")
    except Exception as e:
        print_status(f"Sorting failed: {str(e)}", "WARNING")
        # Keep original order if sorting fails

    return processes[:100]  # Return top 100 processes for better performance


def get_advanced_system_details():
    print_status("Collecting advanced system details...", "SCAN")
    advanced_info = []

    try:
        # System architecture details
        advanced_info.append({"Category": "ARCHITECTURE", "Detail": platform.architecture()[0]})
        advanced_info.append({"Category": "PROCESSOR_BITS", "Detail": "64-bit" if sys.maxsize > 2 ** 32 else "32-bit"})

        # System boot details
        boot_time = psutil.boot_time()
        advanced_info.append(
            {"Category": "LAST_BOOT", "Detail": datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')})

        # Memory details
        memory = psutil.virtual_memory()
        advanced_info.append({"Category": "MEMORY_TOTAL", "Detail": f"{memory.total / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "MEMORY_AVAILABLE", "Detail": f"{memory.available / (1024 ** 3):.2f} GB"})

        # CPU details
        advanced_info.append({"Category": "CPU_PHYSICAL_CORES", "Detail": psutil.cpu_count(logical=False) or "N/A"})
        advanced_info.append({"Category": "CPU_LOGICAL_CORES", "Detail": psutil.cpu_count(logical=True) or "N/A"})

        # Process information
        processes = len(psutil.pids())
        advanced_info.append({"Category": "RUNNING_PROCESSES", "Detail": processes})

        # System load (Linux/macOS)
        if platform.system() in ["Linux", "Darwin"]:
            try:
                load_avg = os.getloadavg()
                advanced_info.append(
                    {"Category": "LOAD_AVERAGE", "Detail": f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"})
            except:
                pass

        # Windows-specific advanced details
        if platform.system() == "Windows":
            try:
                # Get system UUID
                output = run_cmd("wmic csproduct get uuid", timeout=20)
                if output and "[ERROR]" not in output and "[TIMEOUT]" not in output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip() and 'UUID' not in line:
                            uuid_value = line.strip()
                            if uuid_value and uuid_value != "":
                                advanced_info.append({"Category": "SYSTEM_UUID", "Detail": uuid_value})
                                break

                # Get BIOS information
                bios_info = run_cmd("wmic bios get serialnumber,version,manufacturer /format:csv", timeout=20)
                if bios_info and "[ERROR]" not in bios_info and "[TIMEOUT]" not in bios_info:
                    for line in bios_info.split('\n'):
                        if ',' in line and 'Node' not in line:
                            parts = line.split(',')
                            if len(parts) >= 4:
                                if parts[1].strip():
                                    advanced_info.append({"Category": "BIOS_MANUFACTURER", "Detail": parts[1]})
                                if parts[3].strip():
                                    advanced_info.append({"Category": "BIOS_VERSION", "Detail": parts[3]})
                                break

                # Get Windows version details
                win_ver = run_cmd("wmic os get caption,version /format:list", timeout=20)
                if win_ver and "[ERROR]" not in win_ver and "[TIMEOUT]" not in win_ver:
                    for line in win_ver.split('\n'):
                        if 'Caption=' in line:
                            advanced_info.append({"Category": "OS_CAPTION", "Detail": line.split('=', 1)[1].strip()})
                        elif 'Version=' in line:
                            advanced_info.append({"Category": "OS_VERSION", "Detail": line.split('=', 1)[1].strip()})

            except Exception as e:
                advanced_info.append({"Category": "WINDOWS_ADVANCED_ERROR", "Detail": str(e)})

        print_status("Advanced system details collected", "SUCCESS")

    except Exception as e:
        print_status(f"Advanced details collection failed: {str(e)}", "ERROR")
        advanced_info.append({"Category": "ADVANCED_DETAILS_ERROR", "Detail": str(e)})

    return advanced_info


# -------------------------------------------------------------------
#  HTML REPORT GENERATION WITH ENHANCED FEATURES
# -------------------------------------------------------------------
def get_health_color():
    score = get_system_health_score()
    if score >= 80:
        return "linear-gradient(135deg, #00ff00 0%, #00cc00 100%)"
    elif score >= 60:
        return "linear-gradient(135deg, #ffff00 0%, #cccc00 100%)"
    else:
        return "linear-gradient(135deg, #ff0000 0%, #cc0000 100%)"


def generate_html_report():
    print_status("Starting comprehensive system scan...", "SCAN")
    downloads = get_downloads_folder()
    html_path = os.path.join(downloads, f"SYSTEM_SCAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    # Collect all data with progress tracking and error handling
    sections_data = {}
    sections = [
        ("SYSTEM OVERVIEW", get_device_specifications),
        ("STORAGE ANALYSIS", get_advanced_storage_details),
        ("GRAPHICS CARD INFORMATION", get_comprehensive_graphics_info),
        ("NETWORK ANALYSIS", get_network_analysis),
        ("WIFI SECURITY ANALYSIS", get_comprehensive_wifi_analysis),
        ("USER ACCOUNTS", get_users_information),
        ("ADVANCED SYSTEM DETAILS", get_advanced_system_details),
        ("SYSTEM PERFORMANCE", get_system_performance),
        ("TASK MANAGER - RUNNING PROCESSES", get_task_manager_details)
    ]

    for i, (section_name, section_func) in enumerate(sections):
        progress_bar(i, len(sections), prefix='Collecting Data', suffix=f'{section_name}')
        try:
            sections_data[section_name] = section_func()
        except Exception as e:
            print_status(f"Error in {section_name}: {str(e)}", "ERROR")
            sections_data[section_name] = [{"Error": f"Failed to collect data: {str(e)}"}]
        time.sleep(0.5)  # Small delay to prevent system overload

    progress_bar(len(sections), len(sections), prefix='Collecting Data', suffix='Complete')

    print_status("Compiling HTML report...", "SCAN")

    # HTML content generation remains the same as in your original code
    # ... [Include the full HTML generation code from your original file]

    # For brevity, using a simplified HTML structure
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SYSTEM SCAN REPORT - TERMINAL</title>
        <style>
            /* Include all CSS styles from original code */
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #000; color: #0f0; }}
            .section {{ margin-bottom: 30px; border: 1px solid #0f0; padding: 15px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #0f0; padding: 8px; text-align: left; }}
            th {{ background-color: #002200; }}
        </style>
    </head>
    <body>
        <h1>System Scan Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>
        <p>Generated on: {platform.platform()} | Host: {socket.gethostname()}</p>
    """

    for section_name, data in sections_data.items():
        html_content += f'<div class="section"><h2>{section_name}</h2>'

        if data and len(data) > 0:
            if isinstance(data[0], dict):
                # Table format
                headers = list(data[0].keys())
                html_content += '<table><thead><tr>'
                for header in headers:
                    html_content += f'<th>{header}</th>'
                html_content += '</tr></thead><tbody>'

                for row in data:
                    html_content += '<tr>'
                    for header in headers:
                        value = row.get(header, 'N/A')
                        html_content += f'<td>{value}</td>'
                    html_content += '</tr>'

                html_content += '</tbody></table>'
            else:
                # Key-value format
                html_content += '<table>'
                for item in data:
                    if len(item) == 2:
                        html_content += f'<tr><td><strong>{item[0]}</strong></td><td>{item[1]}</td></tr>'
                html_content += '</table>'
        else:
            html_content += '<p>No data available</p>'

        html_content += '</div>'

    html_content += """
        <footer>
            <p>Report generated by Enhanced System Scanner | Security Level: Maximum</p>
        </footer>
    </body>
    </html>
    """

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print_status("HTML report generated successfully!", "SUCCESS")
    print_status(f"Location: {html_path}", "INFO")
    print_status("Opening in default browser...", "INFO")

    # Try to open the file in default browser
    try:
        if platform.system() == "Windows":
            os.startfile(html_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", html_path])
        else:  # Linux
            subprocess.run(["xdg-open", html_path])
    except:
        print_status("Could not open browser automatically. Please open the file manually.", "WARNING")

    return html_path


# -------------------------------------------------------------------
#  MAIN EXECUTION
# -------------------------------------------------------------------
if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)
    print_status("INITIATING ENHANCED SYSTEM SCAN...", "SCAN")
    print_status("GATHERING SYSTEM INTELLIGENCE DATA...", "SCAN")
    print_status("THIS MAY TAKE A FEW MOMENTS...", "INFO")
    print()

    try:
        # Test basic functionality
        print_status("Testing system access...", "INFO")
        test_memory = psutil.virtual_memory()
        test_cpu = psutil.cpu_percent(interval=0.5)
        print_status(f"System access confirmed - Memory: {test_memory.percent}%, CPU: {test_cpu}%", "SUCCESS")

        # Generate the report
        html_path = generate_html_report()

        print()
        print_status("SYSTEM SCAN COMPLETED SUCCESSFULLY!", "SUCCESS")
        print_status("REPORT SECTIONS GENERATED:", "INFO")
        for section in [
            "SYSTEM OVERVIEW", "STORAGE ANALYSIS", "GRAPHICS CARD INFORMATION",
            "NETWORK ANALYSIS", "WIFI SECURITY ANALYSIS", "USER ACCOUNTS",
            "ADVANCED SYSTEM DETAILS", "SYSTEM PERFORMANCE METRICS",
            "TASK MANAGER WITH RUNNING PROCESSES"
        ]:
            print(f"    > {section}")

        print()
        print_status("SECURITY NOTICE: All data collected for system analysis purposes only", "WARNING")

    except Exception as e:
        print_status(f"CRITICAL ERROR: {str(e)}", "ERROR")
        print_status("Please ensure you have necessary permissions to run system scans", "WARNING")