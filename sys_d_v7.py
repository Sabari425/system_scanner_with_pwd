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


for package in ["psutil", "tabulate"]:
    install_package(package)

import psutil
from tabulate import tabulate

# -------------------------------------------------------------------
#  ENHANCED COMMAND EXECUTOR WITH ENCODING FIX
# -------------------------------------------------------------------
command_cache = {}


def run_cmd(cmd, use_cache=True):
    cache_key = f"{cmd}_{platform.system()}"

    if use_cache and cache_key in command_cache:
        cached_time, output = command_cache[cache_key]
        if (datetime.now() - cached_time).seconds < 300:  # 5 minutes cache
            return output

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=45
        )

        output = result.stdout.strip()

        if use_cache:
            command_cache[cache_key] = (datetime.now(), output)

        return output

    except subprocess.TimeoutExpired:
        return "Command execution timeout"
    except Exception as e:
        return f"Command failed: {str(e)}"


# -------------------------------------------------------------------
#  DETERMINE DOWNLOADS PATH
# -------------------------------------------------------------------
def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# -------------------------------------------------------------------
#  TASK MANAGER - COMPREHENSIVE PROCESS INFORMATION
# -------------------------------------------------------------------
def get_task_manager_details():
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent',
                                         'memory_info', 'create_time', 'status', 'cpu_times', 'num_threads']):
            try:
                process_info = proc.info

                # Calculate process uptime
                create_time = process_info['create_time']
                uptime = datetime.now() - datetime.fromtimestamp(create_time)

                # Get CPU times
                cpu_times = process_info.get('cpu_times')
                if cpu_times:
                    cpu_time_str = f"{cpu_times.user + cpu_times.system:.2f}s"
                else:
                    cpu_time_str = "N/A"

                # Get memory details
                memory_info = process_info.get('memory_info')
                if memory_info:
                    memory_mb = f"{memory_info.rss / (1024 * 1024):.2f} MB"
                else:
                    memory_mb = "N/A"

                processes.append({
                    "PID": process_info['pid'],
                    "Name": process_info['name'],
                    "User": process_info['username'] or "SYSTEM",
                    "CPU %": f"{process_info['cpu_percent'] or 0:.2f}",
                    "Memory %": f"{process_info['memory_percent'] or 0:.2f}",
                    "Memory Usage": memory_mb,
                    "Threads": process_info.get('num_threads', 'N/A'),
                    "Status": process_info['status'],
                    "CPU Time": cpu_time_str,
                    "Uptime": str(uptime).split('.')[0],
                    "Started": datetime.fromtimestamp(create_time).strftime('%H:%M:%S')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    except Exception as e:
        processes.append({
            "PID": "Error",
            "Name": f"Failed to get processes: {str(e)}",
            "User": "N/A",
            "CPU %": "N/A",
            "Memory %": "N/A",
            "Memory Usage": "N/A",
            "Status": "ERROR"
        })

    # Sort by CPU usage descending
    try:
        processes.sort(key=lambda x: float(x['CPU %'].replace('%', '')) if x['CPU %'] != 'N/A' else 0, reverse=True)
    except:
        pass

    return processes[:100]  # Return top 100 processes by CPU usage


def get_system_performance():
    performance = []

    # CPU Information
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=False)
    cpu_count_logical = psutil.cpu_count(logical=True)

    # Memory Information
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disk Information
    disk_io = psutil.disk_io_counters()
    disk_usage = {}
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_usage[part.device] = {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except:
            continue

    # Network Information
    net_io = psutil.net_io_counters()

    performance.extend([
        {"Metric": "CPU Usage", "Value": f"{cpu_percent}%",
         "Details": f"{cpu_count} physical, {cpu_count_logical} logical cores"},
        {"Metric": "Memory Usage", "Value": f"{memory.percent}%",
         "Details": f"{memory.used / (1024 ** 3):.1f} GB / {memory.total / (1024 ** 3):.1f} GB"},
        {"Metric": "Available Memory", "Value": f"{memory.available / (1024 ** 3):.1f} GB",
         "Details": f"{((memory.available / memory.total) * 100):.1f}% available"},
        {"Metric": "Swap Usage", "Value": f"{swap.percent}%",
         "Details": f"{swap.used / (1024 ** 3):.1f} GB / {swap.total / (1024 ** 3):.1f} GB"},
    ])

    if disk_io:
        performance.extend([
            {"Metric": "Disk Read", "Value": f"{disk_io.read_bytes / (1024 ** 3):.2f} GB",
             "Details": f"{disk_io.read_count} operations"},
            {"Metric": "Disk Write", "Value": f"{disk_io.write_bytes / (1024 ** 3):.2f} GB",
             "Details": f"{disk_io.write_count} operations"},
        ])

    if net_io:
        performance.extend([
            {"Metric": "Network Sent", "Value": f"{net_io.bytes_sent / (1024 ** 3):.2f} GB",
             "Details": f"{net_io.packets_sent} packets"},
            {"Metric": "Network Received", "Value": f"{net_io.bytes_recv / (1024 ** 3):.2f} GB",
             "Details": f"{net_io.packets_recv} packets"},
        ])

    return performance


# -------------------------------------------------------------------
#  USERS AND ACCOUNTS INFORMATION
# -------------------------------------------------------------------
def get_users_information():
    users_info = []

    if platform.system() == "Windows":
        try:
            output = run_cmd("net user")
            lines = output.split('\n')
            users = []

            for line in lines:
                if 'User accounts for' not in line and '-----' not in line and 'command completed' not in line and line.strip():
                    potential_users = [user.strip() for user in line.split() if user.strip()]
                    for user in potential_users:
                        if user and user not in ['The', 'command', 'completed', 'successfully.']:
                            users.append(user)

            for user in users:
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
                except Exception:
                    continue
        except Exception as e:
            users_info.append({
                "Username": f"Error: {str(e)}",
                "Details": "Failed to retrieve user information"
            })

    return users_info



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

        # Additional system info for Windows
        if platform.system() == "Windows":
            try:
                computer_info = run_cmd(
                    "systeminfo | findstr /C:\"OS Name\" /C:\"OS Version\" /C:\"System Manufacturer\" /C:\"System Model\"")
                for line in computer_info.split('\n'):
                    if 'OS Name' in line:
                        info["OS Name"] = line.split(':', 1)[1].strip()
                    elif 'OS Version' in line:
                        info["OS Version"] = line.split(':', 1)[1].strip()
                    elif 'System Manufacturer' in line:
                        info["Manufacturer"] = line.split(':', 1)[1].strip()
                    elif 'System Model' in line:
                        info["Model"] = line.split(':', 1)[1].strip()
            except:
                pass
    except:
        pass

    return [[k, v] for k, v in info.items()]


def get_advanced_storage_details():
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
                "Usage (%)": f"{usage.percent}%",
                "Status": "Healthy" if usage.percent < 90 else "Warning"
            })
        except:
            continue
    return disks


