import os
import sys
import subprocess
import platform
from datetime import datetime
import socket
import json
import time
from collections import OrderedDict
import threading
import random
import webbrowser


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
    ORANGE = '\033[38;5;214m'
    PINK = '\033[38;5;205m'
    PURPLE = '\033[38;5;141m'


def print_colored(text, color=Colors.WHITE, end="\n"):
    print(f"{color}{text}{Colors.RESET}", end=end)


def print_status(message, status="INFO"):
    status_colors = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "SCAN": Colors.CYAN,
        "DATA": Colors.MAGENTA,
        "SYSTEM": Colors.ORANGE,
        "NETWORK": Colors.PURPLE,
        "SECURITY": Colors.PINK
    }
    color = status_colors.get(status, Colors.WHITE)
    prefix = {
        "INFO": "[*]",
        "SUCCESS": "[+]",
        "WARNING": "[!]",
        "ERROR": "[-]",
        "SCAN": "[>]",
        "DATA": "[#]",
        "SYSTEM": "[S]",
        "NETWORK": "[N]",
        "SECURITY": "[$]"
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


def print_banner():
    """Display advanced ASCII art banner"""
    banner = f"""
{Colors.PURPLE}
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║  {Colors.CYAN}╔═╗┌─┐┌┬┐┌─┐┬┌┐┌┌─┐  ╔═╗┬ ┬┌─┐┌─┐┌─┐┬─┐  {Colors.ORANGE}╔═╗╔═╗╔╗╔╔═╗╦╔═╗╔═╗╔╦╗  {Colors.PURPLE}║
    ║  {Colors.CYAN}╠═╝├─┤ │ ├─┤│││││ │  ║  ├─┤├┤ │  ├┤ ├┬┘  {Colors.ORANGE}╠═╣║ ║║║║║╣ ║╚═╗║╣  ║║  {Colors.PURPLE}║
    ║  {Colors.CYAN}╩  ┴ ┴ ┴ ┴ ┴┴┘└┘└─┘  ╚═╝┴ ┴└─┘└─┘└─┘┴└─  {Colors.ORANGE}╩ ╩╚═╝╝╚╝╚═╝╩╚═╝╚═╝═╩╝  {Colors.PURPLE}║
    ║                                                                  ║
    ║              {Colors.PINK}CREATED BY: {Colors.GREEN}SABARI425 {Colors.PURPLE}                       ║
    ║         {Colors.YELLOW}Advanced System Intelligence Platform{Colors.PURPLE}              ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """
    print(banner)


def print_scanning_animation():
    """Display scanning animation"""
    animations = [
        f"{Colors.CYAN}[{Colors.GREEN}■{Colors.CYAN}□□□□□□□□] Scanning System{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■{Colors.CYAN}□□□□□□□] Analyzing Hardware{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■■{Colors.CYAN}□□□□□□] Checking Network{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■■■{Colors.CYAN}□□□□□] Gathering Security Data{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■■■■{Colors.CYAN}□□□□] Processing Performance{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■■■■■{Colors.CYAN}□□□] Compiling Reports{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■■■■■■{Colors.CYAN}□□] Finalizing Analysis{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■■■■■■■{Colors.CYAN}□] Generating Output{Colors.RESET}",
        f"{Colors.CYAN}[{Colors.GREEN}■■■■■■■■■{Colors.CYAN}] Complete!{Colors.RESET}"
    ]

    for anim in animations:
        print(f"\r{anim}", end="", flush=True)
        time.sleep(0.3)
    print()


def print_system_stats():
    """Display real-time system statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        stats = f"""
{Colors.ORANGE}┌─────────────────── {Colors.CYAN}LIVE SYSTEM STATS {Colors.ORANGE}───────────────────┐{Colors.RESET}
{Colors.ORANGE}│{Colors.RESET}  {Colors.GREEN}CPU Usage:{Colors.RESET}    {cpu_percent:6.1f}%     {Colors.YELLOW}Memory Usage:{Colors.RESET}  {memory.percent:6.1f}%  {Colors.ORANGE}│{Colors.RESET}
{Colors.ORANGE}│{Colors.RESET}  {Colors.BLUE}Memory Used:{Colors.RESET}  {memory.used / 1024 / 1024 / 1024:6.1f} GB   {Colors.MAGENTA}Disk Usage:{Colors.RESET}    {disk.percent:6.1f}%  {Colors.ORANGE}│{Colors.RESET}
{Colors.ORANGE}│{Colors.RESET}  {Colors.CYAN}Memory Free:{Colors.RESET}  {memory.available / 1024 / 1024 / 1024:6.1f} GB   {Colors.PINK}Processes:{Colors.RESET}     {len(psutil.pids()):6d}   {Colors.ORANGE}│{Colors.RESET}
{Colors.ORANGE}└─────────────────────────────────────────────────────────┘{Colors.RESET}
        """
        print(stats)
    except Exception as e:
        print_status(f"Could not display system stats: {str(e)}", "WARNING")


def print_scan_header():
    """Display scan initiation header"""
    header = f"""
{Colors.PURPLE}╔══════════════════════════════════════════════════════════════════╗
{Colors.PURPLE}║{Colors.CYAN}                    SCAN INITIATION SEQUENCE                    {Colors.PURPLE}║
{Colors.PURPLE}║{Colors.GREEN}              Comprehensive System Analysis Started            {Colors.PURPLE}║
{Colors.PURPLE}║{Colors.YELLOW}                     Target: {socket.gethostname():<30}   {Colors.PURPLE}║
{Colors.PURPLE}║{Colors.BLUE}                   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}               {Colors.PURPLE}║
{Colors.PURPLE}╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(header)


# -------------------------------------------------------------------
#  ENHANCED DATA COLLECTION FUNCTIONS
# -------------------------------------------------------------------
command_cache = {}
html_file_opened = False


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


