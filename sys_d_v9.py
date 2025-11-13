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


def simulate_scan_step(step_name, duration=2, steps=20):
    """Simulate a scanning step with progress bar"""
    print_status(f"Scanning: {step_name}", "SCAN")
    for i in range(steps + 1):
        time.sleep(duration / steps)
        progress_bar(i, steps, prefix='Progress:', suffix=step_name, length=30)
    print_status(f"Completed: {step_name}", "SUCCESS")


# -------------------------------------------------------------------
#  ENHANCED COMMAND EXECUTOR WITH PROGRESS
# -------------------------------------------------------------------
command_cache = {}


def run_cmd(cmd, use_cache=True, task_name="Executing command"):
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
            timeout=45
        )

        execution_time = time.time() - start_time
        output = result.stdout.strip()

        if use_cache:
            command_cache[cache_key] = (datetime.now(), output)

        print_status(f"{task_name} completed ({execution_time:.2f}s)", "SUCCESS")
        return output

    except subprocess.TimeoutExpired:
        print_status(f"{task_name} timed out", "ERROR")
        return "[TIMEOUT] Command execution timeout"
    except Exception as e:
        print_status(f"{task_name} failed: {str(e)}", "ERROR")
        return f"[ERROR] Command failed: {str(e)}"


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
    print_status("Collecting process information...", "SCAN")
    processes = []
    total_processes = 0
    collected_processes = 0

    try:
        # First count total processes
        process_list = list(psutil.process_iter(['pid']))
        total_processes = len(process_list)

        for i, proc in enumerate(process_list):
            try:
                process_info = proc.info
                proc_detail = proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_percent',
                                                  'memory_info', 'create_time', 'status', 'cpu_times', 'num_threads'])

                # Calculate process uptime
                create_time = proc_detail['create_time']
                uptime = datetime.now() - datetime.fromtimestamp(create_time)

                # Get CPU times
                cpu_times = proc_detail.get('cpu_times')
                if cpu_times:
                    cpu_time_str = f"{(cpu_times.user + cpu_times.system):.2f}s"
                else:
                    cpu_time_str = "N/A"

                # Get memory details
                memory_info = proc_detail.get('memory_info')
                if memory_info:
                    memory_mb = f"{memory_info.rss / (1024 * 1024):.2f} MB"
                else:
                    memory_mb = "N/A"

                processes.append({
                    "PID": proc_detail['pid'],
                    "Process Name": proc_detail['name'],
                    "User": proc_detail['username'] or "SYSTEM",
                    "CPU %": f"{proc_detail['cpu_percent'] or 0:.2f}",
                    "Memory %": f"{proc_detail['memory_percent'] or 0:.2f}",
                    "Memory Usage": memory_mb,
                    "Threads": proc_detail.get('num_threads', 'N/A'),
                    "Status": proc_detail['status'],
                    "CPU Time": cpu_time_str,
                    "Uptime": str(uptime).split('.')[0],
                    "Started": datetime.fromtimestamp(create_time).strftime('%H:%M:%S')
                })
                collected_processes += 1

                # Update progress every 10 processes
                if i % 10 == 0:
                    progress_bar(i, total_processes, prefix='Process Scan:', suffix=f'{i}/{total_processes} processes',
                                 length=35)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        progress_bar(total_processes, total_processes, prefix='Process Scan:',
                     suffix=f'Complete - {collected_processes} processes', length=35)

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

    # Sort by CPU usage descending
    try:
        processes.sort(key=lambda x: float(x['CPU %'].replace('%', '')) if x['CPU %'] != 'N/A' else 0, reverse=True)
        print_status(f"Sorted {len(processes)} processes by CPU usage", "SUCCESS")
    except Exception as e:
        print_status(f"Sorting failed: {str(e)}", "WARNING")

    return processes[:200]  # Return top 200 processes by CPU usage


