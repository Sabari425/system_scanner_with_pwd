import os
import sys
import subprocess
import platform
from datetime import datetime
import socket
import uuid
import re
import json
import time
import threading
from collections import OrderedDict


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
#  ENHANCED COMMAND EXECUTOR WITH CACHING
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
        start_time = time.time()
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL, timeout=30)
        execution_time = time.time() - start_time

        monitor.log_performance(f"CMD_EXEC_{cmd[:20]}", execution_time)

        if use_cache:
            command_cache[cache_key] = (datetime.now(), output)

        return output.strip()
    except subprocess.TimeoutExpired:
        monitor.log_security_event("COMMAND_TIMEOUT", f"Command timed out: {cmd}")
        return "Command execution timeout"
    except Exception as e:
        return f"Command failed: {str(e)}"


# -------------------------------------------------------------------
#  ADVANCED SYSTEM INFORMATION GATHERING
# -------------------------------------------------------------------
def get_system_health_score():
    """Calculate overall system health score"""
    score = 100

    # CPU usage penalty
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > 80:
        score -= 20
    elif cpu_usage > 60:
        score -= 10

    # Memory usage penalty
    memory = psutil.virtual_memory()
    if memory.percent > 85:
        score -= 20
    elif memory.percent > 70:
        score -= 10

    # Disk usage penalty
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            if usage.percent > 90:
                score -= 15
            elif usage.percent > 80:
                score -= 8
        except:
            continue

    return max(score, 0)