def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# -------------------------------------------------------------------
#  ENHANCED TASK MANAGER SECTION
# -------------------------------------------------------------------
def get_enhanced_task_manager_details():
    print_status("Collecting comprehensive process information...", "SYSTEM")
    processes = []

    try:
        all_processes = list(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent',
                                                  'memory_info', 'create_time', 'status', 'cpu_times', 'num_threads',
                                                  'exe', 'connections', 'nice', 'ionice', 'num_ctx_switches']))

        total_processes = len(all_processes)
        print_status(f"Analyzing {total_processes} processes...", "DATA")

        for i, proc in enumerate(all_processes):
            try:
                process_info = proc.info

                # Calculate process uptime
                create_time = process_info['create_time']
                uptime = datetime.now() - datetime.fromtimestamp(create_time)

                # Get CPU times
                cpu_times = process_info.get('cpu_times')
                if cpu_times:
                    cpu_time_str = f"{(cpu_times.user + cpu_times.system):.2f}s"
                    cpu_user = f"{cpu_times.user:.2f}s"
                    cpu_system = f"{cpu_times.system:.2f}s"
                else:
                    cpu_time_str = "N/A"
                    cpu_user = "N/A"
                    cpu_system = "N/A"

                # Get memory details
                memory_info = process_info.get('memory_info')
                if memory_info:
                    memory_mb = f"{memory_info.rss / (1024 * 1024):.2f} MB"
                    memory_vms = f"{memory_info.vms / (1024 * 1024):.2f} MB"
                else:
                    memory_mb = "N/A"
                    memory_vms = "N/A"

                # Get executable path
                exe_path = process_info.get('exe', 'N/A')
                if exe_path and len(exe_path) > 30:
                    exe_display = "..." + exe_path[-27:]
                else:
                    exe_display = exe_path

                # Get process priority
                nice_value = process_info.get('nice', 'N/A')
                priority_map = {
                    -20: "Real-time", -15: "High", -10: "Above Normal",
                    0: "Normal", 10: "Below Normal", 15: "Low", 19: "Background"
                }
                priority = priority_map.get(nice_value, f"Nice:{nice_value}")

                # Get I/O information
                io_counters = process_info.get('num_ctx_switches')
                if io_counters:
                    ctx_switches = f"{io_counters.voluntary + io_counters.involuntary:,}"
                else:
                    ctx_switches = "N/A"

                # Get network connections
                connections = process_info.get('connections')
                if connections:
                    net_connections = len(connections)
                else:
                    net_connections = 0

                # Determine process risk level
                risk_level = "LOW"
                process_name = process_info['name'].lower()
                suspicious_keywords = ['crypt', 'miner', 'bitcoin', 'monero', 'keylogger', 'spy', 'stealer']
                if any(keyword in process_name for keyword in suspicious_keywords):
                    risk_level = "HIGH"
                elif process_info['username'] and 'system' not in process_info['username'].lower():
                    risk_level = "MEDIUM"

                processes.append({
                    "PID": process_info['pid'],
                    "Process Name": process_info['name'],
                    "User": process_info['username'] or "SYSTEM",
                    "CPU %": f"{process_info['cpu_percent'] or 0:.2f}",
                    "Memory %": f"{process_info['memory_percent'] or 0:.2f}",
                    "Memory Usage": memory_mb,
                    "Virtual Memory": memory_vms,
                    "Threads": process_info.get('num_threads', 'N/A'),
                    "Status": process_info['status'],
                    "CPU Time": cpu_time_str,
                    "CPU User": cpu_user,
                    "CPU System": cpu_system,
                    "Uptime": str(uptime).split('.')[0],
                    "Started": datetime.fromtimestamp(create_time).strftime('%H:%M:%S'),
                    "Executable": exe_display,
                    "Full Path": exe_path,
                    "Priority": priority,
                    "Context Switches": ctx_switches,
                    "Network Connections": net_connections,
                    "Risk Level": risk_level
                })

                # Show progress for large process lists
                if i % 50 == 0:
                    progress_bar(i, total_processes, prefix='Processing', suffix=f'{i}/{total_processes}')

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                continue

        print()  # New line after progress bar

    except Exception as e:
        print_status(f"Process collection error: {str(e)}", "ERROR")

    # Sort by CPU usage descending
    try:
        processes.sort(key=lambda x: float(x['CPU %'].replace('%', '')) if x['CPU %'] != 'N/A' else 0, reverse=True)
        print_status(f"Sorted {len(processes)} processes by CPU usage", "SUCCESS")
    except Exception as e:
        print_status(f"Sorting failed: {str(e)}", "WARNING")

    # Show process statistics
    total_memory = sum(float(p['Memory Usage'].split()[0]) for p in processes if p['Memory Usage'] != 'N/A')
    high_risk = sum(1 for p in processes if p['Risk Level'] == 'HIGH')
    medium_risk = sum(1 for p in processes if p['Risk Level'] == 'MEDIUM')

    print_status(f"Process Statistics: {len(processes)} total, {total_memory:.1f} MB memory, "
                 f"{high_risk} high risk, {medium_risk} medium risk", "DATA")

    return processes[:200]  # Return top 200 processes


