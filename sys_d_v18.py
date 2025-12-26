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
from collections import OrderedDict, defaultdict
import winreg  # Windows registry access
import ctypes  # For Windows API calls

# -------------------------------------------------------------------
#  AUTO-INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------------------------------------------
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"[*] Installing missing package: {pkg}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print(f"[!] Failed to install {pkg}")

# Enhanced package list - only essential ones
required_packages = [
    "psutil", "tabulate", "colorama"
]

for package in required_packages:
    install_package(package)

import psutil
from tabulate import tabulate
import colorama
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init()

# Try to import optional packages
try:
    import wmi
    WMI_AVAILABLE = True
except:
    WMI_AVAILABLE = False

try:
    import GPUtil
    GPU_AVAILABLE = True
except:
    GPU_AVAILABLE = False

try:
    import win32api
    import win32con
    import win32security
    WIN32_AVAILABLE = True
except:
    WIN32_AVAILABLE = False

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
    def rainbow(text):
        """Create rainbow text effect - FIXED METHOD"""
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
        text = Colors.rainbow(text)
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
        "HARDWARE": {"color": Colors.YELLOW, "icon": "[💻]"}
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

def get_file_hash(filepath):
    """Calculate file hash"""
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except:
        return None

# -------------------------------------------------------------------
#  PARALLEL DATA COLLECTION WITH THREADING
# -------------------------------------------------------------------
class DataCollector:
    def __init__(self):
        self.results = {}
        self.queue = queue.Queue()
        
    def collect_parallel(self, functions):
        """Collect data from multiple functions in parallel"""
        threads = []
        
        def worker(func, name):
            try:
                result = func()
                self.queue.put((name, result))
            except Exception as e:
                self.queue.put((name, {"error": str(e)}))
        
        for name, func in functions.items():
            thread = threading.Thread(target=worker, args=(func, name))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        while not self.queue.empty():
            name, result = self.queue.get()
            self.results[name] = result
        
        return self.results

# -------------------------------------------------------------------
#  ENHANCED SYSTEM INFORMATION COLLECTION
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
    if platform.system() == "Windows":
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
            
            try:
                info["Build Branch"] = winreg.QueryValueEx(key, "BuildBranch")[0]
            except:
                info["Build Branch"] = "Unknown"
                
            try:
                info["Build Lab"] = winreg.QueryValueEx(key, "BuildLabEx")[0]
            except:
                info["Build Lab"] = "Unknown"
                
            try:
                info["Registered Owner"] = winreg.QueryValueEx(key, "RegisteredOwner")[0]
            except:
                info["Registered Owner"] = "Unknown"
                
            try:
                info["Registered Organization"] = winreg.QueryValueEx(key, "RegisteredOrganization")[0]
            except:
                info["Registered Organization"] = "Unknown"
                
            winreg.CloseKey(key)
        except Exception as e:
            info["Windows Registry Error"] = str(e)[:50]
    
    # Uptime
    try:
        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        info["Boot Time"] = datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')
        info["Uptime"] = str(uptime).split('.')[0]
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
    
    # GPU Information (if available)
    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            for i, gpu in enumerate(gpus):
                hardware.append({
                    "Category": "GPU",
                    "Name": gpu.name,
                    "Load": f"{gpu.load*100:.1f}%" if gpu.load else "N/A",
                    "Memory Used": f"{gpu.memoryUsed} MB" if gpu.memoryUsed else "N/A",
                    "Memory Total": f"{gpu.memoryTotal} MB" if gpu.memoryTotal else "N/A",
                    "Temperature": f"{gpu.temperature} °C" if gpu.temperature else "N/A"
                })
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
    
    return processes[:50]  # Return top 50 processes

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
        for i, conn in enumerate(connections[:10]):  # Limit to 10 connections
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
        try:
            # Check Windows Defender
            try:
                defender_status = subprocess.run(
                    ["powershell", "-Command", "Get-MpComputerStatus"],
                    capture_output=True, text=True, timeout=10
                )
                if defender_status.returncode == 0 and "True" in defender_status.stdout:
                    security_info.append({
                        "Security Feature": "Windows Defender",
                        "Status": "Enabled",
                        "Risk": "Low"
                    })
                else:
                    security_info.append({
                        "Security Feature": "Windows Defender",
                        "Status": "Disabled",
                        "Risk": "High"
                    })
            except:
                security_info.append({
                    "Security Feature": "Windows Defender",
                    "Status": "Unknown",
                    "Risk": "Medium"
                })
            
            # Check Firewall
            try:
                firewall_status = subprocess.run(
                    ["netsh", "advfirewall", "show", "allprofiles"],
                    capture_output=True, text=True, timeout=10
                )
                if firewall_status.returncode == 0 and "ON" in firewall_status.stdout:
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
            
            # Check UAC
            try:
                uac_status = subprocess.run(
                    ["reg", "query", r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "/v", "EnableLUA"],
                    capture_output=True, text=True, timeout=10
                )
                if uac_status.returncode == 0 and "0x1" in uac_status.stdout:
                    security_info.append({
                        "Security Feature": "UAC",
                        "Status": "Enabled",
                        "Risk": "Low"
                    })
                else:
                    security_info.append({
                        "Security Feature": "UAC",
                        "Status": "Disabled",
                        "Risk": "High"
                    })
            except:
                security_info.append({
                    "Security Feature": "UAC",
                    "Status": "Unknown",
                    "Risk": "Medium"
                })
                
        except Exception as e:
            security_info.append({
                "Security Feature": "Security Audit",
                "Status": f"Error: {str(e)[:30]}",
                "Risk": "Unknown"
            })
    else:
        security_info.append({
            "Security Feature": "Platform",
            "Status": f"Non-Windows: {platform.system()}",
            "Risk": "N/A"
        })
    
    # Check for admin privileges
    try:
        if platform.system() == "Windows":
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            is_admin = os.getuid() == 0
        
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
    
    return security_info