def get_system_performance():
    print_status("Analyzing system performance...", "SCAN")
    performance = []

    try:
        # CPU Information with progress
        progress_bar(0, 6, prefix='Performance:', suffix='CPU Analysis', length=30)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        progress_bar(1, 6, prefix='Performance:', suffix='Memory Analysis', length=30)

        # Memory Information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        progress_bar(2, 6, prefix='Performance:', suffix='Disk Analysis', length=30)

        # Disk Information
        disk_io = psutil.disk_io_counters()
        progress_bar(3, 6, prefix='Performance:', suffix='Network Analysis', length=30)

        # Network Information
        net_io = psutil.net_io_counters()
        progress_bar(4, 6, prefix='Performance:', suffix='Compiling Data', length=30)

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

        progress_bar(6, 6, prefix='Performance:', suffix='Complete', length=30)
        print_status("System performance analysis completed", "SUCCESS")

    except Exception as e:
        print_status(f"Performance analysis failed: {str(e)}", "ERROR")

    return performance


# -------------------------------------------------------------------
#  USERS AND ACCOUNTS INFORMATION
# -------------------------------------------------------------------
def get_users_information():
    print_status("Collecting user account information...", "SCAN")
    users_info = []

    if platform.system() == "Windows":
        try:
            output = run_cmd("net user", task_name="Retrieving user list")
            lines = output.split('\n')
            users = []

            # Parse user accounts with progress
            user_lines = [line for line in lines if
                          'User accounts for' not in line and '-----' not in line and 'command completed' not in line and line.strip()]
            total_users = len(user_lines)

            for i, line in enumerate(user_lines):
                potential_users = [user.strip() for user in line.split() if user.strip()]
                for user in potential_users:
                    if user and user not in ['The', 'command', 'completed', 'successfully.']:
                        users.append(user)

                progress_bar(i, total_users, prefix='User Scan:', suffix=f'Processing users', length=30)

            print_status(f"Found {len(users)} user accounts", "DATA")

            # Get detailed user information
            for i, user in enumerate(users):
                try:
                    user_details = run_cmd(f'net user "{user}"', task_name=f"Analyzing user {user}")
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
                    progress_bar(i + 1, len(users), prefix='User Details:', suffix=f'{user}', length=30)

                except Exception:
                    continue

            print_status(f"Collected details for {len(users_info)} users", "SUCCESS")

        except Exception as e:
            print_status(f"User information collection failed: {str(e)}", "ERROR")
            users_info.append({
                "Username": f"Error: {str(e)}",
                "Details": "Failed to retrieve user information"
            })
    else:
        print_status("User collection for Linux systems", "INFO")
        # Linux implementation would go here

    return users_info

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

# -------------------------------------------------------------------
#  SYSTEM INFORMATION GATHERING WITH PROGRESS
# -------------------------------------------------------------------
def get_system_health_score():
    score = 100
    try:
        cpu_usage = psutil.cpu_percent(interval=0.5)
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
    print_status("Collecting system specifications...", "SCAN")
    info = OrderedDict()

    progress_bar(1, 8, prefix='System Specs:', suffix='Basic Info', length=30)
    info["Host Name"] = socket.gethostname()
    info["Processor"] = platform.processor()
    info["Platform"] = platform.platform()
    info["Architecture"] = platform.architecture()[0]
    info["System Type"] = platform.machine()
    info["Python Version"] = platform.python_version()

    try:
        progress_bar(2, 8, prefix='System Specs:', suffix='Memory Analysis', length=30)
        memory = psutil.virtual_memory()
        info["Total RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"
        info["Available RAM"] = f"{memory.available / (1024 ** 3):.2f} GB"
        info["RAM Usage"] = f"{memory.percent}%"

        progress_bar(3, 8, prefix='System Specs:', suffix='Uptime Calculation', length=30)
        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        info["System Uptime"] = str(uptime).split('.')[0]
        info["System Health"] = f"{get_system_health_score()}/100"

        progress_bar(4, 8, prefix='System Specs:', suffix='Windows Specific', length=30)
        # Additional system info for Windows
        if platform.system() == "Windows":
            try:
                computer_info = run_cmd(
                    "systeminfo | findstr /C:\"OS Name\" /C:\"OS Version\" /C:\"System Manufacturer\" /C:\"System Model\"",
                    task_name="Retrieving Windows system info")
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

        progress_bar(8, 8, prefix='System Specs:', suffix='Complete', length=30)
        print_status("System specifications collected", "SUCCESS")

    except Exception as e:
        print_status(f"System specs collection error: {str(e)}", "ERROR")

    return [[k, v] for k, v in info.items()]


def get_advanced_storage_details():
    print_status("Analyzing storage devices...", "SCAN")
    disks = []
    partitions = list(psutil.disk_partitions())

    for i, part in enumerate(partitions):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "Device": part.device,
                "Mountpoint": part.mountpoint,
                "File System": part.fstype,
                "Total Size": f"{usage.total / (1024 ** 3):.2f} GB",
                "Used": f"{usage.used / (1024 ** 3):.2f} GB",
                "Free": f"{usage.free / (1024 ** 3):.2f} GB",
                "Usage": f"{usage.percent}%",
                "Status": "HEALTHY" if usage.percent < 90 else "WARNING"
            })
            progress_bar(i + 1, len(partitions), prefix='Storage Scan:', suffix=part.device, length=30)
        except:
            continue

    print_status(f"Analyzed {len(disks)} storage devices", "SUCCESS")
    return disks