def get_process_tree():
    """Get process parent-child relationships"""
    print_status("Building process tree...", "SYSTEM")
    process_tree = []

    try:
        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'username']):
            try:
                info = proc.info
                process_tree.append({
                    "PID": info['pid'],
                    "Name": info['name'],
                    "Parent PID": info['ppid'],
                    "User": info['username'] or "SYSTEM"
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print_status(f"Built tree with {len(process_tree)} processes", "SUCCESS")
    except Exception as e:
        print_status(f"Process tree building failed: {str(e)}", "ERROR")

    return process_tree


def get_running_services():
    """Get information about running services"""
    print_status("Collecting service information...", "SYSTEM")
    services = []

    if platform.system() == "Windows":
        try:
            output = run_cmd("sc query state= all", task_name="Querying services")
            lines = output.split('\n')
            current_service = {}

            for line in lines:
                line = line.strip()
                if line.startswith('SERVICE_NAME:'):
                    if current_service:
                        services.append(current_service)
                    current_service = {'SERVICE_NAME': line.split(':', 1)[1].strip()}
                elif line.startswith('DISPLAY_NAME:'):
                    current_service['DISPLAY_NAME'] = line.split(':', 1)[1].strip()
                elif line.startswith('STATE'):
                    current_service['STATE'] = line.split(':', 1)[1].strip()
                elif line.startswith('PID'):
                    current_service['PID'] = line.split(':', 1)[1].strip()

            if current_service:
                services.append(current_service)

            print_status(f"Found {len(services)} services", "SUCCESS")
        except Exception as e:
            print_status(f"Service collection failed: {str(e)}", "ERROR")

    return services


# -------------------------------------------------------------------
#  COMPREHENSIVE DATA COLLECTION FUNCTIONS
# -------------------------------------------------------------------
def get_system_health_score():
    score = 100
    try:
        # CPU health (30 points)
        cpu_usage = psutil.cpu_percent(interval=0.5)
        if cpu_usage > 90:
            score -= 25
        elif cpu_usage > 80:
            score -= 20
        elif cpu_usage > 70:
            score -= 15
        elif cpu_usage > 60:
            score -= 10

        # Memory health (30 points)
        memory = psutil.virtual_memory()
        if memory.percent > 95:
            score -= 25
        elif memory.percent > 85:
            score -= 20
        elif memory.percent > 75:
            score -= 15
        elif memory.percent > 65:
            score -= 10

        # Disk health (30 points)
        disk_penalty = 0
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                if usage.percent > 95:
                    disk_penalty = max(disk_penalty, 25)
                elif usage.percent > 90:
                    disk_penalty = max(disk_penalty, 20)
                elif usage.percent > 85:
                    disk_penalty = max(disk_penalty, 15)
                elif usage.percent > 80:
                    disk_penalty = max(disk_penalty, 10)
            except:
                continue
        score -= disk_penalty

        # Process health (10 points)
        processes = len(psutil.pids())
        if processes > 500:
            score -= 5
        elif processes > 300:
            score -= 3

    except Exception as e:
        print_status(f"Health score calculation error: {str(e)}", "WARNING")

    return max(score, 0)


def get_health_color(score=None):
    if score is None:
        score = get_system_health_score()
    if score >= 80:
        return "linear-gradient(135deg, #00ff00 0%, #00cc00 100%)"
    elif score >= 60:
        return "linear-gradient(135deg, #ffff00 0%, #cccc00 100%)"
    else:
        return "linear-gradient(135deg, #ff0000 0%, #cc0000 100%)"


def get_device_specifications():
    print_status("Collecting system specifications...", "SYSTEM")
    info = OrderedDict()

    info["Host Name"] = socket.gethostname()
    info["Processor"] = platform.processor() or "Unknown"
    info["Platform"] = platform.platform()
    info["Architecture"] = platform.architecture()[0]
    info["System Type"] = platform.machine()
    info["Python Version"] = platform.python_version()

    try:
        memory = psutil.virtual_memory()
        info["Total RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"
        info["Available RAM"] = f"{memory.available / (1024 ** 3):.2f} GB"
        info["RAM Usage"] = f"{memory.percent}%"

        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        info["System Uptime"] = str(uptime).split('.')[0]

        health_score = get_system_health_score()
        info["System Health"] = f"{health_score}/100"

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
    except Exception as e:
        print_status(f"System specs collection error: {str(e)}", "ERROR")

    return [[k, v] for k, v in info.items()]


def get_advanced_storage_details():
    print_status("Analyzing storage devices...", "SYSTEM")
    disks = []

    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_io = psutil.disk_io_counters(perdisk=True)

            disk_info = {
                "Device": part.device,
                "Mountpoint": part.mountpoint,
                "File System": part.fstype,
                "Total Size": f"{usage.total / (1024 ** 3):.2f} GB",
                "Used": f"{usage.used / (1024 ** 3):.2f} GB",
                "Free": f"{usage.free / (1024 ** 3):.2f} GB",
                "Usage": f"{usage.percent}%",
                "Status": "HEALTHY" if usage.percent < 85 else "WARNING"
            }

            # Add disk I/O if available
            if disk_io:
                device_key = part.device.replace('\\', '').replace(':', '')
                if device_key in disk_io:
                    io = disk_io[device_key]
                    disk_info["Read Speed"] = f"{io.read_bytes / (1024 ** 2):.0f} MB"
                    disk_info["Write Speed"] = f"{io.write_bytes / (1024 ** 2):.0f} MB"

            disks.append(disk_info)
        except:
            continue

    print_status(f"Analyzed {len(disks)} storage devices", "SUCCESS")
    return disks


def get_comprehensive_graphics_info():
    print_status("Collecting graphics card information...", "SYSTEM")
    gpu_info = []

    if platform.system() == "Windows":
        try:
            output = run_cmd(
                "wmic path win32_videocontroller get name, adapterram, driverversion, videoprocessor, videomodedescription /format:csv")
            if output and "No Instance" not in output:
                lines = output.split('\n')
                for line in lines:
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 5:
                            gpu_info.append({
                                "Graphics Card": parts[2],
                                "Adapter RAM": f"{int(parts[3]) / (1024 ** 3):.2f} GB" if parts[
                                    3].strip().isdigit() else "UNKNOWN",
                                "Driver Version": parts[4],
                                "Video Processor": parts[5] if len(parts) > 5 else "UNKNOWN",
                                "Current Resolution": parts[6] if len(parts) > 6 else "UNKNOWN"
                            })
        except Exception as e:
            print_status(f"GPU information collection failed: {str(e)}", "ERROR")

    return gpu_info if gpu_info else [
        {"Graphics Card": "No GPU information available", "Details": "Check system configuration"}]


def get_network_analysis():
    print_status("Analyzing network interfaces...", "NETWORK")
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
                    "Speed": f"{stat.speed} Mbps" if stat.speed > 0 else "UNKNOWN",
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
                    if addr.family == -1:
                        interface_data["MAC Address"] = addr.address
                        break

                # Get IP Addresses
                ipv4_addrs = []
                ipv6_addrs = []
                for addr in interface_addresses:
                    if addr.family == 2:  # IPv4
                        ipv4_addrs.append(f"{addr.address}/{addr.netmask}")
                    elif addr.family == 23:  # IPv6
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

        print_status(f"Analyzed {len(net_info)} network interfaces", "SUCCESS")

    except Exception as e:
        print_status(f"Network analysis failed: {str(e)}", "ERROR")

    return net_info


def get_comprehensive_wifi_analysis():
    print_status("Scanning WiFi networks...", "SECURITY")
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

            print_status(f"Found {len(profiles)} WiFi profiles", "DATA")

            for profile in profiles:
                try:
                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear')
                    password = "Not stored or encrypted"
                    security = "Unknown"
                    connection_mode = "Unknown"
                    ssid = profile

                    for line in key_output.split('\n'):
                        line_lower = line.lower()
                        if 'key content' in line_lower and ':' in line:
                            password_value = line.split(':')[1].strip()
                            if password_value:
                                password = password_value
                        elif 'authentication' in line_lower and ':' in line:
                            security = line.split(':')[1].strip()
                        elif 'connection mode' in line_lower and ':' in line:
                            connection_mode = line.split(':')[1].strip()
                        elif 'ssid name' in line_lower and ':' in line:
                            ssid = line.split(':')[1].strip()

                    wifi_info.append({
                        "SSID": ssid,
                        "Password": password,
                        "Security Type": security,
                        "Connection Mode": connection_mode,
                        "Status": "PASSWORD_FOUND" if password != "Not stored or encrypted" else "NO_PASSWORD"
                    })

                except:
                    wifi_info.append({
                        "SSID": profile,
                        "Password": "ERROR_RETRIEVING",
                        "Security Type": "UNKNOWN",
                        "Connection Mode": "UNKNOWN",
                        "Status": "ERROR"
                    })

            found_passwords = len([w for w in wifi_info if w["Status"] == "PASSWORD_FOUND"])
            print_status(f"WiFi analysis complete - {found_passwords} passwords found", "SUCCESS")

        except Exception as e:
            print_status(f"WiFi analysis failed: {str(e)}", "ERROR")

    return wifi_info


def get_users_information():
    print_status("Collecting user account information...", "SECURITY")
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

            print_status(f"Found {len(users)} user accounts", "DATA")

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
                        "Local Group Memberships": "N/A",
                        "Password Required": "Yes",
                        "Workstations Allowed": "All"
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
                        elif 'password required' in detail_line_lower:
                            user_data["Password Required"] = detail_line.split('Password required')[1].strip()

                    users_info.append(user_data)

                except Exception:
                    continue

            print_status(f"Collected details for {len(users_info)} users", "SUCCESS")

        except Exception as e:
            print_status(f"User information collection failed: {str(e)}", "ERROR")

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

def get_system_performance():
    print_status("Analyzing system performance...", "SYSTEM")
    performance = []

    try:
        # CPU Information
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()

        # Memory Information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk Information
        disk_io = psutil.disk_io_counters()

        # Network Information
        net_io = psutil.net_io_counters()

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

    return performance


def get_advanced_system_details():
    print_status("Collecting advanced system details...", "SYSTEM")
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

        print_status("Advanced system details collected", "SUCCESS")

    except Exception as e:
        print_status(f"Advanced details collection failed: {str(e)}", "ERROR")

    return advanced_info


# -------------------------------------------------------------------
#  HTML REPORT GENERATION WITH ENHANCED FEATURES
# -------------------------------------------------------------------
def generate_html_report():
    global html_file_opened

    print_banner()
    print_scan_header()
    print_system_stats()
    print_scanning_animation()

    downloads = get_downloads_folder()
    html_path = os.path.join(downloads, f"SYSTEM_SCAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    # Collect all data with progress indication
    sections_data = {}
    data_collectors = [
        ("SYSTEM OVERVIEW", get_device_specifications),
        ("STORAGE ANALYSIS", get_advanced_storage_details),
        ("GRAPHICS CARD INFORMATION", get_comprehensive_graphics_info),
        ("NETWORK ANALYSIS", get_network_analysis),
        ("WIFI SECURITY ANALYSIS", get_comprehensive_wifi_analysis),
        ("USER ACCOUNTS", get_users_information),
        ("ADVANCED SYSTEM DETAILS", get_advanced_system_details),
        ("SYSTEM PERFORMANCE", get_system_performance),
        ("PROCESS TREE", get_process_tree),
        ("RUNNING SERVICES", get_running_services),
        ("TASK MANAGER - RUNNING PROCESSES", get_enhanced_task_manager_details)
    ]

    print_status("Starting comprehensive data collection...", "SCAN")

    for i, (section_name, collector_func) in enumerate(data_collectors):
        progress_bar(i, len(data_collectors), prefix='Collecting Data', suffix=f'{section_name}')
        sections_data[section_name] = collector_func()
        time.sleep(0.5)  # Small delay for better UX

    progress_bar(len(data_collectors), len(data_collectors), prefix='Collecting Data', suffix='Complete!')
    print()

    print_status("Compiling HTML report...", "SCAN")

    health_score = get_system_health_score()
    health_color = get_health_color(health_score)

    # Enhanced HTML content with better Task Manager section
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SYSTEM SCAN REPORT - SABARI425</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            :root {{
                --primary-color: #00ff00;
                --secondary-color: #00cc00;
                --background-color: #000000;
                --card-background: rgba(0, 20, 0, 0.8);
                --border-color: #003300;
                --text-color: #00ff00;
                --text-secondary: #00cc00;
                --warning-color: #ffff00;
                --danger-color: #ff0000;
            }}

            body {{
                font-family: 'JetBrains Mono', monospace;
                background: var(--background-color);
                min-height: 100vh;
                margin: 0;
                padding: 0;
                color: var(--text-color);
                line-height: 1.4;
                overflow-x: hidden;
            }}

            .matrix-bg {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(0, 255, 0, 0.02) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(0, 255, 0, 0.02) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(0, 255, 0, 0.01) 0%, transparent 50%);
                pointer-events: none;
                z-index: -1;
            }}

            .scan-line {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
                animation: scan 3s linear infinite;
                box-shadow: 0 0 10px var(--primary-color);
                z-index: 1000;
            }}

            @keyframes scan {{
                0% {{ top: 0%; opacity: 0; }}
                50% {{ opacity: 1; }}
                100% {{ top: 100%; opacity: 0; }}
            }}

            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                position: relative;
            }}

            .header {{
                background: var(--card-background);
                padding: 25px;
                margin-bottom: 25px;
                text-align: center;
                border: 1px solid var(--primary-color);
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.1), transparent);
                animation: headerGlow 3s linear infinite;
            }}

            @keyframes headerGlow {{
                0% {{ left: -100%; }}
                100% {{ left: 100%; }}
            }}

            .header h1 {{
                color: var(--primary-color);
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
                text-shadow: 0 0 10px var(--primary-color);
                letter-spacing: 2px;
            }}

            .creator {{
                color: var(--warning-color);
                font-size: 1.2em;
                margin-bottom: 15px;
                font-weight: 500;
            }}

            .header p {{
                color: var(--text-secondary);
                font-size: 0.9em;
                margin: 3px 0;
                font-weight: 300;
            }}

            .health-score {{
                display: inline-block;
                background: {health_color};
                color: #000000;
                padding: 8px 20px;
                margin-top: 10px;
                font-weight: 600;
                border: 1px solid var(--primary-color);
                text-shadow: 0 0 5px #000000;
                border-radius: 3px;
            }}

            .section {{
                background: var(--card-background);
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid var(--border-color);
                position: relative;
                transition: all 0.3s ease;
            }}

            .section::before {{
                content: '>';
                position: absolute;
                left: 10px;
                top: 20px;
                color: var(--primary-color);
                font-weight: bold;
            }}

            .section:hover {{
                border-color: var(--primary-color);
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
            }}

            .section h2 {{
                color: var(--primary-color);
                padding-bottom: 10px;
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 500;
                border-bottom: 1px solid var(--border-color);
                margin-left: 15px;
            }}

            /* Scrollable table containers */
            .table-container {{
                overflow-x: auto;
                margin: 15px 0;
                border: 1px solid var(--border-color);
                background: rgba(0, 5, 0, 0.5);
                position: relative;
            }}

            .wide-table {{
                min-width: 1200px;
            }}

            .extra-wide-table {{
                min-width: 1800px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.85em;
            }}

            th {{
                background: rgba(0, 30, 0, 0.8);
                color: var(--primary-color);
                padding: 12px 10px;
                text-align: left;
                font-weight: 500;
                border: 1px solid var(--border-color);
                text-transform: uppercase;
                letter-spacing: 1px;
                position: sticky;
                left: 0;
                cursor: pointer;
            }}

            th:hover {{
                background: rgba(0, 50, 0, 0.8);
            }}

            td {{
                padding: 10px 10px;
                border: 1px solid var(--border-color);
                color: var(--text-secondary);
                font-weight: 300;
            }}

            tr:nth-child(even) {{
                background: rgba(0, 15, 0, 0.3);
            }}

            tr:hover {{
                background: rgba(0, 255, 0, 0.1);
                color: var(--primary-color);
            }}

            .status-active {{
                color: var(--primary-color);
                font-weight: 600;
                text-shadow: 0 0 5px var(--primary-color);
            }}

            .status-inactive {{
                color: var(--danger-color);
                font-weight: 600;
            }}

            .status-warning {{
                color: var(--warning-color);
                font-weight: 600;
            }}

            .risk-high {{
                background: rgba(255, 0, 0, 0.2);
                color: var(--danger-color);
                font-weight: 600;
            }}

            .risk-medium {{
                background: rgba(255, 255, 0, 0.1);
                color: var(--warning-color);
                font-weight: 600;
            }}

            .risk-low {{
                background: rgba(0, 255, 0, 0.1);
                color: var(--primary-color);
            }}

            .metric-value {{
                font-family: 'JetBrains Mono', monospace;
                background: rgba(0, 255, 0, 0.1);
                padding: 3px 6px;
                color: var(--primary-color);
                border: 1px solid var(--border-color);
                font-weight: 400;
            }}

            .footer {{
                text-align: center;
                color: var(--text-secondary);
                margin-top: 30px;
                padding: 20px;
                background: var(--card-background);
                border: 1px solid var(--border-color);
                font-size: 0.8em;
            }}

            .performance-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}

            .performance-card {{
                background: rgba(0, 20, 0, 0.6);
                padding: 15px;
                border: 1px solid var(--border-color);
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
            }}

            .performance-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 3px;
                height: 100%;
                background: var(--primary-color);
            }}

            .performance-card:hover {{
                border-color: var(--primary-color);
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
                transform: translateY(-2px);
            }}

            .performance-card h3 {{
                color: var(--primary-color);
                margin-bottom: 8px;
                font-size: 0.9em;
                font-weight: 500;
            }}

            .performance-value {{
                font-size: 1.5em;
                font-weight: 600;
                color: var(--primary-color);
                margin: 8px 0;
                text-shadow: 0 0 5px var(--primary-color);
            }}

            .performance-details {{
                color: var(--text-secondary);
                font-size: 0.8em;
            }}

            .terminal-prompt {{
                color: var(--primary-color);
                margin-right: 5px;
            }}

            .blink {{
                animation: blink 1s infinite;
            }}

            @keyframes blink {{
                0%, 50% {{ opacity: 1; }}
                51%, 100% {{ opacity: 0; }}
            }}

            /* Matrix rain effect */
            .matrix-rain {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: -2;
                opacity: 0.1;
            }}

            /* Custom scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}

            ::-webkit-scrollbar-track {{
                background: rgba(0, 10, 0, 0.8);
            }}

            ::-webkit-scrollbar-thumb {{
                background: var(--primary-color);
                border-radius: 0;
            }}

            ::-webkit-scrollbar-thumb:hover {{
                background: var(--secondary-color);
            }}

            /* Typewriter effect for headers */
            .typewriter {{
                overflow: hidden;
                border-right: 2px solid var(--primary-color);
                white-space: nowrap;
                animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
            }}

            @keyframes typing {{
                from {{ width: 0 }}
                to {{ width: 100% }}
            }}

            @keyframes blink-caret {{
                from, to {{ border-color: transparent }}
                50% {{ border-color: var(--primary-color) }}
            }}

            /* Mobile responsiveness */
            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}

                .header h1 {{
                    font-size: 1.8em;
                }}

                .performance-grid {{
                    grid-template-columns: 1fr;
                }}

                .section {{
                    padding: 15px 10px;
                }}

                .section h2 {{
                    font-size: 1.1em;
                    margin-left: 20px;
                }}

                .section::before {{
                    left: 5px;
                    top: 15px;
                }}

                .table-container {{
                    margin: 10px -10px;
                }}

                table {{
                    font-size: 0.75em;
                }}

                th, td {{
                    padding: 8px 6px;
                }}

                .wide-table, .extra-wide-table {{
                    min-width: 800px;
                }}
            }}

            @media (max-width: 480px) {{
                .header {{
                    padding: 15px;
                }}

                .header h1 {{
                    font-size: 1.5em;
                }}

                .health-score {{
                    font-size: 0.9em;
                    padding: 6px 15px;
                }}

                .performance-value {{
                    font-size: 1.2em;
                }}
            }}

            /* Real-time data pulsing effect */
            .pulse {{
                animation: pulse 2s infinite;
            }}

            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
                100% {{ opacity: 1; }}
            }}

            /* Process risk indicators */
            .risk-indicator {{
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 5px;
            }}

            .risk-high-indicator {{
                background: var(--danger-color);
                box-shadow: 0 0 5px var(--danger-color);
            }}

            .risk-medium-indicator {{
                background: var(--warning-color);
                box-shadow: 0 0 5px var(--warning-color);
            }}

            .risk-low-indicator {{
                background: var(--primary-color);
                box-shadow: 0 0 5px var(--primary-color);
            }}

            /* Search and filter controls */
            .controls {{
                margin: 10px 0;
                padding: 10px;
                background: rgba(0, 15, 0, 0.5);
                border: 1px solid var(--border-color);
            }}

            .search-box {{
                background: rgba(0, 5, 0, 0.8);
                border: 1px solid var(--border-color);
                color: var(--primary-color);
                padding: 8px;
                font-family: 'JetBrains Mono', monospace;
                width: 300px;
                margin-right: 10px;
            }}

            .filter-btn {{
                background: rgba(0, 30, 0, 0.8);
                border: 1px solid var(--border-color);
                color: var(--primary-color);
                padding: 8px 15px;
                font-family: 'JetBrains Mono', monospace;
                cursor: pointer;
                margin-right: 5px;
            }}

            .filter-btn:hover {{
                background: rgba(0, 50, 0, 0.8);
                border-color: var(--primary-color);
            }}

            .filter-btn.active {{
                background: rgba(0, 255, 0, 0.2);
                border-color: var(--primary-color);
            }}
        </style>
    </head>
    <body>
        <div class="matrix-bg"></div>
        <div class="scan-line"></div>
        <div class="matrix-rain" id="matrixRain"></div>

        <div class="container">
            <div class="header">
                <div class="creator">CREATED BY: SABARI425</div>
                <h1>><span class="blink">_</span> ADVANCED SYSTEM SCAN REPORT</h1>
                <p>> SCAN INITIATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>> TARGET: {socket.gethostname()} | PLATFORM: {platform.platform()}</p>
                <div class="health-score pulse">
                    SYSTEM_INTEGRITY: {health_score}/100
                </div>
            </div>
    """

    # Add each section to HTML
    for section_name, data in sections_data.items():
        html_content += f"""
            <div class="section">
                <h2 class="typewriter">> {section_name}</h2>
        """

        if data:
            if section_name in ["TASK MANAGER - RUNNING PROCESSES"]:
                # Enhanced Task Manager with search and filtering
                html_content += f'''
                <div class="controls">
                    <input type="text" id="processSearch" class="search-box" placeholder="Search processes..." onkeyup="searchProcesses()">
                    <button class="filter-btn" onclick="filterByRisk('all')">All</button>
                    <button class="filter-btn" onclick="filterByRisk('high')">High Risk</button>
                    <button class="filter-btn" onclick="filterByRisk('medium')">Medium Risk</button>
                    <button class="filter-btn" onclick="filterByRisk('low')">Low Risk</button>
                    <button class="filter-btn" onclick="sortByCPU()">Sort by CPU</button>
                    <button class="filter-btn" onclick="sortByMemory()">Sort by Memory</button>
                </div>
                <div class="table-container">
                    <table class="extra-wide-table" id="processTable">
                '''
            elif section_name in ["NETWORK ANALYSIS", "WIFI SECURITY ANALYSIS", "USER ACCOUNTS"]:
                html_content += f'<div class="table-container"><table class="wide-table">'
            elif section_name == "SYSTEM PERFORMANCE":
                html_content += '<div class="performance-grid">'
                for item in data:
                    html_content += f'''
                    <div class="performance-card">
                        <h3>> {item["Metric"]}</h3>
                        <div class="performance-value">{item["Value"]}</div>
                        <div class="performance-details">>{item["Details"]}</div>
                    </div>
                    '''
                html_content += '</div>'
            else:
                html_content += '<table>'

            if section_name != "SYSTEM PERFORMANCE":
                if isinstance(data[0], dict):
                    # Table data
                    headers = list(data[0].keys())
                    rows = [[row.get(header, '') for header in headers] for row in data]

                    html_content += '<thead><tr>' + ''.join(
                        f'<th>{header}</th>' for header in headers) + '</tr></thead>'
                    html_content += '<tbody>'
                    for row in rows:
                        row_html = '<tr>'
                        for i, cell in enumerate(row):
                            cell_str = str(cell)
                            # Enhanced risk level coloring for Task Manager
                            if section_name == "TASK MANAGER - RUNNING PROCESSES" and headers[i] == "Risk Level":
                                if cell_str == "HIGH":
                                    row_html += f'<td class="risk-high"><span class="risk-indicator risk-high-indicator"></span>{cell}</td>'
                                elif cell_str == "MEDIUM":
                                    row_html += f'<td class="risk-medium"><span class="risk-indicator risk-medium-indicator"></span>{cell}</td>'
                                else:
                                    row_html += f'<td class="risk-low"><span class="risk-indicator risk-low-indicator"></span>{cell}</td>'
                            elif headers[i] in ["Status", "Account Active", "Health"]:
                                if any(x in cell_str.lower() for x in
                                       ["active", "yes", "healthy", "connected", "running"]):
                                    row_html += f'<td class="status-active">{cell}</td>'
                                elif any(x in cell_str.lower() for x in
                                         ["inactive", "no", "error", "disconnected", "stopped"]):
                                    row_html += f'<td class="status-inactive">{cell}</td>'
                                elif any(x in cell_str.lower() for x in ["warning", "caution"]):
                                    row_html += f'<td class="status-warning">{cell}</td>'
                                else:
                                    row_html += f'<td>{cell}</td>'
                            elif "password" in headers[i].lower() and cell_str != "Not stored or encrypted":
                                row_html += f'<td class="status-active">{cell}</td>'
                            else:
                                row_html += f'<td>{cell}</td>'
                        row_html += '</tr>'
                        html_content += row_html
                    html_content += '</tbody></table>'
                else:
                    # Key-value data
                    for item in data:
                        if len(item) == 2:
                            html_content += f'<tr><td><span class="terminal-prompt">></span> {item[0]}</td><td class="metric-value">{item[1]}</td></tr>'
                    html_content += '</table>'

            if section_name in ["TASK MANAGER - RUNNING PROCESSES", "NETWORK ANALYSIS", "WIFI SECURITY ANALYSIS",
                                "USER ACCOUNTS"]:
                html_content += '</div>'
        else:
            html_content += '<p style="color: #006600; text-align: center; padding: 20px;">> NO_DATA_AVAILABLE</p>'

        html_content += '</div>'

    html_content += """
            <div class="footer">
                <p>> SCAN_COMPLETED: """ + datetime.now().strftime('%H:%M:%S') + """</p>
                <p>> SYSTEM_SCAN_V3.0 | CREATED BY: SABARI425 | SECURITY_LEVEL: MAXIMUM</p>
            </div>
        </div>

        <script>
            // Matrix rain effect
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.classList.add('matrix-rain');
            document.getElementById('matrixRain').appendChild(canvas);

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const chars = "01";
            const charSize = 14;
            const columns = canvas.width / charSize;
            const drops = [];

            for (let i = 0; i < columns; i++) {
                drops[i] = 1;
            }

            function drawMatrix() {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#00ff00';
                ctx.font = charSize + 'px JetBrains Mono';

                for (let i = 0; i < drops.length; i++) {
                    const text = chars[Math.floor(Math.random() * chars.length)];
                    ctx.fillText(text, i * charSize, drops[i] * charSize);

                    if (drops[i] * charSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }

            setInterval(drawMatrix, 35);

            // Enhanced Task Manager functionality
            function searchProcesses() {
                const input = document.getElementById('processSearch');
                const filter = input.value.toLowerCase();
                const table = document.getElementById('processTable');
                const tr = table.getElementsByTagName('tr');

                for (let i = 1; i < tr.length; i++) {
                    const td = tr[i].getElementsByTagName('td');
                    let found = false;
                    for (let j = 0; j < td.length; j++) {
                        if (td[j]) {
                            const txtValue = td[j].textContent || td[j].innerText;
                            if (txtValue.toLowerCase().indexOf(filter) > -1) {
                                found = true;
                                break;
                            }
                        }
                    }
                    tr[i].style.display = found ? '' : 'none';
                }
            }

            function filterByRisk(riskLevel) {
                const table = document.getElementById('processTable');
                const tr = table.getElementsByTagName('tr');
                const riskColumn = 16; // Risk Level column index

                for (let i = 1; i < tr.length; i++) {
                    const td = tr[i].getElementsByTagName('td')[riskColumn];
                    if (td) {
                        const riskValue = td.textContent.toLowerCase();
                        if (riskLevel === 'all' || riskValue.includes(riskLevel)) {
                            tr[i].style.display = '';
                        } else {
                            tr[i].style.display = 'none';
                        }
                    }
                }

                // Update active button
                const buttons = document.querySelectorAll('.filter-btn');
                buttons.forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
            }

            function sortByCPU() {
                sortTable(document.getElementById('processTable'), 3, true); // CPU% column
            }

            function sortByMemory() {
                sortTable(document.getElementById('processTable'), 4, true); // Memory% column
            }

            function sortTable(table, column, isNumeric) {
                const tbody = table.querySelector('tbody');
                if (!tbody) return;

                const rows = Array.from(tbody.querySelectorAll('tr'));
                let direction = table.getAttribute('data-sort-direction') === 'asc' ? 'desc' : 'asc';
                table.setAttribute('data-sort-direction', direction);

                rows.sort((a, b) => {
                    let aText = a.cells[column].textContent.trim();
                    let bText = b.cells[column].textContent.trim();

                    if (isNumeric) {
                        aText = parseFloat(aText.replace('%', '')) || 0;
                        bText = parseFloat(bText.replace('%', '')) || 0;
                    }

                    if (direction === 'asc') {
                        return aText > bText ? 1 : -1;
                    } else {
                        return aText < bText ? 1 : -1;
                    }
                });

                // Remove existing rows
                rows.forEach(row => tbody.removeChild(row));

                // Add sorted rows with animation
                rows.forEach((row, index) => {
                    row.style.opacity = '0';
                    row.style.transform = 'translateY(-20px)';
                    tbody.appendChild(row);

                    setTimeout(() => {
                        row.style.transition = 'all 0.3s ease';
                        row.style.opacity = '1';
                        row.style.transform = 'translateY(0)';
                    }, index * 20);
                });
            }

            // Enhanced interactive features
            document.addEventListener('DOMContentLoaded', function() {
                // Add real-time data updates simulation
                const updateData = () => {
                    const healthScore = document.querySelector('.health-score');
                    if (healthScore) {
                        healthScore.classList.add('pulse');
                        setTimeout(() => {
                            healthScore.classList.remove('pulse');
                        }, 2000);
                    }
                };

                // Update data every 10 seconds
                setInterval(updateData, 10000);

                // Add table sorting with visual feedback
                const tables = document.querySelectorAll('table');
                tables.forEach(table => {
                    const headers = table.querySelectorAll('th');
                    headers.forEach((header, index) => {
                        header.style.cursor = 'pointer';
                        header.title = 'Click to sort';

                        header.addEventListener('click', () => {
                            // Visual feedback
                            header.style.background = 'rgba(0, 255, 0, 0.3)';
                            setTimeout(() => {
                                header.style.background = '';
                            }, 500);

                            const isNumeric = header.textContent.includes('%') || 
                                            header.textContent.includes('MB') ||
                                            header.textContent.includes('GB');
                            sortTable(table, index, isNumeric);
                        });
                    });
                });

                // Add hover effects to performance cards
                const performanceCards = document.querySelectorAll('.performance-card');
                performanceCards.forEach(card => {
                    card.addEventListener('mouseenter', () => {
                        card.style.transform = 'translateY(-5px) scale(1.02)';
                    });

                    card.addEventListener('mouseleave', () => {
                        card.style.transform = 'translateY(0) scale(1)';
                    });
                });

                // Add scroll progress indicator
                const createScrollProgress = () => {
                    const progress = document.createElement('div');
                    progress.style.position = 'fixed';
                    progress.style.top = '0';
                    progress.style.left = '0';
                    progress.style.height = '2px';
                    progress.style.background = 'linear-gradient(90deg, #00ff00, #00cc00)';
                    progress.style.zIndex = '1001';
                    progress.style.width = '0%';
                    progress.style.transition = 'width 0.1s ease';
                    document.body.appendChild(progress);

                    window.addEventListener('scroll', () => {
                        const winHeight = window.innerHeight;
                        const docHeight = document.documentElement.scrollHeight;
                        const scrollTop = window.pageYOffset;
                        const scrollPercent = (scrollTop / (docHeight - winHeight)) * 100;
                        progress.style.width = scrollPercent + '%';
                    });
                };

                createScrollProgress();

                // Add section navigation
                const sections = document.querySelectorAll('.section');
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.style.animation = 'pulse 0.5s ease';
                            setTimeout(() => {
                                entry.target.style.animation = '';
                            }, 500);
                        }
                    });
                }, { threshold: 0.3 });

                sections.forEach(section => {
                    observer.observe(section);
                });
            });

            // Handle window resize
            window.addEventListener('resize', function() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            });

            // Add keyboard navigation
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Home') {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                } else if (e.key === 'End') {
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }
            });
        </script>
    </body>
    </html>
    """

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print_status("HTML report generated successfully!", "SUCCESS")
    print_status(f"Location: {html_path}", "INFO")

    # Open HTML file only once
    if not html_file_opened:
        print_status("Opening in default browser...", "INFO")
        try:
            webbrowser.open(f'file://{html_path}')
            html_file_opened = True
        except Exception as e:
            print_status(f"Could not open browser automatically: {str(e)}", "WARNING")
    else:
        print_status("Report ready - file already opened in browser", "INFO")

    return html_path


# -------------------------------------------------------------------
#  MAIN EXECUTION
# -------------------------------------------------------------------
def main():
    try:
        print_banner()
        print_status("INITIATING COMPREHENSIVE SYSTEM SCAN...", "SCAN")
        print_status("GATHERING INTELLIGENCE DATA...", "INFO")
        print_status("THIS MAY TAKE A FEW MOMENTS...", "INFO")
        print()

        # Show system stats before scan
        print_system_stats()
        time.sleep(2)

        html_path = generate_html_report()

        print()
        print_status("SCAN COMPLETED SUCCESSFULLY!", "SUCCESS")
        print_status("REPORT SECTIONS INCLUDED:", "INFO")
        sections = [
            "SYSTEM OVERVIEW", "STORAGE ANALYSIS", "GRAPHICS CARD INFORMATION",
            "NETWORK ANALYSIS", "WIFI SECURITY ANALYSIS", "USER ACCOUNTS",
            "ADVANCED SYSTEM DETAILS", "SYSTEM PERFORMANCE METRICS",
            "PROCESS TREE", "RUNNING SERVICES", "ENHANCED TASK MANAGER"
        ]

        for section in sections:
            print(f"    {Colors.GREEN}> {section}{Colors.RESET}")

        print()
        print_status("ADVANCED FEATURES ENABLED:", "DATA")
        features = [
            "Real-time Process Risk Analysis",
            "Advanced Task Manager with Search & Filter",
            "Process Tree Visualization",
            "Service Monitoring",
            "Network Security Analysis",
            "System Health Scoring",
            "Interactive HTML Report"
        ]

        for feature in features:
            print(f"    {Colors.CYAN}✓ {feature}{Colors.RESET}")

        print()
        print_status("SECURITY NOTICE: All data collected for security analysis purposes", "WARNING")
        print_status(f"Report saved to: {html_path}", "INFO")

    except Exception as e:
        print_status(f"ERROR GENERATING REPORT: {str(e)}", "ERROR")
        print_status("Please ensure you have necessary permissions", "WARNING")


if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)
    main()