def get_installed_software_extended():
    """Get detailed installed software information"""
    software_list = []
    
    if platform.system() == "Windows":
        try:
            # Check both 32-bit and 64-bit registry locations
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            
                            # Try to get display name
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            except:
                                display_name = None
                            
                            if display_name:  # Only add if it has a display name
                                software_info = {
                                    "Name": (display_name[:50] + "...") if len(display_name) > 50 else display_name,
                                    "Version": "N/A",
                                    "Publisher": "N/A",
                                    "Install Date": "N/A",
                                    "Install Location": "N/A",
                                    "Registry Key": subkey_name[:20] + "..." if len(subkey_name) > 20 else subkey_name
                                }
                                
                                # Try to get version
                                try:
                                    software_info["Version"] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except:
                                    pass
                                
                                # Try to get publisher
                                try:
                                    software_info["Publisher"] = winreg.QueryValueEx(subkey, "Publisher")[0]
                                except:
                                    pass
                                
                                # Try to get install date
                                try:
                                    software_info["Install Date"] = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                except:
                                    pass
                                
                                # Try to get install location
                                try:
                                    location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    if location and len(location) > 30:
                                        software_info["Install Location"] = "..." + location[-27:]
                                    else:
                                        software_info["Install Location"] = location
                                except:
                                    pass
                                
                                software_list.append(software_info)
                            
                            winreg.CloseKey(subkey)
                        except:
                            continue
                    
                    winreg.CloseKey(key)
                except:
                    continue
            
            # Remove duplicates based on name
            seen = set()
            unique_software = []
            for item in software_list:
                identifier = item["Name"]
                if identifier not in seen:
                    seen.add(identifier)
                    unique_software.append(item)
            
            software_list = unique_software[:30]  # Limit to 30 entries
            
        except Exception as e:
            software_list.append({
                "Name": f"Error: {str(e)[:50]}",
                "Version": "N/A",
                "Publisher": "N/A"
            })
    else:
        software_list.append({
            "Name": f"Non-Windows system: {platform.system()}",
            "Version": "N/A",
            "Publisher": "N/A"
        })
    
    return software_list