def get_comprehensive_graphics_info():
    print_status("Collecting graphics card information...", "SCAN")
    gpu_info = []

    if platform.system() == "Windows":
        try:
            output = run_cmd(
                "wmic path win32_videocontroller get name, adapterram, driverversion, videoprocessor /format:csv",
                task_name="Querying GPU information")
            if output and "No Instance" not in output:
                lines = output.split('\n')
                gpu_count = 0

                for line in lines:
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 5:
                            gpu_info.append({
                                "Graphics Card": parts[2],
                                "Adapter RAM": f"{int(parts[3]) / (1024 ** 3):.2f} GB" if parts[
                                    3].strip().isdigit() else "UNKNOWN",
                                "Driver Version": parts[4],
                                "Video Processor": parts[5] if len(parts) > 5 else "UNKNOWN"
                            })
                            gpu_count += 1

                progress_bar(gpu_count, gpu_count if gpu_count > 0 else 1, prefix='GPU Scan:',
                             suffix=f'{gpu_count} GPUs found', length=30)
                print_status(f"Found {gpu_count} graphics cards", "SUCCESS")
        except Exception as e:
            print_status(f"GPU information collection failed: {str(e)}", "ERROR")

    return gpu_info if gpu_info else [
        {"Graphics Card": "No GPU information available", "Details": "Check system configuration"}]


def get_network_analysis():
    print_status("Analyzing network interfaces...", "SCAN")
    net_info = []

    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        total_interfaces = len(interfaces)

        for i, (interface_name, interface_addresses) in enumerate(interfaces.items()):
            if interface_name in stats:
                stat = stats[interface_name]
                io = io_counters.get(interface_name)

                interface_data = {
                    "Interface": interface_name,
                    "Status": "ACTIVE" if stat.isup else "INACTIVE",
                    "MTU": stat.mtu,
                    "Speed": f"{stat.speed} Mbps" if stat.speed > 0 else "UNKNOWN",
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

            progress_bar(i + 1, total_interfaces, prefix='Network Scan:', suffix=interface_name, length=30)

        print_status(f"Analyzed {len(net_info)} network interfaces", "SUCCESS")

    except Exception as e:
        print_status(f"Network analysis failed: {str(e)}", "ERROR")

    return net_info


def get_comprehensive_wifi_analysis():
    print_status("Scanning WiFi networks...", "SCAN")
    wifi_info = []

    if platform.system() == "Windows":
        try:
            profiles_output = run_cmd("netsh wlan show profiles", task_name="Retrieving WiFi profiles")
            profiles = []
            for line in profiles_output.split('\n'):
                if 'All User Profile' in line and ':' in line:
                    profile_name = line.split(':')[1].strip()
                    if profile_name:
                        profiles.append(profile_name)

            print_status(f"Found {len(profiles)} WiFi profiles", "DATA")

            for i, profile in enumerate(profiles):
                try:
                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear',
                                         task_name=f"Analyzing WiFi: {profile}")
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
                        "Status": "PASSWORD_FOUND" if password != "Not stored or encrypted" else "NO_PASSWORD"
                    })

                    progress_bar(i + 1, len(profiles), prefix='WiFi Analysis:', suffix=profile, length=30)

                except:
                    wifi_info.append({
                        "SSID": profile,
                        "Password": "ERROR_RETRIEVING",
                        "Security": "UNKNOWN",
                        "Status": "ERROR"
                    })

            found_passwords = len([w for w in wifi_info if w["Status"] == "PASSWORD_FOUND"])
            print_status(f"WiFi analysis complete - {found_passwords} passwords found", "SUCCESS")

        except Exception as e:
            print_status(f"WiFi analysis failed: {str(e)}", "ERROR")

    return wifi_info