def get_device_specifications():
    info = OrderedDict()

    # Basic system information
    info["Device Name"] = socket.gethostname()
    info["Processor"] = platform.processor()
    info["Platform"] = platform.platform()
    info["Architecture"] = platform.architecture()[0]
    info["System Type"] = platform.machine()
    info["Python Version"] = platform.python_version()

    # Advanced CPU information
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            info["CPU Max Frequency"] = f"{cpu_freq.max:.2f} MHz"
            info["CPU Current Frequency"] = f"{cpu_freq.current:.2f} MHz"
            info["CPU Min Frequency"] = f"{cpu_freq.min:.2f} MHz"

        info["CPU Cores (Physical)"] = psutil.cpu_count(logical=False)
        info["CPU Cores (Logical)"] = psutil.cpu_count(logical=True)
        info["CPU Usage Current"] = f"{psutil.cpu_percent(interval=0.5)}%"

        # CPU load averages
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
        info["CPU Load 1min"] = f"{load_avg[0]:.2f}"
        info["CPU Load 5min"] = f"{load_avg[1]:.2f}"
        info["CPU Load 15min"] = f"{load_avg[2]:.2f}"

    except:
        pass

    # RAM information
    memory = psutil.virtual_memory()
    info["Installed RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"
    info["Available RAM"] = f"{memory.available / (1024 ** 3):.2f} GB"
    info["RAM Usage"] = f"{memory.percent}%"
    info["RAM Used"] = f"{memory.used / (1024 ** 3):.2f} GB"
    info["RAM Free"] = f"{memory.free / (1024 ** 3):.2f} GB"
    info["RAM Cached"] = f"{getattr(memory, 'cached', 0) / (1024 ** 3):.2f} GB" if hasattr(memory, 'cached') else "N/A"

    # Swap memory
    swap = psutil.swap_memory()
    info["Swap Total"] = f"{swap.total / (1024 ** 3):.2f} GB"
    info["Swap Used"] = f"{swap.used / (1024 ** 3):.2f} GB"
    info["Swap Free"] = f"{swap.free / (1024 ** 3):.2f} GB"
    info["Swap Usage"] = f"{swap.percent}%"

    # System uptime
    boot_time = psutil.boot_time()
    uptime = datetime.now() - datetime.fromtimestamp(boot_time)
    info["System Uptime"] = str(uptime).split('.')[0]
    info["Last Boot"] = datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')

    # System Health
    info["System Health Score"] = f"{get_system_health_score()}/100"

    # Windows-specific info
    if platform.system() == "Windows":
        try:
            result = run_cmd("systeminfo", use_cache=True)
            lines = result.split('\n')
            for line in lines:
                if 'OS Name:' in line:
                    info["Edition"] = line.split(':', 1)[1].strip()
                elif 'OS Version:' in line:
                    info["Version"] = line.split(':', 1)[1].strip()
                elif 'Original Install Date:' in line:
                    info["Installed on"] = line.split(':', 1)[1].strip()
                elif 'System Manufacturer:' in line:
                    info["Manufacturer"] = line.split(':', 1)[1].strip()
                elif 'System Model:' in line:
                    info["Model"] = line.split(':', 1)[1].strip()
                elif 'System Type:' in line:
                    info["Architecture Type"] = line.split(':', 1)[1].strip()
                elif 'Total Physical Memory:' in line:
                    info["Physical Memory"] = line.split(':', 1)[1].strip()
        except:
            pass

    return [[k, v] for k, v in info.items()]


def get_advanced_storage_details():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_io = psutil.disk_io_counters(perdisk=True).get(part.device.replace('\\', '').replace(':', ''), None)

            disk_info = {
                "Device": part.device,
                "Mountpoint": part.mountpoint,
                "File System": part.fstype,
                "Total Size (GB)": f"{usage.total / (1024 ** 3):.2f}",
                "Used (GB)": f"{usage.used / (1024 ** 3):.2f}",
                "Free (GB)": f"{usage.free / (1024 ** 3):.2f}",
                "Usage (%)": f"{usage.percent}%",
                "Status": "Healthy" if usage.percent < 90 else "Warning"
            }

            if disk_io:
                disk_info["Read Bytes (GB)"] = f"{disk_io.read_bytes / (1024 ** 3):.2f}"
                disk_info["Write Bytes (GB)"] = f"{disk_io.write_bytes / (1024 ** 3):.2f}"
                disk_info["Read Count"] = f"{disk_io.read_count:,}"
                disk_info["Write Count"] = f"{disk_io.write_count:,}"
                disk_info["Read Time (ms)"] = f"{disk_io.read_time}"
                disk_info["Write Time (ms)"] = f"{disk_io.write_time}"

            disks.append(disk_info)
        except PermissionError:
            continue
        except Exception as e:
            disks.append({
                "Device": part.device,
                "Mountpoint": part.mountpoint,
                "Error": str(e)
            })

    return disks


def get_comprehensive_graphics_info():
    gpu_info = []

    # Primary method: WMI for Windows
    if platform.system() == "Windows":
        try:
            output = run_cmd(
                "wmic path win32_videocontroller get name, adapterram, driverversion, videoprocessor, videomodedescription, videomemorytype, availability, status /format:table")
            if output and "No Instance(s) Available" not in output:
                lines = output.split('\n')
                for line in lines[1:]:
                    if line.strip() and not line.startswith('Name'):
                        parts = [p for p in line.split('  ') if p.strip()]
                        if len(parts) >= 3:
                            gpu_info.append({
                                "Graphics Card": parts[0].strip(),
                                "Adapter RAM (GB)": f"{int(parts[1]) / (1024 ** 3):.2f}" if parts[
                                    1].strip().isdigit() else "Unknown",
                                "Driver Version": parts[2].strip() if len(parts) > 2 else "Unknown",
                                "Video Processor": parts[3].strip() if len(parts) > 3 else "Unknown",
                                "Resolution": parts[4].strip() if len(parts) > 4 else "Unknown",
                                "Memory Type": parts[5].strip() if len(parts) > 5 else "Unknown",
                                "Availability": parts[6].strip() if len(parts) > 6 else "Unknown",
                                "Status": parts[7].strip() if len(parts) > 7 else "Unknown"
                            })
        except Exception as e:
            monitor.log_security_event("GPU_INFO_ERROR", f"Failed to get GPU info: {str(e)}")

    # Fallback method
    if not gpu_info:
        try:
            output = run_cmd("wmic path win32_videocontroller get name, adapterram, driverversion")
            if output and "No Instance(s) Available" not in output:
                lines = output.split('\n')[1:]
                for line in lines:
                    if line.strip():
                        parts = [p.strip() for p in line.split('  ') if p.strip()]
                        if len(parts) >= 1:
                            gpu_info.append({
                                "Graphics Card": parts[0],
                                "Adapter RAM": f"{int(parts[1]) / (1024 ** 3):.2f} GB" if len(parts) > 1 and parts[
                                    1].isdigit() else "Unknown",
                                "Driver Version": parts[2] if len(parts) > 2 else "Unknown"
                            })
        except:
            pass

    if not gpu_info:
        gpu_info.append({
            "Graphics Card": "No GPU information available",
            "Status": "Check system configuration"
        })

    return gpu_info


def get_network_analysis():
    net_info = []
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)

    for interface_name, interface_addresses in interfaces.items():
        if interface_name in stats:
            stat = stats[interface_name]
            io = io_counters.get(interface_name, None)

            interface_data = {
                "Interface": interface_name,
                "Status": "ACTIVE" if stat.isup else "INACTIVE",
                "MTU": stat.mtu,
                "Speed (Mbps)": f"{stat.speed}" if stat.speed > 0 else "UNKNOWN",
                "Duplex": "FULL" if stat.duplex == 2 else "HALF" if stat.duplex == 1 else "UNKNOWN",
                "Flags": stat.flags if hasattr(stat, 'flags') else "N/A"
            }

            # MAC Address
            mac_address = "NONE"
            for addr in interface_addresses:
                if addr.family == -1:  # MAC
                    mac_address = addr.address
                    break
            interface_data["MAC Address"] = mac_address

            # IP Addresses with types
            ipv4_addrs = []
            ipv6_addrs = []
            dns_servers = []

            for addr in interface_addresses:
                if addr.family == 2:  # IPv4
                    ipv4_addrs.append(f"{addr.address}/{addr.netmask}")
                elif addr.family == 23:  # IPv6
                    ipv6_addrs.append(addr.address)
                elif addr.family == 30:  # DNS
                    dns_servers.append(addr.address)

            interface_data["IPv4 Addresses"] = "\n".join(ipv4_addrs) if ipv4_addrs else "NONE"
            interface_data["IPv6 Addresses"] = "\n".join(ipv6_addrs) if ipv6_addrs else "NONE"
            interface_data["DNS Servers"] = "\n".join(dns_servers) if dns_servers else "NONE"

            # I/O Statistics
            if io:
                interface_data["Data Received"] = f"{io.bytes_recv / (1024 ** 2):.2f} MB"
                interface_data["Data Sent"] = f"{io.bytes_sent / (1024 ** 2):.2f} MB"
                interface_data["Packets Received"] = f"{io.packets_recv:,}"
                interface_data["Packets Sent"] = f"{io.packets_sent:,}"
                interface_data["Errors In"] = f"{io.errin}"
                interface_data["Errors Out"] = f"{io.errout}"
                interface_data["Drop In"] = f"{io.dropin}"
                interface_data["Drop Out"] = f"{io.dropout}"
            else:
                interface_data["Data Received"] = "N/A"
                interface_data["Data Sent"] = "N/A"
                interface_data["Packets Received"] = "N/A"
                interface_data["Packets Sent"] = "N/A"

            net_info.append(interface_data)

    return net_info


