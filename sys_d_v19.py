import os
import sys
import subprocess
import platform
from datetime import datetime, timedelta
import socket
import json
import time
import uuid
import getpass
import hashlib
import re
import threading
import queue
import math
from collections import OrderedDict, defaultdict, Counter
import statistics

# -------------------------------------------------------------------
#  AUTO-INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------------------------------------------
def install_package(pkg):
    try:
        __import__(pkg)
        return True
    except ImportError:
        try:
            print(f"[*] Installing missing package: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            print(f"[!] Failed to install {pkg}")
            return False

# Essential packages
required_packages = ["psutil", "tabulate"]

for package in required_packages:
    install_package(package)

import psutil
from tabulate import tabulate

# Try to import Windows-specific modules
try:
    import winreg
    WINREG_AVAILABLE = True
except:
    WINREG_AVAILABLE = False

try:
    import ctypes
    CTYPES_AVAILABLE = True
except:
    CTYPES_AVAILABLE = False

# -------------------------------------------------------------------
#  ENHANCED COLOR CLASS WITH GRADIENTS AND EFFECTS
# -------------------------------------------------------------------
class Colors:
    # Basic ANSI colors
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[90m'
    RESET = '\033[0m'
    
    # Enhanced effects
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    
    # Bright colors
    BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_RED = '\033[91;1m'
    BRIGHT_YELLOW = '\033[93;1m'
    BRIGHT_BLUE = '\033[94;1m'
    BRIGHT_MAGENTA = '\033[95;1m'
    BRIGHT_CYAN = '\033[96;1m'
    BRIGHT_WHITE = '\033[97;1m'
    
    # Material Design colors
    MATERIAL_RED = '\033[38;5;203m'
    MATERIAL_GREEN = '\033[38;5;77m'
    MATERIAL_BLUE = '\033[38;5;68m'
    MATERIAL_YELLOW = '\033[38;5;227m'
    MATERIAL_ORANGE = '\033[38;5;215m'
    
    # Cyber/Neon colors
    NEON_GREEN = '\033[38;5;82m'
    NEON_RED = '\033[38;5;196m'
    NEON_BLUE = '\033[38;5;81m'
    NEON_PINK = '\033[38;5;207m'
    
    @staticmethod
    def rgb(r, g, b):
        """Create RGB color (0-255 range)"""
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def hex(hex_color):
        """Create color from hex code (e.g., '#FF5733')"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def gradient(text, start_color, end_color):
        """Create gradient text effect"""
        result = ""
        length = len(text)
        for i, char in enumerate(text):
            ratio = i / max(length, 1)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            result += f'\033[38;2;{r};{g};{b}m{char}'
        return result + Colors.RESET
    
    @staticmethod
    def rainbow_text(text):
        """Create rainbow text effect"""
        colors = [
            (255, 0, 0),    # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (148, 0, 211)   # Violet
        ]
        result = ""
        for i, char in enumerate(text):
            color_idx = int((i / max(len(text), 1)) * (len(colors) - 1))
            r, g, b = colors[color_idx]
            result += f'\033[38;2;{r};{g};{b}m{char}'
        return result + Colors.RESET

# -------------------------------------------------------------------
#  ENHANCED UTILITY FUNCTIONS
# -------------------------------------------------------------------
def print_colored(text, color=Colors.WHITE, style="", end="\n"):
    """Print colored text with optional styles"""
    if style == "gradient" and isinstance(color, tuple) and len(color) == 2:
        text = Colors.gradient(text, color[0], color[1])
        print(text, end=end)
    elif style == "rainbow":
        text = Colors.rainbow_text(text)
        print(text, end=end)
    else:
        print(f"{color}{text}{Colors.RESET}", end=end)

def print_status(message, status="INFO", details=""):
    """Enhanced status printer with details"""
    status_config = {
        "INFO": {"color": Colors.BOLD + Colors.CYAN, "icon": "[+]"},
        "SUCCESS": {"color": Colors.GREEN, "icon": "[✓]"},
        "WARNING": {"color": Colors.YELLOW, "icon": "[!]"},
        "ERROR": {"color": Colors.RED, "icon": "[✗]"},
        "SCAN": {"color": Colors.MAGENTA, "icon": "[→]"},
        "DATA": {"color": Colors.BLUE, "icon": "[■]"},
        "SYSTEM": {"color": Colors.CYAN, "icon": "[⚙]"},
        "SECURITY": {"color": Colors.RED, "icon": "[🛡]"},
        "NETWORK": {"color": Colors.GREEN, "icon": "[🌐]"},
        "HARDWARE": {"color": Colors.YELLOW, "icon": "[💻]"},
        "STATS": {"color": Colors.MAGENTA, "icon": "[📊]"},
        "GRAPH": {"color": Colors.CYAN, "icon": "[📈]"}
    }
    
    config = status_config.get(status, status_config["INFO"])
    icon = config["icon"]
    color = config["color"]
    
    if details:
        message = f"{message} {Colors.DIM}({details}){Colors.RESET}"
    
    print_colored(f"{icon} {message}", color)

def format_bytes(bytes_num):
    """Convert bytes to human readable format"""
    if bytes_num == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    
    while bytes_num >= 1024.0 and unit_index < len(units) - 1:
        bytes_num /= 1024.0
        unit_index += 1
    
    return f"{bytes_num:.2f} {units[unit_index]}"

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return (part / total) * 100

# -------------------------------------------------------------------
#  DATA COLLECTION FUNCTIONS - ALL DEFINED
# -------------------------------------------------------------------
def run_command_with_timeout(cmd, timeout=10):
    """Run command with timeout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, 
                               text=True, encoding='utf-8', 
                               errors='ignore', timeout=timeout)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR] {str(e)}"

# -------------------------------------------------------------------
#  SYSTEM INFORMATION FUNCTIONS
# -------------------------------------------------------------------
def get_comprehensive_system_info():
    """Get extremely detailed system information"""
    info = OrderedDict()
    
    # Basic system info
    info["System"] = platform.system()
    info["Node Name"] = platform.node()
    info["Release"] = platform.release()
    info["Version"] = platform.version()
    info["Machine"] = platform.machine()
    
    # Try to get processor info
    try:
        info["Processor"] = platform.processor()
    except:
        info["Processor"] = "Unknown"
    
    try:
        info["Architecture"] = platform.architecture()[0]
    except:
        info["Architecture"] = "Unknown"
    
    # Python info
    info["Python Version"] = platform.python_version()
    try:
        info["Python Compiler"] = platform.python_compiler()
        info["Python Build"] = platform.python_build()[1]
    except:
        info["Python Compiler"] = "Unknown"
        info["Python Build"] = "Unknown"
    
    # Windows specific
    if platform.system() == "Windows" and WINREG_AVAILABLE:
        try:
            # Get Windows edition
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            try:
                info["Product Name"] = winreg.QueryValueEx(key, "ProductName")[0]
            except:
                info["Product Name"] = "Unknown"
            
            try:
                info["Edition ID"] = winreg.QueryValueEx(key, "EditionID")[0]
            except:
                info["Edition ID"] = "Unknown"
                
            winreg.CloseKey(key)
        except Exception as e:
            info["Windows Registry Error"] = str(e)[:50]
    
    # Uptime
    try:
        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        info["Boot Time"] = datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format uptime nicely
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        info["Uptime"] = f"{days}d {hours}h {minutes}m {seconds}s"
    except:
        info["Boot Time"] = "Unknown"
        info["Uptime"] = "Unknown"
    
    return [[k, v] for k, v in info.items()]

def get_extended_hardware_info():
    """Get detailed hardware information"""
    hardware = []
    
    # CPU Information
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info = {
                "Category": "CPU",
                "Detail": platform.processor() or "Unknown",
                "Current Frequency": f"{cpu_freq.current:.2f} MHz",
                "Max Frequency": f"{cpu_freq.max:.2f} MHz" if cpu_freq.max else "N/A",
                "Cores": f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical"
            }
        else:
            cpu_info = {
                "Category": "CPU",
                "Detail": platform.processor() or "Unknown",
                "Current Frequency": "N/A",
                "Max Frequency": "N/A",
                "Cores": f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical"
            }
        hardware.append(cpu_info)
    except Exception as e:
        hardware.append({
            "Category": "CPU",
            "Detail": f"Error: {str(e)}",
            "Current Frequency": "N/A",
            "Max Frequency": "N/A",
            "Cores": "N/A"
        })
    
    # Memory Information
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        hardware.append({
            "Category": "MEMORY",
            "Detail": f"Total: {format_bytes(memory.total)}",
            "Available": format_bytes(memory.available),
            "Used": format_bytes(memory.used),
            "Usage": f"{memory.percent}%",
            "Swap Total": format_bytes(swap.total)
        })
    except Exception as e:
        hardware.append({
            "Category": "MEMORY",
            "Detail": f"Error: {str(e)}",
            "Available": "N/A",
            "Used": "N/A",
            "Usage": "N/A",
            "Swap Total": "N/A"
        })
    
    # Disk Information
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                hardware.append({
                    "Category": "DISK",
                    "Device": partition.device,
                    "Mountpoint": partition.mountpoint,
                    "Filesystem": partition.fstype,
                    "Total": format_bytes(usage.total),
                    "Used": format_bytes(usage.used),
                    "Free": format_bytes(usage.free),
                    "Usage": f"{usage.percent}%"
                })
            except:
                continue
    except:
        pass
    
    # Battery Information
    try:
        battery = psutil.sensors_battery()
        if battery:
            time_left = "Unknown"
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                hours = battery.secsleft // 3600
                minutes = (battery.secsleft % 3600) // 60
                time_left = f"{hours}h {minutes}m"
            
            hardware.append({
                "Category": "BATTERY",
                "Percentage": f"{battery.percent}%",
                "Power Plugged": "Yes" if battery.power_plugged else "No",
                "Time Left": time_left
            })
    except:
        pass
    
    # Network Adapters
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for interface, addresses in addrs.items():
            status = "DOWN"
            speed = "N/A"
            
            if interface in stats:
                status = "UP" if stats[interface].isup else "DOWN"
                speed = f"{stats[interface].speed} Mbps" if stats[interface].speed > 0 else "N/A"
            
            mac_address = "N/A"
            if addresses and len(addresses) > 0:
                for addr in addresses:
                    if addr.family == -1:  # MAC address
                        mac_address = addr.address
                        break
            
            hardware.append({
                "Category": "NETWORK",
                "Interface": interface,
                "Status": status,
                "Speed": speed,
                "MAC": mac_address
            })
    except:
        pass
    
    return hardware