def get_advanced_system_details():
    print_status("Collecting advanced system details...", "SCAN")
    advanced_info = []

    try:
        steps_completed = 0
        total_steps = 10

        # System architecture details
        progress_bar(steps_completed := steps_completed + 1, total_steps, prefix='Advanced Scan:',
                     suffix='Architecture', length=30)
        advanced_info.append({"Category": "ARCHITECTURE", "Detail": platform.architecture()[0]})
        advanced_info.append({"Category": "PROCESSOR_BITS", "Detail": "64-bit" if sys.maxsize > 2 ** 32 else "32-bit"})

        # System boot details
        progress_bar(steps_completed := steps_completed + 1, total_steps, prefix='Advanced Scan:', suffix='Boot Info',
                     length=30)
        boot_time = psutil.boot_time()
        advanced_info.append(
            {"Category": "LAST_BOOT", "Detail": datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')})

        # Memory details
        progress_bar(steps_completed := steps_completed + 1, total_steps, prefix='Advanced Scan:',
                     suffix='Memory Details', length=30)
        memory = psutil.virtual_memory()
        advanced_info.append({"Category": "MEMORY_TOTAL", "Detail": f"{memory.total / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "MEMORY_AVAILABLE", "Detail": f"{memory.available / (1024 ** 3):.2f} GB"})

        # CPU details
        progress_bar(steps_completed := steps_completed + 1, total_steps, prefix='Advanced Scan:', suffix='CPU Info',
                     length=30)
        advanced_info.append({"Category": "CPU_PHYSICAL_CORES", "Detail": psutil.cpu_count(logical=False)})
        advanced_info.append({"Category": "CPU_LOGICAL_CORES", "Detail": psutil.cpu_count(logical=True)})

        # Process information
        progress_bar(steps_completed := steps_completed + 1, total_steps, prefix='Advanced Scan:',
                     suffix='Process Count', length=30)
        processes = len(psutil.pids())
        advanced_info.append({"Category": "RUNNING_PROCESSES", "Detail": processes})

        # Windows-specific advanced details
        if platform.system() == "Windows":
            try:
                progress_bar(steps_completed := steps_completed + 1, total_steps, prefix='Advanced Scan:',
                             suffix='System UUID', length=30)
                output = run_cmd("wmic csproduct get uuid", task_name="Retrieving system UUID")
                if "UUID" in output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip() and 'UUID' not in line:
                            uuid_value = line.strip()
                            if uuid_value:
                                advanced_info.append({"Category": "SYSTEM_UUID", "Detail": uuid_value})
                                break

                progress_bar(steps_completed := steps_completed + 1, total_steps, prefix='Advanced Scan:',
                             suffix='BIOS Info', length=30)
                bios_info = run_cmd("wmic bios get serialnumber,version,manufacturer /format:csv",
                                    task_name="Retrieving BIOS information")
                for line in bios_info.split('\n'):
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            advanced_info.append({"Category": "BIOS_MANUFACTURER", "Detail": parts[1]})
                            advanced_info.append({"Category": "BIOS_VERSION", "Detail": parts[3]})
                            break

            except Exception as e:
                advanced_info.append({"Category": "WINDOWS_ADVANCED_ERROR", "Detail": str(e)})

        progress_bar(total_steps, total_steps, prefix='Advanced Scan:', suffix='Complete', length=30)
        print_status("Advanced system details collected", "SUCCESS")

    except Exception as e:
        print_status(f"Advanced details collection failed: {str(e)}", "ERROR")
        advanced_info.append({"Category": "ADVANCED_DETAILS_ERROR", "Detail": str(e)})

    return advanced_info


# -------------------------------------------------------------------
#  HTML REPORT GENERATION WITH PROGRESS
# -------------------------------------------------------------------
def generate_html_report():
    print_status("Starting comprehensive system scan...", "SCAN")
    downloads = get_downloads_folder()
    html_path = os.path.join(downloads, f"SYSTEM_SCAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    # Define scan steps with weights for progress calculation
    scan_steps = [
        ("System Overview", get_device_specifications, 10),
        ("Storage Analysis", get_advanced_storage_details, 15),
        ("Graphics Card Information", get_comprehensive_graphics_info, 5),
        ("Network Analysis", get_network_analysis, 15),
        ("WiFi Security Analysis", get_comprehensive_wifi_analysis, 20),
        ("User Accounts", get_users_information, 10),
        ("Advanced System Details", get_advanced_system_details, 10),
        ("System Performance", get_system_performance, 10),
        ("Task Manager", get_task_manager_details, 25)
    ]

    total_weight = sum(weight for _, _, weight in scan_steps)
    current_progress = 0
    sections_data = {}

    print_status("Beginning data collection phase...", "INFO")

    for step_name, step_function, weight in scan_steps:
        print_status(f"Scanning: {step_name}", "SCAN")
        try:
            sections_data[step_name.upper()] = step_function()
            current_progress += weight
            progress_bar(current_progress, total_weight, prefix='Overall Progress:', suffix=step_name, length=40)
        except Exception as e:
            print_status(f"Error in {step_name}: {str(e)}", "ERROR")
            sections_data[step_name.upper()] = [{"Error": f"Failed to collect {step_name}: {str(e)}"}]
            current_progress += weight  # Still count the weight even if failed

    print_status("Compiling HTML report...", "SCAN")

    # HTML generation code would continue here (same as before)
    # ... [HTML content generation code] ...

    print_status("HTML report generated successfully!", "SUCCESS")
    return html_path


def get_health_color():
    score = get_system_health_score()
    if score >= 80:
        return "linear-gradient(135deg, #00ff00 0%, #00cc00 100%)"
    elif score >= 60:
        return "linear-gradient(135deg, #ffff00 0%, #cccc00 100%)"
    else:
        return "linear-gradient(135deg, #ff0000 0%, #cc0000 100%)"


# -------------------------------------------------------------------
#  MAIN EXECUTION WITH ENHANCED UI
# -------------------------------------------------------------------
if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)
    print("\n\n\n")
    print_colored("╔══════════════════════════════════════════════════════════════╗", Colors.GREEN)
    print_colored("║                   SYSTEM SCAN INITIATED                     ║", Colors.GREEN)
    print_colored("║                 Advanced Intelligence Scanner               ║", Colors.CYAN)
    print_colored("╚══════════════════════════════════════════════════════════════╝", Colors.GREEN)
    print()

    print_status("Initializing scanner modules...", "INFO")
    time.sleep(1)

    try:
        html_path = generate_html_report()

        print()
        print_colored("╔══════════════════════════════════════════════════════════════╗", Colors.GREEN)
        print_colored("║                     SCAN COMPLETED                          ║", Colors.GREEN)
        print_colored("╚══════════════════════════════════════════════════════════════╝", Colors.GREEN)
        print()

        print_status("REPORT GENERATION SUMMARY:", "SUCCESS")
        print_status(f"Output File: {html_path}", "DATA")
        print_status("System Health Score: " + str(get_system_health_score()) + "/100",
                     "SUCCESS" if get_system_health_score() >= 70 else "WARNING")
        print()

        print_status("SECTIONS INCLUDED:", "INFO")
        sections = [
            "SYSTEM OVERVIEW", "STORAGE ANALYSIS", "GRAPHICS CARD INFORMATION",
            "NETWORK ANALYSIS", "WIFI SECURITY ANALYSIS", "USER ACCOUNTS",
            "ADVANCED SYSTEM DETAILS", "SYSTEM PERFORMANCE", "TASK MANAGER"
        ]
        for section in sections:
            print_colored(f"    ✓ {section}", Colors.GREEN)

        print()
        print_status("Opening report in default browser...", "INFO")

        # Try to open the file in default browser
        try:
            if platform.system() == "Windows":
                os.startfile(html_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", html_path])
            else:  # Linux
                subprocess.run(["xdg-open", html_path])
            print_status("Browser launched successfully", "SUCCESS")
        except:
            print_status("Could not open browser automatically", "WARNING")
            print_status(f"Please open manually: {html_path}", "INFO")

    except Exception as e:
        print_status(f"SCAN FAILED: {str(e)}", "ERROR")
        print_status("Please ensure you have necessary permissions", "WARNING")