def get_system_services_extended():
    """Get detailed service information"""
    services = []
    
    if platform.system() == "Windows":
        try:
            # Use psutil for service information
            for service in psutil.win_service_iter():
                try:
                    info = service.as_dict()
                    services.append({
                        "Name": info.get('name', 'N/A')[:20],
                        "Display Name": info.get('display_name', 'N/A')[:30],
                        "State": info.get('status', 'N/A'),
                        "Start Mode": info.get('start_type', 'N/A'),
                        "Start Name": info.get('username', 'N/A')[:20],
                        "Path": (info.get('binpath', 'N/A')[:30] + "...") if info.get('binpath') and len(info.get('binpath', '')) > 30 else info.get('binpath', 'N/A'),
                        "Process ID": info.get('pid', 'N/A')
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
        services.append({
            "Name": f"Non-Windows: {platform.system()}",
            "Display Name": "Services not available",
            "State": "N/A",
            "Start Mode": "N/A"
        })
    
    return services[:20]  # Limit to 20 services

def get_startup_programs():
    """Get startup programs"""
    startup_programs = []
    
    if platform.system() == "Windows":
        startup_paths = [
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs\StartUp"),
            r"C:\Users\All Users\Microsoft\Windows\Start Menu\Programs\Startup"
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
    
    return startup_programs[:15]  # Limit to 15 entries

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
    
    return env_vars[:25]  # Limit to 25 entries

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
    
    return temps[:10]  # Limit to 10 entries

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
            # Get local users using net command
            output = subprocess.run(
                ["net", "user"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10
            )
            
            if output.returncode == 0:
                lines = output.stdout.split('\n')
                user_list = []
                in_user_section = False
                
                for line in lines:
                    line = line.strip()
                    if "User accounts for" in line:
                        in_user_section = True
                        continue
                    if "The command completed" in line:
                        break
                    
                    if in_user_section and line:
                        # Extract usernames
                        words = line.split()
                        for word in words:
                            if word and word not in ["User", "accounts", "for", "\\", "---------"]:
                                user_list.append(word)
                
                # Get details for each user (limited to 5)
                for username in user_list[:5]:
                    try:
                        user_output = subprocess.run(
                            ["net", "user", username],
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='ignore',
                            timeout=10
                        )
                        
                        user_details = {}
                        for line in user_output.stdout.split('\n'):
                            line_lower = line.lower()
                            if 'full name' in line_lower:
                                user_details['Full Name'] = line.split('Full Name')[1].strip()
                            elif 'account active' in line_lower:
                                user_details['Active'] = 'Yes' if 'yes' in line_lower else 'No'
                            elif 'last logon' in line_lower:
                                user_details['Last Logon'] = line.split('Last logon')[1].strip()
                        
                        users.append({
                            "Username": username[:20],
                            "Full Name": user_details.get('Full Name', 'N/A')[:30],
                            "Active": user_details.get('Active', 'N/A'),
                            "Last Logon": user_details.get('Last Logon', 'N/A')[:30]
                        })
                        
                    except:
                        users.append({
                            "Username": username[:20],
                            "Full Name": "Error retrieving",
                            "Active": "N/A",
                            "Last Logon": "N/A"
                        })
            else:
                users.append({
                    "Username": "net command failed",
                    "Full Name": f"Return code: {output.returncode}",
                    "Active": "N/A",
                    "Last Logon": "N/A"
                })
        
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
                "Full Name": "N/A",
                "Active": "Yes",
                "Last Logon": "Current session"
            })
        except:
            users.append({
                "Username": f"Non-Windows: {platform.system()}",
                "Full Name": "N/A",
                "Active": "N/A",
                "Last Logon": "N/A"
            })
    
    return users

def get_system_drivers_extended():
    """Get detailed driver information"""
    drivers = []
    
    if platform.system() == "Windows":
        try:
            output = subprocess.run(
                ["driverquery", "/v", "/fo", "csv"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=15
            )
            
            if output.returncode == 0 and output.stdout:
                lines = output.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse CSV
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            # Simple CSV parsing
                            parts = []
                            in_quotes = False
                            current_part = ""
                            
                            for char in line:
                                if char == '"':
                                    in_quotes = not in_quotes
                                elif char == ',' and not in_quotes:
                                    parts.append(current_part.strip('"'))
                                    current_part = ""
                                else:
                                    current_part += char
                            
                            if current_part:
                                parts.append(current_part.strip('"'))
                            
                            if len(parts) >= 6:
                                drivers.append({
                                    "Module Name": parts[0][:30],
                                    "Display Name": parts[1][:40],
                                    "Driver Type": parts[2][:20],
                                    "Start Mode": parts[3][:15],
                                    "State": parts[4][:15],
                                    "Status": parts[5][:20] if len(parts) > 5 else "N/A"
                                })
            
            # Limit to 15 drivers
            drivers = drivers[:15]
            
        except Exception as e:
            drivers.append({
                "Module Name": f"Error: {str(e)[:30]}",
                "Display Name": "Driver query failed",
                "Driver Type": "N/A",
                "Start Mode": "N/A"
            })
    else:
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
            profiles_output = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10
            )
            
            if profiles_output.returncode == 0:
                profiles = []
                for line in profiles_output.stdout.split('\n'):
                    if "All User Profile" in line and ":" in line:
                        profile_name = line.split(":")[1].strip()
                        if profile_name:
                            profiles.append(profile_name)
                
                # Get details for each profile (limited to 5)
                for profile in profiles[:5]:
                    try:
                        profile_output = subprocess.run(
                            ["netsh", "wlan", "show", "profile", f"name={profile}", "key=clear"],
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='ignore',
                            timeout=10
                        )
                        
                        details = {}
                        if profile_output.returncode == 0:
                            for line in profile_output.stdout.split('\n'):
                                line = line.strip()
                                if "Key Content" in line and ":" in line:
                                    details['Password'] = line.split(":")[1].strip()
                                elif "Authentication" in line and ":" in line:
                                    details['Auth'] = line.split(":")[1].strip()
                                elif "Cipher" in line and ":" in line:
                                    details['Cipher'] = line.split(":")[1].strip()
                        
                        wifi_networks.append({
                            "SSID": profile[:30],
                            "Authentication": details.get('Auth', 'Unknown')[:20],
                            "Cipher": details.get('Cipher', 'Unknown')[:20],
                            "Password": details.get('Password', 'Not stored')[:30]
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
                    "SSID": "netsh command failed",
                    "Authentication": f"Code: {profiles_output.returncode}",
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
        wifi_networks.append({
            "SSID": f"Non-Windows: {platform.system()}",
            "Authentication": "WiFi info not available",
            "Cipher": "N/A",
            "Password": "N/A"
        })
    
    return wifi_networks

# -------------------------------------------------------------------
#  ENHANCED HTML REPORT GENERATION
# -------------------------------------------------------------------
def generate_enhanced_html_report():
    """Generate comprehensive HTML report with all collected data"""
    
    print_status("Starting comprehensive system intelligence scan...", "SCAN")
    
    # Collect all data sequentially (safer than parallel)
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
        except Exception as e:
            print_status(f"Failed to collect {name}: {str(e)[:50]}", "ERROR")
            all_data[name] = [{"Error": f"Collection failed: {str(e)[:50]}"}]
    
    # Generate HTML report
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.exists(downloads_folder):
        downloads_folder = os.getcwd()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_filename = f"System_Intelligence_Report_{timestamp}.html"
    html_path = os.path.join(downloads_folder, html_filename)
    
    # Health score calculation (simplified)
    health_score = calculate_health_score(all_data)
    
    # Generate HTML content
    html_content = generate_html_content(all_data, health_score, timestamp)
    
    # Write to file
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print_status(f"Report generated successfully: {html_path}", "SUCCESS")
        return html_path
    except Exception as e:
        print_status(f"Failed to write HTML file: {str(e)}", "ERROR")
        return None

def calculate_health_score(data):
    """Calculate system health score based on collected data"""
    score = 85  # Base score
    
    try:
        # Check memory usage
        for item in data.get("hardware_info", []):
            if item.get("Category") == "MEMORY" and "Usage" in item:
                usage_str = item["Usage"]
                if "%" in usage_str:
                    usage = float(usage_str.replace("%", "").strip())
                    if usage > 90:
                        score -= 20
                    elif usage > 80:
                        score -= 10
                    elif usage > 70:
                        score -= 5
        
        # Check disk usage
        for item in data.get("hardware_info", []):
            if item.get("Category") == "DISK" and "Usage" in item:
                usage_str = item["Usage"]
                if "%" in usage_str:
                    usage = float(usage_str.replace("%", "").strip())
                    if usage > 95:
                        score -= 15
                    elif usage > 90:
                        score -= 10
                    elif usage > 85:
                        score -= 5
        
        # Check security
        for item in data.get("security_audit", []):
            if item.get("Risk") == "High":
                score -= 5
            elif item.get("Status") == "Disabled" and "enabled" in item.get("Security Feature", "").lower():
                score -= 3
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
    except:
        score = 85  # Default if calculation fails
    
    return score

def generate_html_content(all_data, health_score, timestamp):
    """Generate HTML content with all data"""
    
    health_color = get_health_color(health_score)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hostname = socket.gethostname() if hasattr(socket, 'gethostname') else "Unknown"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Intelligence Report</title>
    <style>
        /* Your existing CSS styles */
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
            max-width: 1400px;
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

            table {{
                font-size: 0.75em;
            }}

            th, td {{
                padding: 6px 4px;
            }}
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
            background: #00ff00;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #00cc00;
        }}
    </style>
</head>
<body>
    <div class="matrix-bg"></div>
    <div class="scan-line"></div>
    
    <div class="container">
        <div class="header">
            <h1>><span class="blink">_</span> SYSTEM INTELLIGENCE REPORT</h1>
            <div class="creator">ENHANCED SYSTEM SCANNER v2.0 | SABARI425</div>
            <p>> SCAN TIME: {current_time}</p>
            <p>> TARGET: {hostname} | PLATFORM: {platform.platform()}</p>
            <div class="health-score">
                SYSTEM HEALTH: {health_score}/100
            </div>
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
            <p>> ENHANCED SYSTEM SCANNER | MAXIMUM INFORMATION COLLECTION</p>
            <p>> REPORT ID: {timestamp} | GENERATED BY: {getpass.getuser()}</p>
            <p>> SABARI425 ORGANIZATION | SECURITY LEVEL: MAXIMUM</p>
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
            
            // Add scan line effect
            const scanLine = document.querySelector('.scan-line');
            setInterval(() => {{
                scanLine.style.top = '0%';
                setTimeout(() => {{
                    scanLine.style.transition = 'top 3s linear';
                    scanLine.style.top = '100%';
                }}, 100);
            }}, 4000);
        }});
    </script>