def display_network_analysis_with_scroll():
    """Display network analysis with horizontal scrolling capability"""
    net_info = get_network_analysis()

    if not net_info:
        print(f"{Fore.YELLOW}No network interfaces found{Style.RESET_ALL}")
        return

    # Convert to list of lists for tabulate
    table_data = []
    for interface in net_info:
        row = [
            interface.get("Interface", "N/A"),
            interface.get("Status", "N/A"),
            interface.get("MAC Address", "N/A"),
            interface.get("IPv4 Addresses", "N/A"),
            interface.get("IPv6 Addresses", "N/A"),
            interface.get("MTU", "N/A"),
            interface.get("Speed (Mbps)", "N/A"),
            interface.get("Duplex", "N/A"),
            interface.get("Data Received", "N/A"),
            interface.get("Data Sent", "N/A"),
            interface.get("Packets Received", "N/A"),
            interface.get("Packets Sent", "N/A"),
            interface.get("Errors In", "N/A"),
            interface.get("Errors Out", "N/A"),
            interface.get("DNS Servers", "N/A")
        ]
        table_data.append(row)

    headers = [
        "Interface", "Status", "MAC Address", "IPv4 Addresses",
        "IPv6 Addresses", "MTU", "Speed", "Duplex", "Data Recv",
        "Data Sent", "Pkts Recv", "Pkts Sent", "Err In", "Err Out", "DNS"
    ]

    print(f"{Fore.CYAN}Network Analysis - Scroll horizontally to view all columns{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Use horizontal scroll or adjust terminal width to see all data{Style.RESET_ALL}")
    print()

    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt="simple", numalign="left", stralign="left"))

    # Summary statistics
    active_interfaces = sum(1 for interface in net_info if interface.get("Status") == "ACTIVE")
    total_interfaces = len(net_info)

    print(
        f"\n{Fore.GREEN}Summary: {active_interfaces} active interfaces out of {total_interfaces} total{Style.RESET_ALL}")