def get_detailed_process_info():
    """Get extremely detailed process information"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent',
                                     'memory_info', 'create_time', 'status', 'cpu_times',
                                     'num_threads', 'exe', 'cmdline', 'ppid']):
        try:
            pinfo = proc.info
            
            # Calculate additional metrics
            create_time = datetime.fromtimestamp(pinfo['create_time'])
            uptime = datetime.now() - create_time
            
            # Get parent process info
            parent_name = "N/A"
            if pinfo['ppid']:
                try:
                    parent = psutil.Process(pinfo['ppid'])
                    parent_name = parent.name()
                except:
                    pass
            
            # Format memory
            memory_mb = "N/A"
            if pinfo.get('memory_info'):
                memory_mb = f"{pinfo['memory_info'].rss / (1024*1024):.2f}"
            
            # Format executable path
            exe_path = "N/A"
            if pinfo.get('exe'):
                if len(pinfo['exe']) > 50:
                    exe_path = "..." + pinfo['exe'][-47:]
                else:
                    exe_path = pinfo['exe']
            
            # Format command line
            cmd_line = ""
            if pinfo.get('cmdline'):
                cmd_line = ' '.join(pinfo['cmdline'][:2])
                if len(cmd_line) > 30:
                    cmd_line = cmd_line[:27] + "..."
            
            processes.append({
                "PID": pinfo['pid'],
                "Name": (pinfo['name'][:30] + "...") if len(pinfo['name']) > 30 else pinfo['name'],
                "User": pinfo['username'] or "SYSTEM",
                "CPU %": f"{pinfo['cpu_percent']:.2f}",
                "Memory %": f"{pinfo['memory_percent']:.3f}",
                "Memory (MB)": memory_mb,
                "Threads": pinfo.get('num_threads', 'N/A'),
                "Status": pinfo['status'],
                "Parent": f"{parent_name} ({pinfo['ppid']})",
                "Uptime": str(uptime).split('.')[0],
                "Created": create_time.strftime('%H:%M:%S'),
                "Executable": exe_path,
                "Command Line": cmd_line
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            continue
    
    # Sort by CPU usage
    try:
        processes.sort(key=lambda x: float(x['CPU %']), reverse=True)
    except:
        pass
    
    return processes[:100]  # Return top 100 processes

def get_network_analysis_extended():
    """Get comprehensive network analysis"""
    network_info = []
    
    # Network interfaces
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        
        for interface in addrs:
            iface_info = {
                "Interface": interface,
                "Status": "UP" if interface in stats and stats[interface].isup else "DOWN",
                "MTU": stats[interface].mtu if interface in stats else "N/A",
                "Speed": f"{stats[interface].speed} Mbps" if interface in stats and stats[interface].speed > 0 else "N/A",
                "MAC": "N/A",
                "IPv4": [],
                "IPv6": []
            }
            
            # Get addresses
            for addr in addrs[interface]:
                if addr.family == -1:  # MAC
                    iface_info["MAC"] = addr.address
                elif addr.family == 2:  # IPv4
                    if addr.netmask:
                        iface_info["IPv4"].append(f"{addr.address}/{addr.netmask}")
                    else:
                        iface_info["IPv4"].append(addr.address)
                elif addr.family == 23:  # IPv6
                    iface_info["IPv6"].append(addr.address)
            
            # Get IO stats
            if interface in io_counters:
                io = io_counters[interface]
                iface_info.update({
                    "Bytes Sent": format_bytes(io.bytes_sent),
                    "Bytes Recv": format_bytes(io.bytes_recv),
                    "Packets Sent": f"{io.packets_sent:,}",
                    "Packets Recv": f"{io.packets_recv:,}",
                    "Errors In": f"{io.errin:,}",
                    "Errors Out": f"{io.errout:,}",
                    "Dropped In": f"{io.dropin:,}",
                    "Dropped Out": f"{io.dropout:,}"
                })
            
            # Join lists to strings
            iface_info["IPv4"] = ", ".join(iface_info["IPv4"]) if iface_info["IPv4"] else "N/A"
            iface_info["IPv6"] = ", ".join(iface_info["IPv6"]) if iface_info["IPv6"] else "N/A"
            
            network_info.append(iface_info)
    except Exception as e:
        network_info.append({
            "Interface": "Error",
            "Status": f"Collection failed: {str(e)[:50]}",
            "MTU": "N/A",
            "Speed": "N/A"
        })
    
    # Active connections
    try:
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            try:
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        "Protocol": conn.type.name,
                        "Local": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "Remote": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        "Status": conn.status,
                        "PID": conn.pid
                    })
            except:
                continue
        
        # Add connections as separate section
        for i, conn in enumerate(connections[:20]):  # Limit to 20 connections
            network_info.append({
                "Interface": f"CONN_{i+1}",
                "Protocol": conn["Protocol"],
                "Local": conn["Local"],
                "Remote": conn["Remote"],
                "Status": conn["Status"],
                "PID": conn["PID"]
            })
    except:
        pass
    
    return network_info

def get_security_audit():
    """Perform security audit"""
    security_info = []
    
    if platform.system() == "Windows":
        # Check for admin privileges
        try:
            if CTYPES_AVAILABLE:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                is_admin = False
            security_info.append({
                "Security Feature": "Admin Privileges",
                "Status": "Yes" if is_admin else "No",
                "Risk": "High" if is_admin else "Low"
            })
        except:
            security_info.append({
                "Security Feature": "Admin Privileges",
                "Status": "Unknown",
                "Risk": "Unknown"
            })
        
        # Try to check firewall
        try:
            firewall_status = run_command_with_timeout("netsh advfirewall show allprofiles", 5)
            if "ON" in firewall_status:
                security_info.append({
                    "Security Feature": "Firewall",
                    "Status": "Enabled",
                    "Risk": "Low"
                })
            else:
                security_info.append({
                    "Security Feature": "Firewall",
                    "Status": "Disabled",
                    "Risk": "High"
                })
        except:
            security_info.append({
                "Security Feature": "Firewall",
                "Status": "Unknown",
                "Risk": "Medium"
            })
    else:
        # For non-Windows systems
        try:
            is_admin = os.getuid() == 0
            security_info.append({
                "Security Feature": "Root Privileges",
                "Status": "Yes" if is_admin else "No",
                "Risk": "High" if is_admin else "Low"
            })
        except:
            pass
        
        security_info.append({
            "Security Feature": "Platform",
            "Status": f"{platform.system()}",
            "Risk": "N/A"
        })
    
    return security_info

def get_installed_software_extended():
    """Get detailed installed software information"""
    software_list = []
    
    if platform.system() == "Windows":
        try:
            # Try using wmic command
            output = run_command_with_timeout('wmic product get name,version,vendor /format:csv', 15)
            if output and "No Instance" not in output:
                lines = output.split('\n')
                for line in lines:
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            software_list.append({
                                "Name": parts[1][:50],
                                "Version": parts[2],
                                "Publisher": parts[3],
                                "Install Date": "N/A",
                                "Install Location": "N/A"
                            })
            
            # If wmic failed, try registry
            if not software_list and WINREG_AVAILABLE:
                try:
                    registry_paths = [
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
                    ]
                    
                    for reg_path in registry_paths:
                        try:
                            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                            for i in range(0, min(100, winreg.QueryInfoKey(key)[0])):
                                try:
                                    subkey_name = winreg.EnumKey(key, i)
                                    subkey = winreg.OpenKey(key, subkey_name)
                                    
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    except:
                                        display_name = None
                                    
                                    if display_name:
                                        software_info = {
                                            "Name": (display_name[:50] + "...") if len(display_name) > 50 else display_name,
                                            "Version": "N/A",
                                            "Publisher": "N/A",
                                            "Install Date": "N/A",
                                            "Install Location": "N/A"
                                        }
                                        
                                        try:
                                            software_info["Version"] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                        except:
                                            pass
                                        
                                        try:
                                            software_info["Publisher"] = winreg.QueryValueEx(subkey, "Publisher")[0]
                                        except:
                                            pass
                                        
                                        software_list.append(software_info)
                                    
                                    winreg.CloseKey(subkey)
                                except:
                                    continue
                            
                            winreg.CloseKey(key)
                        except:
                            continue
                except:
                    pass
            
        except Exception as e:
            software_list.append({
                "Name": f"Error: {str(e)[:50]}",
                "Version": "N/A",
                "Publisher": "N/A"
            })
    else:
        # For Linux/Mac
        try:
            # Try to get installed packages
            if platform.system() == "Linux":
                output = run_command_with_timeout("dpkg-query -l | tail -n +6 | head -20", 10)
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 3:
                                software_list.append({
                                    "Name": parts[1][:50],
                                    "Version": parts[2],
                                    "Publisher": "System Package",
                                    "Install Date": "N/A",
                                    "Install Location": "N/A"
                                })
            elif platform.system() == "Darwin":  # macOS
                output = run_command_with_timeout("system_profiler SPApplicationsDataType | grep -A2 'Location:' | head -30", 10)
                if output:
                    lines = output.split('\n')
                    current_name = ""
                    for line in lines:
                        if 'Location:' in line:
                            path = line.split('Location:')[1].strip()
                            name = os.path.basename(path).replace('.app', '')
                            if name:
                                software_list.append({
                                    "Name": name[:50],
                                    "Version": "N/A",
                                    "Publisher": "macOS Application",
                                    "Install Date": "N/A",
                                    "Install Location": path[:50]
                                })
        except:
            pass
        
        if not software_list:
            software_list.append({
                "Name": f"Non-Windows system: {platform.system()}",
                "Version": "N/A",
                "Publisher": "N/A"
            })
    
    # Remove duplicates
    seen = set()
    unique_software = []
    for item in software_list:
        identifier = item["Name"]
        if identifier not in seen:
            seen.add(identifier)
            unique_software.append(item)
    
    return unique_software[:50]

def get_system_services_extended():
    """Get detailed service information"""
    services = []
    
    if platform.system() == "Windows":
        try:
            # Use wmic for service information
            output = run_command_with_timeout('wmic service get name,displayname,state,startmode,pathname /format:csv', 10)
            if output and "No Instance" not in output:
                lines = output.split('\n')
                for line in lines:
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 6:
                            services.append({
                                "Name": parts[1][:20],
                                "Display Name": parts[2][:30],
                                "State": parts[3],
                                "Start Mode": parts[4],
                                "Path": (parts[5][:30] + "...") if len(parts[5]) > 30 else parts[5]
                            })
            
            # Fallback to psutil
            if not services:
                for service in psutil.win_service_iter():
                    try:
                        info = service.as_dict()
                        services.append({
                            "Name": info.get('name', 'N/A')[:20],
                            "Display Name": info.get('display_name', 'N/A')[:30],
                            "State": info.get('status', 'N/A'),
                            "Start Mode": info.get('start_type', 'N/A'),
                            "Path": (info.get('binpath', 'N/A')[:30] + "...") if info.get('binpath') and len(info.get('binpath', '')) > 30 else info.get('binpath', 'N/A')
                        })
                    except:
                        continue
        except Exception as e:
            services.append({
                "Name": f"Error: {str(e)[:30]}",
                "Display Name": "Service enumeration failed",
                "State": "N/A",
                "Start Mode": "N/A"
            })
    else:
        # For Linux systems
        try:
            if platform.system() == "Linux":
                output = run_command_with_timeout("systemctl list-units --type=service --all --no-pager | head -30", 10)
                if output:
                    lines = output.split('\n')
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 4:
                                services.append({
                                    "Name": parts[0][:20],
                                    "Display Name": parts[0][:30],
                                    "State": parts[3],
                                    "Start Mode": "N/A",
                                    "Path": "System Service"
                                })
        except:
            pass
        
        if not services:
            services.append({
                "Name": f"Non-Windows: {platform.system()}",
                "Display Name": "Services not available",
                "State": "N/A",
                "Start Mode": "N/A"
            })
    
    return services[:30]

def get_startup_programs():
    """Get startup programs"""
    startup_programs = []
    
    if platform.system() == "Windows":
        startup_paths = [
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs\StartUp"),
        ]
        
        for path in startup_paths:
            if os.path.exists(path):
                try:
                    for file in os.listdir(path):
                        if file.lower().endswith(('.lnk', '.exe', '.bat', '.cmd')):
                            full_path = os.path.join(path, file)
                            try:
                                file_size = os.path.getsize(full_path)
                                mod_time = datetime.fromtimestamp(os.path.getmtime(full_path))
                                startup_programs.append({
                                    "Name": file[:30],
                                    "Path": (full_path[:50] + "...") if len(full_path) > 50 else full_path,
                                    "Size": format_bytes(file_size),
                                    "Modified": mod_time.strftime('%Y-%m-%d'),
                                    "Type": "Startup"
                                })
                            except:
                                continue
                except:
                    continue
    elif platform.system() == "Linux":
        # Check common startup locations
        startup_paths = [
            "/etc/rc.local",
            "/etc/init.d/",
            os.path.expanduser("~/.config/autostart"),
            os.path.expanduser("~/.config/autostart-scripts")
        ]
        
        for path in startup_paths:
            if os.path.exists(path):
                if os.path.isfile(path):
                    try:
                        file_size = os.path.getsize(path)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(path))
                        startup_programs.append({
                            "Name": os.path.basename(path)[:30],
                            "Path": path[:50],
                            "Size": format_bytes(file_size),
                            "Modified": mod_time.strftime('%Y-%m-%d'),
                            "Type": "Startup Script"
                        })
                    except:
                        pass
                elif os.path.isdir(path):
                    try:
                        for file in os.listdir(path)[:5]:  # Limit to 5 files
                            full_path = os.path.join(path, file)
                            if os.path.isfile(full_path):
                                file_size = os.path.getsize(full_path)
                                mod_time = datetime.fromtimestamp(os.path.getmtime(full_path))
                                startup_programs.append({
                                    "Name": file[:30],
                                    "Path": (full_path[:50] + "...") if len(full_path) > 50 else full_path,
                                    "Size": format_bytes(file_size),
                                    "Modified": mod_time.strftime('%Y-%m-%d'),
                                    "Type": "Startup"
                                })
                    except:
                        pass
    
    return startup_programs[:20]

def get_system_environment_extended():
    """Get comprehensive environment variables"""
    env_vars = []
    
    try:
        # System environment variables
        for key, value in os.environ.items():
            # Filter out sensitive data
            if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token', 'credential']):
                env_vars.append({
                    "Variable": key[:30],
                    "Value": (value[:80] + "...") if len(value) > 80 else value,
                    "Type": "System"
                })
        
        # Path variable broken down (limited)
        if 'PATH' in os.environ:
            paths = os.environ['PATH'].split(os.pathsep)
            for i, path in enumerate(paths[:5]):  # First 5 paths only
                env_vars.append({
                    "Variable": f"PATH[{i}]",
                    "Value": (path[:100] + "...") if len(path) > 100 else path,
                    "Type": "Path Entry"
                })
    except Exception as e:
        env_vars.append({
            "Variable": "Error",
            "Value": f"Failed to get env vars: {str(e)[:50]}",
            "Type": "Error"
        })
    
    return env_vars[:30]

def get_hardware_temperatures():
    """Get hardware temperatures if available"""
    temps = []
    
    try:
        sensors = psutil.sensors_temperatures()
        if sensors:
            for name, entries in sensors.items():
                for entry in entries:
                    temps.append({
                        "Sensor": name[:20],
                        "Label": (entry.label[:20] + "...") if entry.label and len(entry.label) > 20 else entry.label or "N/A",
                        "Current": f"{entry.current}°C",
                        "High": f"{entry.high}°C" if entry.high else "N/A",
                        "Critical": f"{entry.critical}°C" if entry.critical else "N/A"
                    })
    except:
        pass
    
    if not temps:
        temps.append({
            "Sensor": "No sensors",
            "Label": "Temperature data not available",
            "Current": "N/A",
            "High": "N/A",
            "Critical": "N/A"
        })
    
    return temps[:15]

def get_system_logs_extended():
    """Get system logs"""
    logs = []
    
    try:
        # Recent events using psutil
        boot_time = psutil.boot_time()
        logs.append({
            "Time": datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S'),
            "Event": "System Boot",
            "Details": f"Boot time recorded"
        })
        
        # User login information
        current_user = getpass.getuser()
        logs.append({
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Event": "User Session",
            "Details": f"Current user: {current_user}"
        })
        
        # Python process info
        logs.append({
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Event": "Scanner Process",
            "Details": f"PID: {os.getpid()}, Python: {sys.version.split()[0]}"
        })
        
        # System load
        try:
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            logs.append({
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Event": "System Load",
                "Details": f"Load average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
            })
        except:
            pass
        
    except Exception as e:
        logs.append({
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Event": "Error",
            "Details": f"Log collection error: {str(e)[:50]}"
        })
    
    return logs

def get_performance_metrics():
    """Get real-time performance metrics"""
    metrics = []
    
    try:
        # CPU Metrics
        cpu_percent = psutil.cpu_percent(interval=0.5, percpu=False)
        try:
            cpu_percent_per_core = psutil.cpu_percent(interval=0.5, percpu=True)
            core_details = ", ".join([f"{p}%" for p in cpu_percent_per_core[:4]])  # First 4 cores only
            if len(cpu_percent_per_core) > 4:
                core_details += f" ... (+{len(cpu_percent_per_core)-4} more)"
        except:
            core_details = "N/A"
        
        metrics.append({
            "Metric": "CPU Usage",
            "Value": f"{cpu_percent}%",
            "Details": f"Cores: {core_details}"
        })
        
        # Memory Metrics
        memory = psutil.virtual_memory()
        metrics.append({
            "Metric": "Memory Usage",
            "Value": f"{memory.percent}%",
            "Details": f"{format_bytes(memory.used)} / {format_bytes(memory.total)}"
        })
        
        # Swap Metrics
        swap = psutil.swap_memory()
        if swap.total > 0:
            metrics.append({
                "Metric": "Swap Usage",
                "Value": f"{swap.percent}%",
                "Details": f"{format_bytes(swap.used)} / {format_bytes(swap.total)}"
            })
        
        # Disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.append({
                    "Metric": "Disk Read",
                    "Value": format_bytes(disk_io.read_bytes),
                    "Details": f"{disk_io.read_count:,} operations"
                })
                metrics.append({
                    "Metric": "Disk Write",
                    "Value": format_bytes(disk_io.write_bytes),
                    "Details": f"{disk_io.write_count:,} operations"
                })
        except:
            pass
        
        # Network I/O
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.append({
                    "Metric": "Network Sent",
                    "Value": format_bytes(net_io.bytes_sent),
                    "Details": f"{net_io.packets_sent:,} packets"
                })
                metrics.append({
                    "Metric": "Network Received",
                    "Value": format_bytes(net_io.bytes_recv),
                    "Details": f"{net_io.packets_recv:,} packets"
                })
        except:
            pass
        
        # Process count
        try:
            process_count = len(psutil.pids())
            metrics.append({
                "Metric": "Running Processes",
                "Value": process_count,
                "Details": f"System processes: {process_count}"
            })
        except:
            pass
        
    except Exception as e:
        metrics.append({
            "Metric": "Error",
            "Value": "Failed",
            "Details": str(e)[:50]
        })
    
    return metrics

def get_user_accounts_extended():
    """Get detailed user account information"""
    users = []
    
    if platform.system() == "Windows":
        try:
            # Get current user
            current_user = getpass.getuser()
            users.append({
                "Username": current_user,
                "Full Name": "Current User",
                "Active": "Yes",
                "Last Logon": "Now"
            })
            
            # Try to get other users via wmic
            try:
                output = run_command_with_timeout('wmic useraccount get name,fullname /format:csv', 10)
                if output and "No Instance" not in output:
                    lines = output.split('\n')
                    for line in lines:
                        if ',' in line and 'Node' not in line:
                            parts = line.split(',')
                            if len(parts) >= 3:
                                username = parts[1]
                                fullname = parts[2] if len(parts) > 2 else "N/A"
                                if username != current_user:  # Don't add current user again
                                    users.append({
                                        "Username": username[:20],
                                        "Full Name": fullname[:30],
                                        "Active": "Unknown",
                                        "Last Logon": "N/A"
                                    })
            except:
                pass
                
        except Exception as e:
            users.append({
                "Username": f"Error: {str(e)[:30]}",
                "Full Name": "N/A",
                "Active": "N/A",
                "Last Logon": "N/A"
            })
    else:
        # For non-Windows systems
        try:
            current_user = getpass.getuser()
            users.append({
                "Username": current_user,
                "Full Name": "Current User",
                "Active": "Yes",
                "Last Logon": "Now"
            })
            
            # Try to get other users from /etc/passwd (Linux)
            if platform.system() == "Linux":
                try:
                    with open('/etc/passwd', 'r') as f:
                        lines = f.readlines()
                        for line in lines[:10]:  # First 10 users only
                            parts = line.split(':')
                            if len(parts) >= 5:
                                username = parts[0]
                                fullname = parts[4].split(',')[0]
                                if username != current_user and username not in ['root', 'daemon', 'bin']:
                                    users.append({
                                        "Username": username[:20],
                                        "Full Name": fullname[:30],
                                        "Active": "Yes",
                                        "Last Logon": "N/A"
                                    })
                except:
                    pass
        except:
            users.append({
                "Username": f"Non-Windows: {platform.system()}",
                "Full Name": "N/A",
                "Active": "N/A",
                "Last Logon": "N/A"
            })
    
    return users[:15]

def get_system_drivers_extended():
    """Get detailed driver information"""
    drivers = []
    
    if platform.system() == "Windows":
        try:
            output = run_command_with_timeout("driverquery /v", 15)
            if output:
                lines = output.split('\n')
                for line in lines[3:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 6:
                            drivers.append({
                                "Module Name": parts[0][:30],
                                "Display Name": " ".join(parts[1:-4])[:40] if len(parts) > 5 else parts[1][:40],
                                "Driver Type": parts[-4][:20],
                                "Start Mode": parts[-3][:15],
                                "State": parts[-2][:15]
                            })
            
            # Limit to 20 drivers
            drivers = drivers[:20]
            
        except Exception as e:
            drivers.append({
                "Module Name": f"Error: {str(e)[:30]}",
                "Display Name": "Driver query failed",
                "Driver Type": "N/A",
                "Start Mode": "N/A"
            })
    else:
        # For Linux systems
        try:
            if platform.system() == "Linux":
                output = run_command_with_timeout("lsmod | head -20", 10)
                if output:
                    lines = output.split('\n')
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 3:
                                drivers.append({
                                    "Module Name": parts[0][:30],
                                    "Display Name": "Kernel Module",
                                    "Driver Type": "Module",
                                    "Start Mode": "Loaded",
                                    "State": "Active"
                                })
        except:
            pass
        
        if not drivers:
            drivers.append({
                "Module Name": f"Non-Windows: {platform.system()}",
                "Display Name": "Drivers not available",
                "Driver Type": "N/A",
                "Start Mode": "N/A"
            })
    
    return drivers

def get_wifi_networks_extended():
    """Get detailed WiFi network information"""
    wifi_networks = []
    
    if platform.system() == "Windows":
        try:
            # Get WiFi profiles
            profiles_output = run_command_with_timeout("netsh wlan show profiles", 10)
            
            if profiles_output and "No wireless interface" not in profiles_output:
                profiles = []
                for line in profiles_output.split('\n'):
                    if "All User Profile" in line and ":" in line:
                        profile_name = line.split(":")[1].strip()
                        if profile_name:
                            profiles.append(profile_name)
                
                # Get details for each profile (limited to 5)
                for profile in profiles[:5]:
                    try:
                        profile_output = run_command_with_timeout(f'netsh wlan show profile name="{profile}"', 10)
                        
                        details = {}
                        if profile_output:
                            for line in profile_output.split('\n'):
                                line = line.strip()
                                if "Authentication" in line and ":" in line:
                                    details['Auth'] = line.split(":")[1].strip()
                                elif "Cipher" in line and ":" in line:
                                    details['Cipher'] = line.split(":")[1].strip()
                        
                        wifi_networks.append({
                            "SSID": profile[:30],
                            "Authentication": details.get('Auth', 'Unknown')[:20],
                            "Cipher": details.get('Cipher', 'Unknown')[:20],
                            "Password": "Not shown (encrypted)"
                        })
                        
                    except:
                        wifi_networks.append({
                            "SSID": profile[:30],
                            "Authentication": "Error",
                            "Cipher": "Error",
                            "Password": "Error retrieving"
                        })
            else:
                wifi_networks.append({
                    "SSID": "WiFi info",
                    "Authentication": "No WiFi interface or profiles",
                    "Cipher": "N/A",
                    "Password": "N/A"
                })
        
        except Exception as e:
            wifi_networks.append({
                "SSID": f"Error: {str(e)[:30]}",
                "Authentication": "N/A",
                "Cipher": "N/A",
                "Password": "N/A"
            })
    else:
        # For Linux systems
        try:
            if platform.system() == "Linux":
                output = run_command_with_timeout("nmcli -t -f ssid,signal,security device wifi list | head -10", 10)
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip():
                            parts = line.split(':')
                            if len(parts) >= 3:
                                wifi_networks.append({
                                    "SSID": parts[0][:30],
                                    "Authentication": parts[2][:20] if len(parts) > 2 else "Unknown",
                                    "Cipher": "WPA2" if "WPA2" in parts[2] else "Unknown",
                                    "Password": "Not available"
                                })
        except:
            pass
        
        if not wifi_networks:
            wifi_networks.append({
                "SSID": f"Non-Windows: {platform.system()}",
                "Authentication": "WiFi info not available",
                "Cipher": "N/A",
                "Password": "N/A"
            })
    
    return wifi_networks

# -------------------------------------------------------------------
#  STATISTICS AND GRAPH FUNCTIONS
# -------------------------------------------------------------------
def calculate_health_score(all_data):
    """Calculate system health score based on collected data"""
    score = 85  # Base score
    
    try:
        # Check memory usage
        for item in all_data.get("hardware_info", []):
            if item.get("Category") == "MEMORY" and "Usage" in item:
                usage_str = item["Usage"]
                if "%" in usage_str:
                    try:
                        usage = float(usage_str.replace("%", "").strip())
                        if usage > 90:
                            score -= 20
                        elif usage > 80:
                            score -= 10
                        elif usage > 70:
                            score -= 5
                    except:
                        pass
        
        # Check disk usage
        for item in all_data.get("hardware_info", []):
            if item.get("Category") == "DISK" and "Usage" in item:
                usage_str = item["Usage"]
                if "%" in usage_str:
                    try:
                        usage = float(usage_str.replace("%", "").strip())
                        if usage > 95:
                            score -= 15
                        elif usage > 90:
                            score -= 10
                        elif usage > 85:
                            score -= 5
                    except:
                        pass
        
        # Check security
        for item in all_data.get("security_audit", []):
            if item.get("Risk") == "High":
                score -= 5
        
        # Check CPU usage from performance metrics
        for item in all_data.get("performance_metrics", []):
            if item.get("Metric") == "CPU Usage":
                value_str = item.get("Value", "0%")
                if "%" in value_str:
                    try:
                        cpu_usage = float(value_str.replace("%", ""))
                        if cpu_usage > 90:
                            score -= 15
                        elif cpu_usage > 80:
                            score -= 10
                        elif cpu_usage > 70:
                            score -= 5
                    except:
                        pass
        
        # Bonus for good conditions
        # Check if memory usage is low
        memory_ok = False
        for item in all_data.get("hardware_info", []):
            if item.get("Category") == "MEMORY" and "Usage" in item:
                usage_str = item["Usage"]
                if "%" in usage_str:
                    try:
                        if float(usage_str.replace("%", "")) < 50:
                            memory_ok = True
                    except:
                        pass
        
        # Check if disk usage is reasonable
        disk_ok = True
        disk_count = 0
        for item in all_data.get("hardware_info", []):
            if item.get("Category") == "DISK" and "Usage" in item:
                usage_str = item["Usage"]
                if "%" in usage_str:
                    try:
                        if float(usage_str.replace("%", "")) > 90:
                            disk_ok = False
                        disk_count += 1
                    except:
                        pass
        
        if memory_ok and disk_ok and disk_count > 0:
            score += 10
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
    except:
        score = 85  # Default if calculation fails
    
    return score

def calculate_system_statistics(all_data):
    """Calculate comprehensive system statistics"""
    stats = {}
    
    # Process statistics
    processes = all_data.get("process_info", [])
    if processes:
        try:
            cpu_usages = []
            memory_usages = []
            for p in processes:
                if "CPU %" in p:
                    try:
                        cpu_usages.append(float(p["CPU %"].replace("%", "")))
                    except:
                        pass
                if "Memory %" in p:
                    try:
                        memory_usages.append(float(p["Memory %"].replace("%", "")))
                    except:
                        pass
            
            if cpu_usages:
                stats["process_count"] = len(processes)
                stats["avg_cpu_usage"] = statistics.mean(cpu_usages) if cpu_usages else 0
                stats["max_cpu_usage"] = max(cpu_usages) if cpu_usages else 0
            
            if memory_usages:
                stats["avg_memory_usage"] = statistics.mean(memory_usages) if memory_usages else 0
                stats["max_memory_usage"] = max(memory_usages) if memory_usages else 0
            
            # Process status distribution
            status_counts = {}
            for p in processes:
                status = p.get("Status", "UNKNOWN")
                status_counts[status] = status_counts.get(status, 0) + 1
            stats["process_status_dist"] = status_counts
            
        except:
            pass
    
    # Hardware statistics
    hardware = all_data.get("hardware_info", [])
    if hardware:
        try:
            # Disk statistics
            disks = [h for h in hardware if h.get("Category") == "DISK"]
            if disks:
                disk_usages = []
                for disk in disks:
                    usage_str = disk.get("Usage", "0%")
                    if "%" in usage_str:
                        try:
                            usage = float(usage_str.replace("%", ""))
                            disk_usages.append(usage)
                        except:
                            pass
                
                if disk_usages:
                    stats["avg_disk_usage"] = statistics.mean(disk_usages)
                    stats["max_disk_usage"] = max(disk_usages)
                    stats["disk_count"] = len(disks)
            
            # Memory statistics
            memory = [h for h in hardware if h.get("Category") == "MEMORY"]
            if memory:
                mem = memory[0]
                usage_str = mem.get("Usage", "0%")
                if "%" in usage_str:
                    try:
                        stats["memory_usage"] = float(usage_str.replace("%", ""))
                    except:
                        pass
        except:
            pass
    
    # Network statistics
    network = all_data.get("network_info", [])
    if network:
        try:
            active_interfaces = len([n for n in network if n.get("Status") == "UP"])
            stats["active_network_interfaces"] = active_interfaces
            stats["total_network_interfaces"] = len(network)
        except:
            pass
    
    # Software statistics
    software = all_data.get("installed_software", [])
    if software:
        stats["installed_software_count"] = len(software)
    
    # Service statistics
    services = all_data.get("system_services", [])
    if services:
        running_services = len([s for s in services if s.get("State") in ["RUNNING", "Running"]])
        stats["running_services"] = running_services
        stats["total_services"] = len(services)
    
    # User statistics
    users = all_data.get("user_accounts", [])
    if users:
        active_users = len([u for u in users if u.get("Active", "").lower() in ["yes", "true"]])
        stats["active_users"] = active_users
        stats["total_users"] = len(users)
    
    return stats

def generate_statistics_summary(all_data):
    """Generate comprehensive statistics summary"""
    stats = calculate_system_statistics(all_data)
    health_score = calculate_health_score(all_data)
    
    summary = []
    
    # System Overview
    summary.append({"Category": "SYSTEM OVERVIEW", "Metric": "Total Processes", "Value": stats.get("process_count", 0)})
    summary.append({"Category": "SYSTEM OVERVIEW", "Metric": "Running Services", "Value": f"{stats.get('running_services', 0)}/{stats.get('total_services', 0)}"})
    summary.append({"Category": "SYSTEM OVERVIEW", "Metric": "Active Users", "Value": f"{stats.get('active_users', 0)}/{stats.get('total_users', 0)}"})
    summary.append({"Category": "SYSTEM OVERVIEW", "Metric": "Installed Software", "Value": stats.get("installed_software_count", 0)})
    
    # Performance Statistics
    if "avg_cpu_usage" in stats:
        summary.append({"Category": "PERFORMANCE", "Metric": "Avg CPU Usage", "Value": f"{stats['avg_cpu_usage']:.1f}%"})
    if "max_cpu_usage" in stats:
        summary.append({"Category": "PERFORMANCE", "Metric": "Max CPU Usage", "Value": f"{stats['max_cpu_usage']:.1f}%"})
    if "avg_memory_usage" in stats:
        summary.append({"Category": "PERFORMANCE", "Metric": "Avg Memory Usage", "Value": f"{stats['avg_memory_usage']:.2f}%"})
    if "memory_usage" in stats:
        summary.append({"Category": "PERFORMANCE", "Metric": "Current Memory Usage", "Value": f"{stats['memory_usage']:.1f}%"})
    if "avg_disk_usage" in stats:
        summary.append({"Category": "PERFORMANCE", "Metric": "Avg Disk Usage", "Value": f"{stats['avg_disk_usage']:.1f}%"})
    
    # Network Statistics
    if "active_network_interfaces" in stats:
        summary.append({"Category": "NETWORK", "Metric": "Active Interfaces", "Value": f"{stats['active_network_interfaces']}/{stats.get('total_network_interfaces', 0)}"})
    
    # Hardware Statistics
    if "disk_count" in stats:
        summary.append({"Category": "HARDWARE", "Metric": "Storage Devices", "Value": stats['disk_count']})
    
    # Health Statistics
    summary.append({"Category": "HEALTH", "Metric": "System Health Score", "Value": f"{health_score}/100"})
    
    # Add risk assessment
    risk_level = "LOW"
    if health_score < 60:
        risk_level = "HIGH"
    elif health_score < 80:
        risk_level = "MEDIUM"
    summary.append({"Category": "HEALTH", "Metric": "Risk Level", "Value": risk_level})
    
    return summary

def generate_bar_graph(data_points, title="", width=50, max_value=None):
    """Generate ASCII bar graph"""
    if not data_points:
        return ""
    
    if max_value is None:
        if isinstance(data_points, dict):
            max_value = max(data_points.values())
        else:
            max_value = max(data_points)
    
    if max_value == 0:
        max_value = 1
    
    graph_lines = []
    
    if title:
        graph_lines.append(f"> {title}")
        graph_lines.append("─" * (len(title) + 2))
    
    if isinstance(data_points, dict):
        # For dictionary data
        max_key_len = max(len(str(k)) for k in data_points.keys())
        for key, value in data_points.items():
            bar_length = int((value / max_value) * width)
            bar = "█" * bar_length
            percentage = (value / max_value) * 100 if max_value > 0 else 0
            graph_lines.append(f"{str(key):<{max_key_len}} |{Colors.GREEN}{bar}{Colors.RESET}| {value} ({percentage:.1f}%)")
    else:
        # For list data
        for i, value in enumerate(data_points):
            bar_length = int((value / max_value) * width)
            bar = "█" * bar_length
            percentage = (value / max_value) * 100 if max_value > 0 else 0
            graph_lines.append(f"Item {i+1:2d} |{Colors.GREEN}{bar}{Colors.RESET}| {value} ({percentage:.1f}%)")
    
    return "\n".join(graph_lines)

def generate_pie_chart(data_points, title=""):
    """Generate text-based pie chart representation"""
    if not data_points or not isinstance(data_points, dict):
        return ""
    
    total = sum(data_points.values())
    if total == 0:
        return ""
    
    chart_lines = []
    
    if title:
        chart_lines.append(f"> {title}")
        chart_lines.append("─" * (len(title) + 2))
    
    # Calculate percentages and sort
    sorted_items = sorted(data_points.items(), key=lambda x: x[1], reverse=True)
    
    # Define pie segments characters
    segments = ["◉", "◐", "◑", "◒", "○", "◎", "●", "◌"]
    
    for i, (key, value) in enumerate(sorted_items[:8]):  # Limit to 8 items for readability
        percentage = (value / total) * 100
        segment_char = segments[i % len(segments)]
        chart_lines.append(f"{segment_char} {key[:30]:30} {Colors.GREEN}{percentage:5.1f}%{Colors.RESET} ({value})")
    
    return "\n".join(chart_lines)

def generate_cpu_usage_graph(processes):
    """Generate CPU usage graph for top processes"""
    if not processes or len(processes) < 3:
        return ""
    
    # Get top 8 processes by CPU usage
    try:
        top_processes = sorted(processes, 
                              key=lambda x: float(x.get("CPU %", "0").replace("%", "")), 
                              reverse=True)[:8]
        
        graph_data = {}
        for proc in top_processes:
            name = proc.get("Name", "Unknown")
            cpu_usage = float(proc.get("CPU %", "0").replace("%", ""))
            graph_data[name[:20]] = cpu_usage
        
        return generate_bar_graph(graph_data, "Top Processes by CPU Usage", width=40)
    except:
        return ""

def generate_memory_usage_graph(processes):
    """Generate memory usage graph for top processes"""
    if not processes or len(processes) < 3:
        return ""
    
    # Get top 8 processes by memory usage
    try:
        top_processes = sorted(processes, 
                              key=lambda x: float(x.get("Memory %", "0").replace("%", "")), 
                              reverse=True)[:8]
        
        graph_data = {}
        for proc in top_processes:
            name = proc.get("Name", "Unknown")
            mem_usage = float(proc.get("Memory %", "0").replace("%", ""))
            graph_data[name[:20]] = mem_usage
        
        return generate_bar_graph(graph_data, "Top Processes by Memory Usage", width=40)
    except:
        return ""

def generate_disk_usage_graph(hardware_info):
    """Generate disk usage graph"""
    if not hardware_info:
        return ""
    
    disks = [h for h in hardware_info if h.get("Category") == "DISK"]
    if not disks:
        return ""
    
    graph_data = {}
    for disk in disks:
        device = disk.get("Device", "Unknown")
        usage_str = disk.get("Usage", "0%")
        if "%" in usage_str:
            try:
                usage = float(usage_str.replace("%", ""))
                graph_data[device[-20:]] = usage
            except:
                pass
    
    if graph_data:
        return generate_bar_graph(graph_data, "Disk Usage by Device", width=40)
    return ""

def generate_service_status_graph(services):
    """Generate service status distribution graph"""
    if not services:
        return ""
    
    status_counts = {}
    for s in services:
        state = s.get("State", "UNKNOWN")
        status_counts[state] = status_counts.get(state, 0) + 1
    
    return generate_pie_chart(status_counts, "Service Status Distribution")

def generate_network_activity_graph(network_info):
    """Generate network interface activity graph"""
    if not network_info:
        return ""
    
    # Filter only interface entries (not connections)
    interfaces = [n for n in network_info if "IPv4" in n or "IPv6" in n]
    
    graph_data = {}
    for iface in interfaces[:6]:  # Limit to 6 interfaces
        name = iface.get("Interface", "Unknown")
        status = iface.get("Status", "DOWN")
        # Convert status to numeric for graphing
        value = 100 if status == "UP" else 10
        graph_data[name[:15]] = value
    
    if graph_data:
        return generate_bar_graph(graph_data, "Network Interface Status", width=40)
    return ""

def generate_system_health_graph(health_score):
    """Generate health score visualization"""
    health_lines = []
    health_lines.append("> SYSTEM HEALTH METER")
    health_lines.append("─" * 50)
    
    # Health meter
    meter_width = 50
    filled = int((health_score / 100) * meter_width)
    meter = "█" * filled + "░" * (meter_width - filled)
    
    # Color coding
    if health_score >= 80:
        color = Colors.GREEN
        status = "EXCELLENT"
    elif health_score >= 60:
        color = Colors.YELLOW
        status = "GOOD"
    else:
        color = Colors.RED
        status = "POOR"
    
    health_lines.append(f"[{color}{meter}{Colors.RESET}]")
    health_lines.append(f"Score: {color}{health_score}/100{Colors.RESET} - Status: {color}{status}{Colors.RESET}")
    
    return "\n".join(health_lines)

def get_comprehensive_statistics(all_data):
    """Get comprehensive statistics and graphs"""
    stats_data = []
    
    # Basic statistics
    stats_summary = generate_statistics_summary(all_data)
    stats_data.extend(stats_summary)
    
    return stats_data

def get_system_graphs(all_data):
    """Get all system graphs"""
    graphs = []
    
    # Process graphs
    processes = all_data.get("process_info", [])
    if processes:
        cpu_graph = generate_cpu_usage_graph(processes)
        if cpu_graph:
            graphs.append({"Graph Type": "CPU Usage", "Visualization": cpu_graph})
        
        mem_graph = generate_memory_usage_graph(processes)
        if mem_graph:
            graphs.append({"Graph Type": "Memory Usage", "Visualization": mem_graph})
    
    # Hardware graphs
    hardware = all_data.get("hardware_info", [])
    if hardware:
        disk_graph = generate_disk_usage_graph(hardware)
        if disk_graph:
            graphs.append({"Graph Type": "Disk Usage", "Visualization": disk_graph})
    
    # Service graphs
    services = all_data.get("system_services", [])
    if services:
        service_graph = generate_service_status_graph(services)
        if service_graph:
            graphs.append({"Graph Type": "Service Status", "Visualization": service_graph})
    
    # Network graphs
    network = all_data.get("network_info", [])
    if network:
        network_graph = generate_network_activity_graph(network)
        if network_graph:
            graphs.append({"Graph Type": "Network Status", "Visualization": network_graph})
    
    return graphs

def get_health_color(score):
    """Get health color based on score"""
    if score >= 80:
        return "linear-gradient(135deg, #00ff00 0%, #00cc00 100%)"
    elif score >= 60:
        return "linear-gradient(135deg, #ffff00 0%, #cccc00 100%)"
    else:
        return "linear-gradient(135deg, #ff0000 0%, #cc0000 100%)"

# -------------------------------------------------------------------
#  HTML GENERATION FUNCTIONS
# -------------------------------------------------------------------
def generate_section_html(section_name, data):
    """Generate HTML for a specific section"""
    if not data:
        return f"""
        <div class="section">
            <h2>> {section_name}</h2>
            <p style="color: #006600; text-align: center; padding: 20px;">> NO DATA AVAILABLE</p>
        </div>
        """
    
    html = f"""
    <div class="section">
        <h2>> {section_name}</h2>
    """
    
    if isinstance(data, list) and len(data) > 0:
        # Determine if it's a key-value list or table data
        if isinstance(data[0], list) and len(data[0]) == 2:
            # Key-value format (for system_info)
            html += '<table>'
            for item in data:
                if len(item) == 2:
                    key, value = item
                    html += f'''
                    <tr>
                        <td style="width: 30%;"><span style="color: #00ff00;">></span> {key}</td>
                        <td style="width: 70%;">{value}</td>
                    </tr>
                    '''
            html += '</table>'
        elif isinstance(data[0], dict):
            # Table format
            if data:
                headers = list(data[0].keys())
                html += '<div class="scroll-container"><table>'
                html += '<thead><tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr></thead>'
                html += '<tbody>'
                
                for row in data:
                    html += '<tr>'
                    for header in headers:
                        cell = str(row.get(header, ''))
                        cell_class = ""
                        
                        # Apply status classes
                        cell_lower = cell.lower()
                        header_lower = header.lower()
                        
                        if any(status_word in header_lower for status_word in ['status', 'state', 'active', 'enabled', 'risk']):
                            if any(good_word in cell_lower for good_word in ['active', 'enabled', 'yes', 'true', 'running', 'low']):
                                cell_class = "status-active"
                            elif any(bad_word in cell_lower for bad_word in ['inactive', 'disabled', 'no', 'false', 'stopped', 'high', 'critical']):
                                cell_class = "status-critical"
                            elif 'warning' in cell_lower or 'medium' in cell_lower:
                                cell_class = "status-warning"
                        
                        if cell_class:
                            html += f'<td class="{cell_class}">{cell}</td>'
                        else:
                            html += f'<td>{cell}</td>'
                    html += '</tr>'
                
                html += '</tbody></table></div>'
    
    html += '</div>'
    return html

def generate_statistics_html(stats_data, health_score):
    """Generate HTML for statistics dashboard"""
    if not stats_data:
        return "<p style='color: #006600; text-align: center;'>No statistics available</p>"
    
    # Group by category
    stats_by_category = {}
    for stat in stats_data:
        category = stat.get("Category", "Other")
        if category not in stats_by_category:
            stats_by_category[category] = []
        stats_by_category[category].append(stat)
    
    html = ""
    
    # Health meter
    html += f"""
    <div class="health-meter">
        <div class="health-fill" style="width: {health_score}%;"></div>
    </div>
    <div style="text-align: center; margin-bottom: 20px;">
        <span style="color: #00ff00; font-weight: bold;">System Health: {health_score}/100</span>
    </div>
    """
    
    # Statistics grid
    html += '<div class="stats-grid">'
    
    for category, stats in stats_by_category.items():
        for stat in stats:
            metric = stat.get("Metric", "")
            value = stat.get("Value", "")
            
            # Determine color based on value
            value_str = str(value)
            value_color = "#00ff00"  # Default green
            
            if "%" in value_str:
                try:
                    num_value = float(value_str.replace("%", ""))
                    if "Usage" in metric or "CPU" in metric or "Memory" in metric:
                        if num_value < 60:
                            value_color = "#00ff00"  # Green
                        elif num_value < 80:
                            value_color = "#ffff00"  # Yellow
                        else:
                            value_color = "#ff0000"  # Red
                except:
                    pass
            
            html += f"""
            <div class="stat-card">
                <h3>{metric}</h3>
                <div class="stat-value" style="color: {value_color};">{value}</div>
                <div class="stat-label">{category}</div>
            </div>
            """
    
    html += '</div>'
    
    return html

def generate_graphs_html(graphs_data):
    """Generate HTML for graphs"""
    if not graphs_data:
        return "<p style='color: #006600; text-align: center;'>No graphs available</p>"
    
    html = '<div class="stats-grid">'
    
    for graph in graphs_data:
        graph_type = graph.get("Graph Type", "")
        visualization = graph.get("Visualization", "")
        
        # Convert ASCII graph to HTML with green color
        graph_html = visualization.replace("█", '<span style="color: #00ff00;">█</span>')
        graph_html = graph_html.replace("◉", '<span style="color: #00ff00;">◉</span>')
        graph_html = graph_html.replace("◐", '<span style="color: #00cc00;">◐</span>')
        graph_html = graph_html.replace("◑", '<span style="color: #009900;">◑</span>')
        graph_html = graph_html.replace("◒", '<span style="color: #006600;">◒</span>')
        graph_html = graph_html.replace("○", '<span style="color: #00ff00;">○</span>')
        graph_html = graph_html.replace("◎", '<span style="color: #00cc00;">◎</span>')
        graph_html = graph_html.replace("●", '<span style="color: #009900;">●</span>')
        graph_html = graph_html.replace("◌", '<span style="color: #006600;">◌</span>')
        
        html += f"""
        <div class="graph-container">
            <div class="graph-title">{graph_type}</div>
            <div class="graph">{graph_html}</div>
        </div>
        """
    
    html += '</div>'
    
    return html

def generate_html_with_graphs(all_data, health_score, timestamp):
    """Generate HTML content with graphs"""
    
    health_color = get_health_color(health_score)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hostname = socket.gethostname() if hasattr(socket, 'gethostname') else "Unknown"
    platform_info = platform.platform() if hasattr(platform, 'platform') else "Unknown"
    
    # Get statistics and graphs
    stats_data = get_comprehensive_statistics(all_data)
    graphs_data = get_system_graphs(all_data)
    
    # Generate graphs HTML
    graphs_html = generate_graphs_html(graphs_data)
    stats_html = generate_statistics_html(stats_data, health_score)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Intelligence Report with Analytics</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: #000000;
            min-height: 100vh;
            margin: 0;
            padding: 0;
            color: #00ff00;
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
            background: linear-gradient(90deg, transparent, #00ff00, transparent);
            animation: scan 3s linear infinite;
            box-shadow: 0 0 10px #00ff00;
            z-index: 1000;
        }}

        @keyframes scan {{
            0% {{ top: 0%; opacity: 0; }}
            50% {{ opacity: 1; }}
            100% {{ top: 100%; opacity: 0; }}
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
        }}

        .header {{
            background: rgba(0, 20, 0, 0.8);
            padding: 25px;
            margin-bottom: 25px;
            text-align: center;
            border: 1px solid #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            position: relative;
            overflow: hidden;
        }}

        .header h1 {{
            color: #00ff00;
            font-size: 2.2em;
            margin-bottom: 10px;
            font-weight: 300;
            text-shadow: 0 0 10px #00ff00;
            letter-spacing: 1px;
        }}

        .creator {{
            color: #ff00ff;
            font-size: 1.1em;
            margin-bottom: 15px;
            font-weight: 500;
        }}

        .header p {{
            color: #00cc00;
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
            border: 1px solid #00ff00;
            text-shadow: 0 0 5px #000000;
            border-radius: 3px;
        }}

        .section {{
            background: rgba(0, 10, 0, 0.7);
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #003300;
            position: relative;
            transition: all 0.3s ease;
        }}

        .section:hover {{
            border-color: #00ff00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
        }}

        .section h2 {{
            color: #00ff00;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-size: 1.3em;
            font-weight: 500;
            border-bottom: 1px solid #003300;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .stat-card {{
            background: rgba(0, 15, 0, 0.6);
            padding: 15px;
            border: 1px solid #003300;
            border-left: 4px solid #00ff00;
        }}

        .stat-card h3 {{
            color: #00ff00;
            margin-bottom: 10px;
            font-size: 1em;
            font-weight: 500;
        }}

        .stat-value {{
            font-size: 1.8em;
            font-weight: 600;
            color: #00ff00;
            text-shadow: 0 0 5px #00ff00;
        }}

        .stat-label {{
            color: #009900;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .graph-container {{
            background: rgba(0, 5, 0, 0.8);
            padding: 15px;
            margin: 15px 0;
            border: 1px solid #002200;
        }}

        .graph-title {{
            color: #00ff00;
            margin-bottom: 10px;
            font-size: 1.1em;
            font-weight: 500;
        }}

        .graph {{
            background: rgba(0, 10, 0, 0.5);
            padding: 10px;
            border: 1px solid #001100;
            font-family: 'Courier New', monospace;
            white-space: pre;
            overflow-x: auto;
            color: #00cc00;
            font-size: 0.9em;
            line-height: 1.3;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: rgba(0, 5, 0, 0.5);
            font-size: 0.85em;
        }}

        th {{
            background: rgba(0, 30, 0, 0.8);
            color: #00ff00;
            padding: 10px 8px;
            text-align: left;
            font-weight: 500;
            border: 1px solid #002200;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 8px;
            border: 1px solid #001100;
            color: #00cc00;
            font-weight: 300;
            font-size: 0.9em;
        }}

        tr:nth-child(even) {{
            background: rgba(0, 15, 0, 0.3);
        }}

        tr:hover {{
            background: rgba(0, 255, 0, 0.1);
            color: #00ff00;
        }}

        .status-active {{
            color: #00ff00 !important;
            font-weight: 600;
        }}

        .status-inactive {{
            color: #ff0000 !important;
            font-weight: 600;
        }}

        .status-warning {{
            color: #ffff00 !important;
            font-weight: 600;
        }}

        .status-critical {{
            color: #ff0000 !important;
            font-weight: 600;
            text-shadow: 0 0 3px #ff0000;
        }}

        .scroll-container {{
            overflow-x: auto;
            margin: 15px 0;
            border: 1px solid #003300;
            padding: 5px;
            background: rgba(0, 5, 0, 0.5);
        }}

        .footer {{
            text-align: center;
            color: #006600;
            margin-top: 30px;
            padding: 20px;
            background: rgba(0, 10, 0, 0.8);
            border: 1px solid #002200;
            font-size: 0.8em;
        }}

        .blink {{
            animation: blink 1s infinite;
        }}

        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0; }}
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}

            .header h1 {{
                font-size: 1.5em;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            table {{
                font-size: 0.75em;
            }}

            th, td {{
                padding: 6px 4px;
            }}
        }}

        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: rgba(0, 10, 0, 0.8);
        }}

        ::-webkit-scrollbar-thumb {{
            background: #00ff00;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #00cc00;
        }}

        /* Health meter styles */
        .health-meter {{
            width: 100%;
            height: 20px;
            background: rgba(0, 30, 0, 0.5);
            border: 1px solid #003300;
            margin: 10px 0;
            overflow: hidden;
        }}

        .health-fill {{
            height: 100%;
            background: {health_color};
            transition: width 0.5s ease;
        }}
    </style>
</head>
<body>
    <div class="matrix-bg"></div>
    <div class="scan-line"></div>
    
    <div class="container">
        <div class="header">
            <h1>><span class="blink">_</span> SYSTEM INTELLIGENCE ANALYTICS</h1>
            <div class="creator">ENHANCED SYSTEM SCANNER v4.0 | SABARI425</div>
            <p>> SCAN TIME: {current_time}</p>
            <p>> TARGET: {hostname} | PLATFORM: {platform_info}</p>
            <div class="health-score">
                SYSTEM HEALTH: {health_score}/100
            </div>
        </div>

        <!-- Statistics Dashboard -->
        <div class="section">
            <h2>> STATISTICAL DASHBOARD</h2>
            {stats_html}
        </div>

        <!-- System Graphs -->
        <div class="section">
            <h2>> SYSTEM ANALYTICS & VISUALIZATIONS</h2>
            {graphs_html}
        </div>
"""
    
    # Section names mapping
    section_names = {
        "system_info": "SYSTEM OVERVIEW",
        "hardware_info": "HARDWARE INFORMATION", 
        "process_info": "RUNNING PROCESSES",
        "network_info": "NETWORK ANALYSIS",
        "security_audit": "SECURITY AUDIT",
        "installed_software": "INSTALLED SOFTWARE",
        "system_services": "SYSTEM SERVICES",
        "startup_programs": "STARTUP PROGRAMS",
        "environment_vars": "ENVIRONMENT VARIABLES",
        "hardware_temps": "HARDWARE TEMPERATURES",
        "system_logs": "SYSTEM LOGS",
        "performance_metrics": "PERFORMANCE METRICS",
        "user_accounts": "USER ACCOUNTS",
        "system_drivers": "SYSTEM DRIVERS",
        "wifi_networks": "WIFI NETWORKS"
    }
    
    # Add all data sections
    for data_key, section_name in section_names.items():
        section_data = all_data.get(data_key, [])
        html += generate_section_html(section_name, section_data)
    
    # Add footer
    html += f"""
        <div class="footer">
            <p>> SCAN COMPLETED: {datetime.now().strftime('%H:%M:%S')}</p>
            <p>> ENHANCED SYSTEM ANALYTICS | STATISTICAL VISUALIZATION ENGINE</p>
            <p>> REPORT ID: {timestamp} | GENERATED BY: {getpass.getuser()}</p>
            <p>> SABARI425 ORGANIZATION | ANALYTICS LEVEL: MAXIMUM</p>
        </div>
    </div>
    
    <script>
        // Simple table sorting
        document.addEventListener('DOMContentLoaded', function() {{
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {{
                const headers = table.querySelectorAll('th');
                headers.forEach((header, index) => {{
                    header.style.cursor = 'pointer';
                    header.title = 'Click to sort';
                    header.addEventListener('click', () => {{
                        sortTable(table, index);
                    }});
                }});
            }});
            
            function sortTable(table, column) {{
                const tbody = table.querySelector('tbody');
                if (!tbody) return;
                
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                const isNumeric = (text) => !isNaN(parseFloat(text)) && isFinite(text);
                
                rows.sort((a, b) => {{
                    const aText = a.cells[column]?.textContent.trim() || '';
                    const bText = b.cells[column]?.textContent.trim() || '';
                    
                    if (isNumeric(aText) && isNumeric(bText)) {{
                        return parseFloat(aText) - parseFloat(bText);
                    }}
                    
                    return aText.localeCompare(bText);
                }});
                
                // Remove existing rows
                rows.forEach(row => tbody.removeChild(row));
                
                // Add sorted rows
                rows.forEach(row => tbody.appendChild(row));
            }}
            
            // Animate health meter
            const healthFill = document.querySelector('.health-fill');
            if (healthFill) {{
                const score = {health_score};
                setTimeout(() => {{
                    healthFill.style.width = score + '%';
                }}, 500);
            }}
        }});
    </script>
</body>
</html>
"""
    
    return html