</body>
</html>
"""
    
    return html

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
            for key, value in data:
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
                        
                        elif 'password' in header_lower and cell_lower != 'not stored' and 'error' not in cell_lower:
                            cell_class = "status-active"
                        
                        if cell_class:
                            html += f'<td class="{cell_class}">{cell}</td>'
                        else:
                            html += f'<td>{cell}</td>'
                    html += '</tr>'
                
                html += '</tbody></table></div>'
    
    html += '</div>'
    return html

def get_health_color(score):
    """Get health color based on score"""
    if score >= 80:
        return "linear-gradient(135deg, #00ff00 0%, #00cc00 100%)"
    elif score >= 60:
        return "linear-gradient(135deg, #ffff00 0%, #cccc00 100%)"
    else:
        return "linear-gradient(135deg, #ff0000 0%, #cc0000 100%)"

# -------------------------------------------------------------------
#  MAIN EXECUTION
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
    print_colored("                     ✦     ..... SABARI425 .....     ✦                ", Colors.BOLD + Colors.MAGENTA)
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

if __name__ == "__main__":
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
            "Generating Intelligence Report"
        ]
        
        for step in scan_steps:
            simulate_scan_step(step, steps=15)
        
        print("\n")
        print_colored("="*80, Colors.BRIGHT_GREEN)
        print_colored("GENERATING COMPREHENSIVE SYSTEM INTELLIGENCE REPORT", Colors.RAINBOW)
        print_colored("="*80, Colors.BRIGHT_GREEN)
        print("\n")
        
        # Generate the report
        report_path = generate_enhanced_html_report()
        
        if report_path:
            print_colored("\n" + "═"*80, Colors.BRIGHT_GREEN)
            print_colored("SCAN COMPLETED SUCCESSFULLY", Colors.GREEN)
            print_colored("═"*80, Colors.BRIGHT_GREEN)
            
            print_status(f"Report saved to: {report_path}", "SUCCESS")
            
            # Try to open the report
            try:
                if platform.system() == "Windows":
                    os.startfile(report_path)
                    print_status("Opening report in default browser...", "INFO")
                elif platform.system() == "Darwin":
                    subprocess.run(["open", report_path], check=False)
                    print_status("Opening report in default browser...", "INFO")
                else:
                    subprocess.run(["xdg-open", report_path], check=False)
                    print_status("Opening report in default browser...", "INFO")
            except:
                print_status("Could not open browser automatically", "WARNING")
                print_status(f"Please open manually: {report_path}", "INFO")
            
            # Show file info
            try:
                file_size = os.path.getsize(report_path)
                print_status(f"Report size: {format_bytes(file_size)}", "DATA")
            except:
                pass
            
            print_colored("\n" + "━"*80, Colors.GREEN)
            print_status("Enhanced System Scanner completed successfully!", "SUCCESS")
            print_colored("━"*80 + "\n", Colors.GREEN)
            
            # Show sections collected
            print_status("REPORT SECTIONS INCLUDED:", "INFO")
            sections = [
                "✓ System Overview", "✓ Hardware Information", "✓ Running Processes",
                "✓ Network Analysis", "✓ Security Audit", "✓ Installed Software",
                "✓ System Services", "✓ Startup Programs", "✓ Environment Variables",
                "✓ Hardware Temperatures", "✓ System Logs", "✓ Performance Metrics",
                "✓ User Accounts", "✓ System Drivers", "✓ WiFi Networks"
            ]
            
            for i in range(0, len(sections), 3):
                line = sections[i:i+3]
                print_colored("    " + " | ".join(line), Colors.GREEN)
            
            print("\n\n")
            
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