def get_advanced_network_properties():
    detailed_info = []

    try:
        # Network connectivity tests
        connectivity_tests = [
            ("Google DNS", "8.8.8.8"),
            ("Cloudflare DNS", "1.1.1.1"),
            ("Local Gateway", "192.168.1.1"),
            ("Router", "192.168.0.1")
        ]

        for name, host in connectivity_tests:
            try:
                socket.create_connection((host, 53), timeout=3)
                status = "REACHABLE"
            except:
                status = "UNREACHABLE"
            detailed_info.append({"Test": f"Ping {name}", "Result": status})

        # DNS information
        dns_output = run_cmd("ipconfig /all")
        dns_servers = []
        gateways = []
        dhcp_servers = []
        dhcp_enabled = []
        domain_suffix = []

        for line in dns_output.split('\n'):
            line_lower = line.lower()
            if "dns servers" in line_lower and ":" in line:
                dns_servers.append(line.split(":")[1].strip())
            elif "default gateway" in line_lower and ":" in line:
                gateway = line.split(":")[1].strip()
                if gateway and gateway != "":
                    gateways.append(gateway)
            elif "dhcp server" in line_lower and ":" in line:
                dhcp_servers.append(line.split(":")[1].strip())
            elif "dhcp enabled" in line_lower and ":" in line:
                dhcp_enabled.append(line.split(":")[1].strip())
            elif "connection-specific dns suffix" in line_lower and ":" in line:
                domain_suffix.append(line.split(":")[1].strip())

        detailed_info.append({
            "Property": "DNS Servers",
            "Value": ", ".join(dns_servers) if dns_servers else "NOT CONFIGURED"
        })
        detailed_info.append({
            "Property": "Default Gateways",
            "Value": ", ".join(gateways) if gateways else "NOT AVAILABLE"
        })
        detailed_info.append({
            "Property": "DHCP Servers",
            "Value": ", ".join(dhcp_servers) if dhcp_servers else "NOT CONFIGURED"
        })
        detailed_info.append({
            "Property": "DHCP Enabled",
            "Value": ", ".join(dhcp_enabled) if dhcp_enabled else "UNKNOWN"
        })
        detailed_info.append({
            "Property": "Domain Suffix",
            "Value": ", ".join(domain_suffix) if domain_suffix else "NONE"
        })

        # Advanced network info
        detailed_info.extend([
            {"Property": "Hostname", "Value": socket.gethostname()},
            {"Property": "FQDN", "Value": socket.getfqdn()},
            {"Property": "Host IP", "Value": socket.gethostbyname(socket.gethostname())},
            {"Property": "Network Scan Time", "Value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {"Property": "Active Connections",
             "Value": len([conn for conn in psutil.net_connections() if conn.status == 'ESTABLISHED'])},
            {"Property": "Total Network Interfaces", "Value": len(psutil.net_if_addrs())}
        ])

    except Exception as e:
        detailed_info.append({"Property": "Analysis Error", "Value": f"Network analysis failed: {str(e)}"})

    return detailed_info