def get_comprehensive_graphics_info():
    gpu_info = []
    if platform.system() == "Windows":
        try:
            output = run_cmd(
                "wmic path win32_videocontroller get name, adapterram, driverversion, videoprocessor /format:csv")
            if output and "No Instance" not in output:
                lines = output.split('\n')
                for line in lines:
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 5:
                            gpu_info.append({
                                "Graphics Card": parts[2],
                                "Adapter RAM (GB)": f"{int(parts[3]) / (1024 ** 3):.2f}" if parts[
                                    3].strip().isdigit() else "Unknown",
                                "Driver Version": parts[4],
                                "Video Processor": parts[5] if len(parts) > 5 else "Unknown"
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
        io_counters = psutil.net_io_counters(pernic=True)

        for interface_name, interface_addresses in interfaces.items():
            if interface_name in stats:
                stat = stats[interface_name]
                io = io_counters.get(interface_name)

                interface_data = {
                    "Interface": interface_name,
                    "Status": "ACTIVE" if stat.isup else "INACTIVE",
                    "MTU": stat.mtu,
                    "Speed (Mbps)": f"{stat.speed}" if stat.speed > 0 else "UNKNOWN",
                    "MAC Address": "NONE"
                }

                # Get MAC Address
                for addr in interface_addresses:
                    if addr.family == -1:
                        interface_data["MAC Address"] = addr.address
                        break

                # Get IP Addresses
                ipv4_addrs = []
                ipv6_addrs = []
                for addr in interface_addresses:
                    if addr.family == 2:  # IPv4
                        ipv4_addrs.append(addr.address)
                    elif addr.family == 23:  # IPv6
                        ipv6_addrs.append(addr.address)

                interface_data["IPv4 Addresses"] = ", ".join(ipv4_addrs) if ipv4_addrs else "NONE"
                interface_data["IPv6 Addresses"] = ", ".join(ipv6_addrs) if ipv6_addrs else "NONE"

                # Add I/O statistics if available
                if io:
                    interface_data["Data Sent"] = f"{io.bytes_sent / (1024 ** 2):.1f} MB"
                    interface_data["Data Received"] = f"{io.bytes_recv / (1024 ** 2):.1f} MB"

                net_info.append(interface_data)
    except:
        pass
    return net_info


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

            for profile in profiles:
                try:
                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear')
                    password = "Not stored or encrypted"
                    security = "Unknown"

                    for line in key_output.split('\n'):
                        if 'Key Content' in line and ':' in line:
                            password_value = line.split(':')[1].strip()
                            if password_value:
                                password = password_value
                        elif 'Authentication' in line and ':' in line:
                            security = line.split(':')[1].strip()

                    wifi_info.append({
                        "SSID": profile,
                        "Password": password,
                        "Security": security,
                        "Status": "Password Found" if password != "Not stored or encrypted" else "No Password"
                    })
                except:
                    wifi_info.append({
                        "SSID": profile,
                        "Password": "Error retrieving",
                        "Security": "Unknown",
                        "Status": "Error"
                    })
        except Exception as e:
            wifi_info.append({
                "SSID": "Error",
                "Password": f"Failed: {str(e)}",
                "Security": "N/A",
                "Status": "Failed"
            })
    return wifi_info

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

def get_advanced_system_details():
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
        advanced_info.append({"Category": "CPU_PHYSICAL_CORES", "Detail": psutil.cpu_count(logical=False)})
        advanced_info.append({"Category": "CPU_LOGICAL_CORES", "Detail": psutil.cpu_count(logical=True)})

        # Process information
        processes = len(psutil.pids())
        advanced_info.append({"Category": "RUNNING_PROCESSES", "Detail": processes})

        # Windows-specific advanced details
        if platform.system() == "Windows":
            try:
                # Get system UUID
                output = run_cmd("wmic csproduct get uuid")
                if "UUID" in output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip() and 'UUID' not in line:
                            uuid_value = line.strip()
                            if uuid_value:
                                advanced_info.append({"Category": "SYSTEM_UUID", "Detail": uuid_value})
                                break

                # Get BIOS information
                bios_info = run_cmd("wmic bios get serialnumber,version,manufacturer /format:csv")
                for line in bios_info.split('\n'):
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            advanced_info.append({"Category": "BIOS_MANUFACTURER", "Detail": parts[1]})
                            advanced_info.append({"Category": "BIOS_VERSION", "Detail": parts[3]})
                            break

            except Exception as e:
                advanced_info.append({"Category": "WINDOWS_ADVANCED_ERROR", "Detail": str(e)})

    except Exception as e:
        advanced_info.append({"Category": "ADVANCED_DETAILS_ERROR", "Detail": str(e)})

    return advanced_info


# -------------------------------------------------------------------
#  HTML REPORT GENERATION WITH ENHANCED FEATURES
# -------------------------------------------------------------------
def generate_html_report():
    downloads = get_downloads_folder()
    html_path = os.path.join(downloads, f"System_Comprehensive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    # Gather all data
    sections_data = {
        "System Overview": get_device_specifications(),
        "Storage Details": get_advanced_storage_details(),
        "Graphics Card Information": get_comprehensive_graphics_info(),
        "Network Analysis": get_network_analysis(),
        "WiFi Security Analysis": get_comprehensive_wifi_analysis(),
        "Users Information": get_users_information(),
        "Advanced System Details": get_advanced_system_details(),
        "System Performance": get_system_performance(),
        "Task Manager - Running Processes": get_task_manager_details()
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
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                color: #e0e0e0;
                line-height: 1.6;
            }}

            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}

            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border: 1px solid #34495e;
            }}

            .header h1 {{
                color: #ecf0f1;
                font-size: 2.8em;
                margin-bottom: 10px;
                font-weight: 300;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }}

            .header p {{
                color: #bdc3c7;
                font-size: 1.1em;
                margin: 5px 0;
            }}

            .health-score {{
                display: inline-block;
                background: {get_health_color()};
                color: white;
                padding: 8px 20px;
                border-radius: 25px;
                font-weight: bold;
                margin-top: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}

            .section {{
                background: rgba(255, 255, 255, 0.05);
                padding: 25px;
                border-radius: 12px;
                margin-bottom: 25px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}

            .section:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.4);
                border-color: rgba(52, 152, 219, 0.3);
            }}

            .section h2 {{
                color: #3498db;
                border-bottom: 2px solid #3498db;
                padding-bottom: 12px;
                margin-bottom: 20px;
                font-size: 1.5em;
                font-weight: 400;
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .section h2::before {{
                content: "▶";
                font-size: 0.8em;
                color: #3498db;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                background: rgba(255, 255, 255, 0.02);
                border-radius: 8px;
                overflow: hidden;
            }}

            th {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: #ecf0f1;
                padding: 15px 12px;
                text-align: left;
                font-weight: 500;
                border-bottom: 2px solid #3498db;
                font-size: 0.95em;
            }}

            td {{
                padding: 12px 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                color: #bdc3c7;
                font-size: 0.9em;
            }}

            tr:nth-child(even) {{
                background: rgba(255, 255, 255, 0.03);
            }}

            tr:hover {{
                background: rgba(52, 152, 219, 0.1);
                transform: scale(1.01);
                transition: all 0.2s ease;
            }}

            .status-active {{
                color: #2ecc71;
                font-weight: bold;
            }}

            .status-inactive {{
                color: #e74c3c;
                font-weight: bold;
            }}

            .status-warning {{
                color: #f39c12;
                font-weight: bold;
            }}

            .metric-value {{
                font-family: 'Courier New', monospace;
                background: rgba(52, 152, 219, 0.1);
                padding: 4px 8px;
                border-radius: 4px;
                color: #3498db;
                border: 1px solid rgba(52, 152, 219, 0.3);
            }}

            .footer {{
                text-align: center;
                color: #7f8c8d;
                margin-top: 40px;
                padding: 25px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                font-size: 0.9em;
            }}

            .scroll-container {{
                overflow-x: auto;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                background: rgba(0, 0, 0, 0.2);
            }}

            .scroll-table {{
                min-width: 1200px;
            }}

            .task-manager-table {{
                min-width: 1400px;
            }}

            .performance-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 15px;
            }}

            .performance-card {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .performance-card h3 {{
                color: #3498db;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}

            .performance-value {{
                font-size: 1.8em;
                font-weight: bold;
                color: #ecf0f1;
                margin: 10px 0;
            }}

            .performance-details {{
                color: #bdc3c7;
                font-size: 0.9em;
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}

                .header h1 {{
                    font-size: 2em;
                }}

                .performance-grid {{
                    grid-template-columns: 1fr;
                }}

                table {{
                    font-size: 0.8em;
                }}

                th, td {{
                    padding: 8px 10px;
                }}
            }}

            /* Animation for table rows */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            tr {{
                animation: fadeIn 0.5s ease-out;
            }}

            /* Custom scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}

            ::-webkit-scrollbar-track {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }}

            ::-webkit-scrollbar-thumb {{
                background: #3498db;
                border-radius: 4px;
            }}

            ::-webkit-scrollbar-thumb:hover {{
                background: #2980b9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🖥️ System Comprehensive Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
                <p>Device: {socket.gethostname()} | Platform: {platform.platform()}</p>
                <div class="health-score">
                    System Health Score: {get_system_health_score()}/100
                </div>
            </div>
    """

    # Add each section to HTML
    for section_name, data in sections_data.items():
        html_content += f"""
            <div class="section">
                <h2>{section_name}</h2>
        """

        if data:
            if section_name in ["Network Analysis", "Task Manager - Running Processes"]:
                # Special handling for wide tables with scrolling
                table_class = "task-manager-table" if "Task Manager" in section_name else "scroll-table"
                html_content += f'<div class="scroll-container"><table class="{table_class}">'
            elif section_name == "System Performance":
                # Performance metrics in grid layout
                html_content += '<div class="performance-grid">'
                for item in data:
                    html_content += f'''
                    <div class="performance-card">
                        <h3>{item["Metric"]}</h3>
                        <div class="performance-value">{item["Value"]}</div>
                        <div class="performance-details">{item["Details"]}</div>
                    </div>
                    '''
                html_content += '</div>'
            else:
                html_content += '<table>'

            if section_name != "System Performance":
                if isinstance(data[0], dict):
                    # Table data
                    headers = list(data[0].keys())
                    rows = [[row.get(header, '') for header in headers] for row in data]

                    html_content += '<thead><tr>' + ''.join(
                        f'<th>{header}</th>' for header in headers) + '</tr></thead>'
                    html_content += '<tbody>'
                    for row in rows:
                        # Add status classes for specific columns
                        row_html = '<tr>'
                        for i, cell in enumerate(row):
                            if headers[i] in ["Status", "Account Active"]:
                                if "active" in str(cell).lower() or "yes" in str(cell).lower():
                                    row_html += f'<td class="status-active">{cell}</td>'
                                elif "inactive" in str(cell).lower() or "no" in str(cell).lower():
                                    row_html += f'<td class="status-inactive">{cell}</td>'
                                elif "warning" in str(cell).lower():
                                    row_html += f'<td class="status-warning">{cell}</td>'
                                else:
                                    row_html += f'<td>{cell}</td>'
                            else:
                                row_html += f'<td>{cell}</td>'
                        row_html += '</tr>'
                        html_content += row_html
                    html_content += '</tbody></table>'
                else:
                    # Key-value data
                    for item in data:
                        if len(item) == 2:
                            html_content += f'<tr><td><strong>{item[0]}</strong></td><td class="metric-value">{item[1]}</td></tr>'
                    html_content += '</table>'

            if section_name in ["Network Analysis", "Task Manager - Running Processes"]:
                html_content += '</div>'
        else:
            html_content += '<p style="color: #bdc3c7; text-align: center; padding: 20px;">No data available for this section.</p>'

        html_content += '</div>'

    html_content += """
            <div class="footer">
                <p>🔍 Report generated by Advanced System Information Scanner | 📊 Deep System Analysis</p>
                <p>🕒 Scan completed at """ + datetime.now().strftime('%H:%M:%S') + """ | 💾 All data fetched without limitations</p>
            </div>
        </div>

        <script>
            // Add interactive features
            document.addEventListener('DOMContentLoaded', function() {
                // Add click handlers to section headers
                const sectionHeaders = document.querySelectorAll('.section h2');
                sectionHeaders.forEach(header => {
                    header.addEventListener('click', function() {
                        const section = this.parentElement;
                        section.classList.toggle('collapsed');
                    });
                });

                // Auto-refresh for task manager (conceptual)
                console.log('System report generated successfully');

                // Add sorting capability to tables
                const tables = document.querySelectorAll('table');
                tables.forEach(table => {
                    const headers = table.querySelectorAll('th');
                    headers.forEach((header, index) => {
                        header.style.cursor = 'pointer';
                        header.addEventListener('click', () => {
                            sortTable(table, index);
                        });
                    });
                });

                function sortTable(table, column) {
                    const tbody = table.querySelector('tbody');
                    const rows = Array.from(tbody.querySelectorAll('tr'));

                    rows.sort((a, b) => {
                        const aText = a.cells[column].textContent.trim();
                        const bText = b.cells[column].textContent.trim();

                        // Try to compare as numbers first
                        const aNum = parseFloat(aText.replace(/[^0-9.-]+/g, ""));
                        const bNum = parseFloat(bText.replace(/[^0-9.-]+/g, ""));

                        if (!isNaN(aNum) && !isNaN(bNum)) {
                            return aNum - bNum;
                        }

                        // Fall back to string comparison
                        return aText.localeCompare(bText);
                    });

                    // Remove existing rows
                    rows.forEach(row => tbody.removeChild(row));

                    // Add sorted rows
                    rows.forEach(row => tbody.appendChild(row));
                }
            });
        </script>
    </body>
    </html>
    """

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML report generated successfully!")
    print(f"📁 Location: {html_path}")
    print(f"🌐 Open this file in your browser to view the comprehensive system report")

    return html_path


def get_health_color():
    score = get_system_health_score()
    if score >= 80:
        return "linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)"
    elif score >= 60:
        return "linear-gradient(135deg, #f39c12 0%, #f1c40f 100%)"
    else:
        return "linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)"


# -------------------------------------------------------------------
#  MAIN EXECUTION
# -------------------------------------------------------------------
if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)
    print("🚀 Generating Comprehensive System Report...")
    print("📊 This may take a few moments as we gather all system data...")
    print("⏳ Please wait while we compile the complete system analysis...")

    try:
        html_path = generate_html_report()
        print(f"\n🎉 Report generation completed successfully!")
        print(f"📋 The report includes:")
        print(f"   • System Overview and Specifications")
        print(f"   • Storage Details")
        print(f"   • Graphics Card Information")
        print(f"   • Network Analysis")
        print(f"   • WiFi Security Analysis")
        print(f"   • Users Information")
        print(f"   • Advanced System Details")
        print(f"   • System Performance Metrics")
        print(f"   • Task Manager with Running Processes")
        print(f"\n💡 Tip: Open the HTML file in your browser for the best viewing experience")

    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        print("💡 Please ensure you have necessary permissions and try again")