# -------------------------------------------------------------------
#  MAIN EXECUTION FUNCTIONS
# -------------------------------------------------------------------
def print_banner():
    """Display professional hacker-style System Scanner banner"""
    banner = f"""
{Colors.NEON_GREEN}
          ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
          ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
          ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
          ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
          ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
          ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
{Colors.RESET}
{Colors.NEON_GREEN}
          ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗ 
          ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
          ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
          ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
          ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
          ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
{Colors.RESET}
"""
    print(banner)
    print_colored("              ✦     ULTIMATE ANALYTICS EDITION v4.0     ✦                ", Colors.BOLD + Colors.MAGENTA)
    print("\n\n")

def simulate_scan_step(step_name, duration=1, steps=20):
    """Simulate a scanning step with progress bar"""
    print("\n\t", end='')
    print_status(f"Scanning: {step_name}", "SCAN")
    for i in range(steps + 1):
        percent = (i / steps) * 100
        filled = int(30 * i // steps)
        bar = '█' * filled + '░' * (30 - filled)
        
        if percent < 30:
            color = Colors.RED
        elif percent < 70:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
            
        print(f"\r\t\t[{color}{bar}{Colors.RESET}] {percent:.1f}% - {step_name}", end='', flush=True)
        time.sleep(0.03)
    
    print(f"\r\t\t[{Colors.GREEN}{'█'*30}{Colors.RESET}] 100.0% - {step_name}")
    print("\t\t", end='')
    print_status(f"Completed: {step_name}", "SUCCESS")

def display_statistics_preview(all_data):
    """Display statistics preview in terminal"""
    print("\n")
    print_colored("="*80, Colors.BRIGHT_GREEN)
    print_colored("SYSTEM STATISTICS PREVIEW", Colors.GREEN)
    print_colored("="*80, Colors.BRIGHT_GREEN)
    
    stats = calculate_system_statistics(all_data)
    
    if stats:
        print_status("Key Statistics Calculated:", "STATS")
        
        # Process statistics
        if "process_count" in stats:
            print_colored(f"    Total Processes: {stats['process_count']}", Colors.CYAN)
        if "avg_cpu_usage" in stats:
            print_colored(f"    Average CPU Usage: {stats['avg_cpu_usage']:.1f}%", Colors.CYAN)
        if "avg_memory_usage" in stats:
            print_colored(f"    Average Memory Usage: {stats['avg_memory_usage']:.2f}%", Colors.CYAN)
        
        # Hardware statistics
        if "disk_count" in stats:
            print_colored(f"    Storage Devices: {stats['disk_count']}", Colors.CYAN)
        
        # Network statistics
        if "active_network_interfaces" in stats:
            print_colored(f"    Active Network Interfaces: {stats['active_network_interfaces']}", Colors.CYAN)
        
        # Software statistics
        if "installed_software_count" in stats:
            print_colored(f"    Installed Software: {stats['installed_software_count']}", Colors.CYAN)
        
        # Service statistics
        if "running_services" in stats:
            print_colored(f"    Running Services: {stats['running_services']}/{stats.get('total_services', 0)}", Colors.CYAN)
        
        print("\n")
        
        # Display graphs in terminal
        print_status("Generating System Graphs...", "GRAPH")
        print("\n")
        
        # CPU Usage Graph
        processes = all_data.get("process_info", [])
        if processes:
            cpu_graph = generate_cpu_usage_graph(processes)
            if cpu_graph:
                print_colored(cpu_graph, Colors.GREEN)
                print("\n")
        
        # Memory Usage Graph
        if processes:
            mem_graph = generate_memory_usage_graph(processes)
            if mem_graph:
                print_colored(mem_graph, Colors.GREEN)
                print("\n")
        
        # Disk Usage Graph
        hardware = all_data.get("hardware_info", [])
        if hardware:
            disk_graph = generate_disk_usage_graph(hardware)
            if disk_graph:
                print_colored(disk_graph, Colors.GREEN)
                print("\n")
        
        # Health Graph
        health_score = calculate_health_score(all_data)
        health_graph = generate_system_health_graph(health_score)
        if health_graph:
            print_colored(health_graph, Colors.GREEN)

def collect_all_data():
    """Collect all system data"""
    all_data = {}
    
    collection_functions = {
        "system_info": get_comprehensive_system_info,
        "hardware_info": get_extended_hardware_info,
        "process_info": get_detailed_process_info,
        "network_info": get_network_analysis_extended,
        "security_audit": get_security_audit,
        "installed_software": get_installed_software_extended,
        "system_services": get_system_services_extended,
        "startup_programs": get_startup_programs,
        "environment_vars": get_system_environment_extended,
        "hardware_temps": get_hardware_temperatures,
        "system_logs": get_system_logs_extended,
        "performance_metrics": get_performance_metrics,
        "user_accounts": get_user_accounts_extended,
        "system_drivers": get_system_drivers_extended,
        "wifi_networks": get_wifi_networks_extended
    }
    
    for name, func in collection_functions.items():
        try:
            print_status(f"Collecting {name.replace('_', ' ')}...", "DATA", "Please wait")
            all_data[name] = func()
            print_status(f"Collected {len(all_data[name]) if isinstance(all_data[name], list) else 'data'} items", "SUCCESS", name)
        except Exception as e:
            print_status(f"Failed to collect {name}: {str(e)[:50]}", "ERROR")
            all_data[name] = [{"Error": f"Collection failed: {str(e)[:50]}"}]
    
    return all_data

def main():
    print_banner()
    
    try:
        # Simulate scanning steps
        scan_steps = [
            "System Hardware Detection",
            "Memory & Storage Analysis", 
            "Network Interface Scanning",
            "Process Enumeration",
            "Security Configuration Audit",
            "Software Inventory Collection",
            "Service & Driver Analysis",
            "Environment & Configuration",
            "Performance Metrics Gathering",
            "Statistical Analysis",
            "Generating Analytics Report"
        ]
        
        for step in scan_steps:
            simulate_scan_step(step, steps=15)
        
        print("\n")
        print_colored("="*80, Colors.BRIGHT_GREEN)
        print(Colors.rainbow_text("GENERATING ADVANCED SYSTEM ANALYTICS REPORT"))
        print_colored("="*80, Colors.BRIGHT_GREEN)
        print("\n")
        
        # Collect all data
        all_data = collect_all_data()
        
        # Display statistics preview
        display_statistics_preview(all_data)
        
        # Generate HTML report with graphs
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_folder):
            downloads_folder = os.getcwd()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_filename = f"System_Analytics_Report_{timestamp}.html"
        html_path = os.path.join(downloads_folder, html_filename)
        
        # Health score calculation
        health_score = calculate_health_score(all_data)
        
        # Generate HTML content with graphs
        html_content = generate_html_with_graphs(all_data, health_score, timestamp)
        
        # Write to file
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print_status(f"Analytics report generated successfully: {html_path}", "SUCCESS")
            
            # Try to open the report
            try:
                if platform.system() == "Windows":
                    os.startfile(html_path)
                    print_status("Opening analytics report in default browser...", "INFO")
                elif platform.system() == "Darwin":
                    subprocess.run(["open", html_path], check=False)
                    print_status("Opening analytics report in default browser...", "INFO")
                else:
                    subprocess.run(["xdg-open", html_path], check=False)
                    print_status("Opening analytics report in default browser...", "INFO")
            except:
                print_status("Could not open browser automatically", "WARNING")
                print_status(f"Please open manually: {html_path}", "INFO")
            
            # Show file info
            try:
                file_size = os.path.getsize(html_path)
                print_status(f"Report size: {format_bytes(file_size)}", "DATA")
            except:
                pass
            
            print_colored("\n" + "━"*80, Colors.GREEN)
            print_status("Advanced System Analytics completed successfully!", "SUCCESS")
            print_colored("━"*80 + "\n", Colors.GREEN)
            
            # Show analytics features
            print_status("ANALYTICS FEATURES INCLUDED:", "INFO")
            features = [
                "✓ Statistical Dashboard", "✓ CPU Usage Graphs", "✓ Memory Usage Graphs",
                "✓ Disk Usage Visualization", "✓ Service Status Charts", "✓ Network Activity Graphs",
                "✓ Health Score Analytics", "✓ Process Distribution", "✓ Risk Assessment",
                "✓ Performance Metrics", "✓ Comparative Analysis", "✓ Trend Visualization"
            ]
            
            for i in range(0, len(features), 3):
                line = features[i:i+3]
                print_colored("    " + " | ".join(line), Colors.GREEN)
            
            print("\n\n")
            
        except Exception as e:
            print_status(f"Failed to write HTML file: {str(e)}", "ERROR")
            
    except KeyboardInterrupt:
        print("\n")
        print_status("Scan interrupted by user", "WARNING")
        print_status("Partial report may have been generated", "INFO")
    except Exception as e:
        print("\n")
        print_status(f"Fatal error during scan: {str(e)}", "ERROR")
        import traceback
        traceback.print_exc()
    
    # Keep window open if run directly
    if platform.system() == "Windows":
        try:
            input("\nPress Enter to exit...")
        except:
            pass

if __name__ == "__main__":
    main()