def get_real_time_data_usage():
    io_counters = psutil.net_io_counters()

    # Calculate rates (approximate)
    static_data = [
        {"Metric": "Total Bytes Sent", "Value": f"{io_counters.bytes_sent:,} bytes",
         "Formatted": f"{io_counters.bytes_sent / (1024 ** 3):.2f} GB"},
        {"Metric": "Total Bytes Received", "Value": f"{io_counters.bytes_recv:,} bytes",
         "Formatted": f"{io_counters.bytes_recv / (1024 ** 3):.2f} GB"},
        {"Metric": "Total Packets Sent", "Value": f"{io_counters.packets_sent:,} packets"},
        {"Metric": "Total Packets Received", "Value": f"{io_counters.packets_recv:,} packets"},
        {"Metric": "Errors In", "Value": io_counters.errin, "Status": "HIGH" if io_counters.errin > 1000 else "NORMAL"},
        {"Metric": "Errors Out", "Value": io_counters.errout,
         "Status": "HIGH" if io_counters.errout > 1000 else "NORMAL"},
        {"Metric": "Drop In", "Value": io_counters.dropin, "Status": "HIGH" if io_counters.dropin > 100 else "NORMAL"},
        {"Metric": "Drop Out", "Value": io_counters.dropout,
         "Status": "HIGH" if io_counters.dropout > 100 else "NORMAL"},
        {"Metric": "Error Rate In",
         "Value": f"{(io_counters.errin / io_counters.packets_recv) * 100:.4f}%" if io_counters.packets_recv > 0 else "0%"},
        {"Metric": "Error Rate Out",
         "Value": f"{(io_counters.errout / io_counters.packets_sent) * 100:.4f}%" if io_counters.packets_sent > 0 else "0%"}
    ]

    return static_data


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

            total_profiles = len(profiles)
            print(f"{Fore.GREEN}Found {total_profiles} WiFi profiles{Style.RESET_ALL}")

            if total_profiles == 0:
                return [{"Type": "Info", "SSID": "No WiFi profiles found", "Password": "N/A"}]

            # Get current connected network
            current_output = run_cmd("netsh wlan show interfaces")
            current_ssid = "Not connected"
            signal_strength = "Unknown"
            for line in current_output.split('\n'):
                if 'SSID' in line and 'BSSID' not in line and ':' in line:
                    current_ssid = line.split(':')[1].strip()
                elif 'Signal' in line and ':' in line:
                    signal_strength = line.split(':')[1].strip()

            wifi_info.append({
                "Type": "CURRENTLY CONNECTED",
                "SSID": current_ssid,
                "Password": "ACTIVE CONNECTION",
                "Security": signal_strength
            })

            # Process ALL profiles without any limits
            successful = 0
            failed = 0

            for i, profile in enumerate(profiles, 1):
                try:
                    # Show progress
                    progress = (i / total_profiles) * 100
                    print(f"{Fore.CYAN}Scanning {i}/{total_profiles} ({progress:.1f}%): {profile}{Style.RESET_ALL}")

                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear')
                    password = "Not stored or encrypted"
                    security = "Unknown"
                    connection_mode = "Unknown"

                    # Enhanced password extraction
                    for line in key_output.split('\n'):
                        line_lower = line.lower().strip()
                        if 'key content' in line_lower and ':' in line:
                            password_value = line.split(':')[1].strip()
                            if password_value:
                                password = password_value
                        elif 'authentication' in line_lower and ':' in line:
                            security = line.split(':')[1].strip()
                        elif 'connection mode' in line_lower and ':' in line:
                            connection_mode = line.split(':')[1].strip()
                        elif 'cipher' in line_lower and ':' in line:
                            # Additional security info
                            security += f" | {line.split(':')[1].strip()}"

                    # Check if password was actually found
                    if password != "Not stored or encrypted":
                        successful += 1
                    else:
                        failed += 1

                    wifi_info.append({
                        "Type": "Stored Network",
                        "SSID": profile,
                        "Password": password,
                        "Security": f"{security} | {connection_mode}"
                    })

                except Exception as e:
                    wifi_info.append({
                        "Type": "Failed",
                        "SSID": profile,
                        "Password": f"Access denied or Error: {str(e)}",
                        "Security": "Requires administrator privileges"
                    })
                    failed += 1

            # Add summary
            print(f"{Fore.GREEN}WiFi scan completed: {successful} successful, {failed} failed{Style.RESET_ALL}")

        except Exception as e:
            wifi_info.append({
                "Type": "Critical Error",
                "SSID": "Scan Failed",
                "Password": f"Error: {str(e)}",
                "Security": "Run as Administrator"
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

def get_security_credentials():
    creds_info = []
    if platform.system() == "Windows":
        try:
            output = run_cmd("cmdkey /list")
            if output and "Currently stored credentials" in output:
                lines = output.split('\n')
                for line in lines:
                    if 'Target:' in line:
                        target = line.split('Target:')[1].strip()
                        if target and not target.startswith('LegacyGeneric:'):
                            creds_info.append({
                                "Credential Target": target,
                                "Type": "Windows Credential",
                                "Risk Level": "Low"
                            })
        except Exception as e:
            creds_info.append({
                "Credential Target": f"Error: {str(e)}",
                "Type": "Access Denied",
                "Risk Level": "Unknown"
            })

    return creds_info if creds_info else [
        {"Credential Target": "No stored credentials found", "Type": "Info", "Risk Level": "None"}]


def get_enhanced_command_history():
    history_info = []
    try:
        # PowerShell history
        ps_history_path = os.path.join(
            os.environ['USERPROFILE'],
            'AppData', 'Roaming', 'Microsoft', 'Windows', 'PowerShell', 'PSReadLine',
            'ConsoleHost_history.txt'
        )

        # Command Prompt history (approximate)
        cmd_history = []
        try:
            # Try to get recent commands from various sources
            recent_commands = run_cmd("doskey /history")
            if recent_commands and "not recognized" not in recent_commands:
                cmd_history = recent_commands.split('\n')[-10:]
        except:
            pass

        all_commands = []

        # Read PowerShell history
        if os.path.exists(ps_history_path):
            with open(ps_history_path, 'r', encoding='utf-8', errors='ignore') as f:
                ps_commands = f.readlines()[-20:]  # Last 20 commands
                all_commands.extend([("PowerShell", cmd.strip()) for cmd in ps_commands if cmd.strip()])

        # Add Command Prompt history
        all_commands.extend([("CMD", cmd.strip()) for cmd in cmd_history if cmd.strip()])

        # Display most recent 15 commands total
        for i, (shell_type, cmd) in enumerate(all_commands[-15:], 1):
            history_info.append({
                "#": i,
                "Shell": shell_type,
                "Command": cmd[:100] + "..." if len(cmd) > 100 else cmd
            })

    except Exception as e:
        history_info.append({
            "#": 1,
            "Shell": "Error",
            "Command": f"Could not retrieve command history: {str(e)}"
        })

    return history_info if history_info else [{"#": 1, "Shell": "Info", "Command": "No command history available"}]


def get_hardware_connection_analysis():
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

            # Connection quality assessment
            if io:
                total_traffic = io.bytes_sent + io.bytes_recv
                if total_traffic > 1024 ** 3:  # 1 GB
                    usage_level = "Heavy"
                elif total_traffic > 100 * 1024 ** 2:  # 100 MB
                    usage_level = "Moderate"
                else:
                    usage_level = "Light"
            else:
                usage_level = "Unknown"

            hardware_info.append({
                "Interface Name": interface_name,
                "Description": f"Network Adapter - {interface_name}",
                "Physical Address (MAC)": mac_addr,
                "Status": "Connected" if stat.isup else "Disconnected",
                "MTU": stat.mtu,
                "Speed": f"{stat.speed} Mbps" if stat.speed > 0 else "Unknown",
                "Data Received": f"{io.bytes_recv / (1024 ** 3):.3f} GB" if io else "N/A",
                "Data Sent": f"{io.bytes_sent / (1024 ** 3):.3f} GB" if io else "N/A",
                "Usage Level": usage_level
            })

    return hardware_info if hardware_info else [{"Interface Name": "No interfaces", "Status": "N/A"}]


# -------------------------------------------------------------------
#  MULTI-FORMAT REPORT GENERATION
# -------------------------------------------------------------------
def generate_comprehensive_reports():
    downloads = get_downloads_folder()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    reports_generated = []

    # Generate HTML Report
    try:
        html_path = generate_html_report()
        reports_generated.append(("HTML", html_path))
    except Exception as e:
        monitor.log_security_event("REPORT_ERROR", f"HTML report failed: {str(e)}")

    # Generate JSON Report
    try:
        json_path = generate_json_report()
        reports_generated.append(("JSON", json_path))
    except Exception as e:
        monitor.log_security_event("REPORT_ERROR", f"JSON report failed: {str(e)}")

    # Generate Text Report
    try:
        txt_path = generate_text_report()
        reports_generated.append(("TXT", txt_path))
    except Exception as e:
        monitor.log_security_event("REPORT_ERROR", f"Text report failed: {str(e)}")

    return reports_generated


def generate_json_report():
    downloads = get_downloads_folder()
    json_path = os.path.join(downloads, f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    report_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "device_name": socket.gethostname(),
            "platform": platform.platform(),
            "scanner_version": "3.0.0",
            "scan_depth": Config.SCAN_DEPTH
        },
        "system_health": {
            "score": get_system_health_score(),
            "performance_log": monitor.performance_log[-10:],  # Last 10 entries
            "security_events": monitor.security_events[-5:]  # Last 5 events
        },
        "sections": {
            "device_specifications": get_device_specifications(),
            "storage_details": get_advanced_storage_details(),
            "graphics_card_info": get_comprehensive_graphics_info(),
            "network_analysis": get_network_analysis(),
            "detailed_network_properties": get_advanced_network_properties(),
            "data_usage": get_real_time_data_usage(),
            "wifi_analysis": get_comprehensive_wifi_analysis(),
            "security_credentials": get_security_credentials(),
            "command_history": get_enhanced_command_history(),
            "hardware_connection_analysis": get_hardware_connection_analysis()
        }
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, default=str)

    return json_path


def generate_text_report():
    downloads = get_downloads_folder()
    txt_path = os.path.join(downloads, f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"COMPREHENSIVE SYSTEM REPORT\n")
        f.write(f"=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Device: {socket.gethostname()}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"System Health: {get_system_health_score()}/100\n\n")

        sections = [
            ("DEVICE SPECIFICATIONS", get_device_specifications()),
            ("STORAGE DETAILS", get_advanced_storage_details()),
            ("GRAPHICS CARD INFO", get_comprehensive_graphics_info()),
            ("NETWORK ANALYSIS", get_network_analysis()),
            ("NETWORK PROPERTIES", get_advanced_network_properties()),
            ("DATA USAGE", get_real_time_data_usage()),
            ("WIFI ANALYSIS", get_comprehensive_wifi_analysis()),
            ("SECURITY CREDENTIALS", get_security_credentials()),
            ("COMMAND HISTORY", get_enhanced_command_history()),
            ("HARDWARE CONNECTIONS", get_hardware_connection_analysis())
        ]

        for section_name, data in sections:
            f.write(f"\n{section_name}\n")
            f.write("-" * len(section_name) + "\n")
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

    # Gather all data
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
        "Hardware Connection Properties": get_hardware_connection_analysis()
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
                background: #0a0a0a;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,255,0,0.1);
                margin-bottom: 30px;
                text-align: center;
                border: 1px solid #00ff00;
            }}

            .header h1 {{
                color: #00ff00;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 0 0 10px #00ff00;
            }}

            .header p {{
                color: #00ff00;
                font-size: 1.1em;
            }}

            .section {{
                background: #0a0a0a;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,255,0,0.1);
                margin-bottom: 25px;
                transition: transform 0.3s ease;
                border: 1px solid #00ff00;
            }}

            .section:hover {{
                transform: translateY(-5.5px);
                box-shadow: 0 8px 25px rgba(0,255,0,0.2);
            }}

            .section h2 {{
                color: #00ff00;
                border-bottom: 2px solid #00ff00;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 1.3em;
                text-shadow: 0 0 5px #00ff00;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}

            th {{
                background: #003300;
                color: #00ff00;
                padding: 12px 15px;
                text-align: left;
                font-weight: 600;
                border: 1px solid #00ff00;
            }}

            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #00ff00;
                color: #00ff00;
                border: 1px solid #00ff00;
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
                color: #ff0000;
                font-weight: bold;
            }}

            .metric-value {{
                font-family: 'Courier New', monospace;
                background: #001a00;
                padding: 2px 6px;
                border-radius: 4px;
                color: #00ff00;
            }}

            .footer {{
                text-align: center;
                color: #00ff00;
                margin-top: 40px;
                padding: 20px;
            }}

            .network-scroll-container {{
                overflow-x: auto;
                margin: 20px 0;
                border: 1px solid #00ff00;
                border-radius: 8px;
                padding: 10px;
            }}

            .network-table {{
                min-width: 1200px;
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
                    padding: 8px 10px;
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

    # Add each section to HTML
    for section_name, data in sections_data.items():
        html_content += f"""
            <div class="section">
                <h2>{section_name}</h2>
        """

        if data:
            if section_name == "Network Analysis":
                # Special handling for network analysis with scrolling
                html_content += '<div class="network-scroll-container">'
                html_content += '<table class="network-table">'
            else:
                html_content += '<table>'

            if isinstance(data[0], dict):
                # Table data
                headers = list(data[0].keys())
                rows = [[row.get(header, '') for header in headers] for row in data]

                html_content += '<thead><tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr></thead>'
                html_content += '<tbody>'
                for row in rows:
                    html_content += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
                html_content += '</tbody></table>'
            else:
                # Key-value data
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
                <p>Report generated by Advanced System Information Scanner v3.0</p>
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
#  ENHANCED DISPLAY FUNCTIONS
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
        ["11", "Generate HTML Report (All Data)"],
        ["12", "Generate All Reports (HTML, JSON, TXT)"],
        ["13", "Exit"]
    ]

    while True:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}MAIN MENU:{Style.RESET_ALL}")
        print(tabulate(menu_options, headers=["Option", "Description"], tablefmt="simple"))

        choice = input(f"\n{Fore.WHITE}Enter your choice (1-13): {Style.RESET_ALL}").strip()

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
            print_warning("This table has many columns - scroll horizontally to view all data")
            display_network_analysis_with_scroll()

        elif choice == '5':
            print_section_header("DETAILED NETWORK PROPERTIES")
            print_table(get_advanced_network_properties(), tablefmt="simple")

        elif choice == '6':
            print_section_header("DATA USAGE STATISTICS")
            print_table(get_real_time_data_usage(), tablefmt="simple")

        elif choice == '7':
            print_section_header("WIFI PASSWORDS - ALL NETWORKS")
            print_warning("Some passwords may not be retrievable without administrator privileges")
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
            print_section_header("GENERATING HTML REPORT")
            try:
                html_path = generate_html_report()
                print_success(f"HTML report generated successfully!")
                print_success(f"Report saved to: {html_path}")
                print_warning("Open the HTML file in your browser to view the comprehensive report")
            except Exception as e:
                print_error(f"Failed to generate HTML report: {str(e)}")

        elif choice == '12':
            print_section_header("GENERATING ALL REPORTS")
            try:
                reports = generate_comprehensive_reports()
                print_success("All reports generated successfully!")
                for report_type, report_path in reports:
                    print_success(f"{report_type} report: {report_path}")
            except Exception as e:
                print_error(f"Failed to generate reports: {str(e)}")

        elif choice == '13':
            print_success("Thank you for using the System Information Scanner!")
            break

        else:
            print_error("Invalid choice! Please enter a number between 1-13.")

        if choice != '13':
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
                print_warning("Consider running as Administrator for full functionality.")
                print_warning("This is especially important for WiFi password retrieval.")
        except:
            pass

    main()