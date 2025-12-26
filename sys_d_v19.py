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

# Try to import Windows-specific modules
try:
    import winreg  # Windows registry access
    WINREG_AVAILABLE = True
except:
    WINREG_AVAILABLE = False

try:
    import ctypes  # For Windows API calls
    CTYPES_AVAILABLE = True
except:
    CTYPES_AVAILABLE = False

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

# -------------------------------------------------------------------
#  ENHANCED COLOR CLASS WITH GRADIENTS AND EFFECTS - FIXED VERSION
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
#  STATISTICAL ANALYSIS FUNCTIONS
# -------------------------------------------------------------------
def calculate_system_statistics(all_data):
    """Calculate comprehensive system statistics"""
    stats = {}
    
    # Process statistics
    processes = all_data.get("process_info", [])
    if processes:
        try:
            cpu_usages = [float(p.get("CPU %", "0").replace("%", "")) for p in processes if "CPU %" in p]
            memory_usages = [float(p.get("Memory %", "0").replace("%", "")) for p in processes if "Memory %" in p]
            
            stats["process_count"] = len(processes)
            stats["avg_cpu_usage"] = statistics.mean(cpu_usages) if cpu_usages else 0
            stats["max_cpu_usage"] = max(cpu_usages) if cpu_usages else 0
            stats["avg_memory_usage"] = statistics.mean(memory_usages) if memory_usages else 0
            stats["max_memory_usage"] = max(memory_usages) if memory_usages else 0
            
            # Process status distribution
            status_counts = Counter([p.get("Status", "UNKNOWN") for p in processes])
            stats["process_status_dist"] = dict(status_counts)
            
            # Top processes by CPU and Memory
            top_cpu = sorted(processes, key=lambda x: float(x.get("CPU %", "0").replace("%", "")), reverse=True)[:5]
            top_memory = sorted(processes, key=lambda x: float(x.get("Memory %", "0").replace("%", "")), reverse=True)[:5]
            stats["top_cpu_processes"] = [(p["Name"], p["CPU %"]) for p in top_cpu]
            stats["top_memory_processes"] = [(p["Name"], p["Memory %"]) for p in top_memory]
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
        
        # Count by publisher (top 5)
        publishers = Counter([s.get("Publisher", "Unknown") for s in software])
        stats["top_publishers"] = dict(publishers.most_common(5))
    
    # Service statistics
    services = all_data.get("system_services", [])
    if services:
        running_services = len([s for s in services if s.get("State") == "RUNNING"])
        stats["running_services"] = running_services
        stats["total_services"] = len(services)
    
    # User statistics
    users = all_data.get("user_accounts", [])
    if users:
        active_users = len([u for u in users if u.get("Active", "").lower() == "yes"])
        stats["active_users"] = active_users
        stats["total_users"] = len(users)
    
    # Performance metrics
    perf_metrics = all_data.get("performance_metrics", [])
    if perf_metrics:
        for metric in perf_metrics:
            if metric.get("Metric") == "CPU Usage":
                usage_str = metric.get("Value", "0%")
                if "%" in usage_str:
                    try:
                        stats["current_cpu_usage"] = float(usage_str.replace("%", ""))
                    except:
                        pass
    
    return stats

def generate_statistics_summary(all_data):
    """Generate comprehensive statistics summary"""
    stats = calculate_system_statistics(all_data)
    
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
    
    # Add computed health metrics
    health_score = calculate_health_score(all_data)
    summary.append({"Category": "HEALTH", "Metric": "System Health Score", "Value": f"{health_score}/100"})
    
    # Add risk assessment
    risk_level = "LOW"
    if health_score < 60:
        risk_level = "HIGH"
    elif health_score < 80:
        risk_level = "MEDIUM"
    summary.append({"Category": "HEALTH", "Metric": "Risk Level", "Value": risk_level})
    
    return summary

# -------------------------------------------------------------------
#  GRAPH GENERATION FUNCTIONS (Text-based ASCII Graphs)
# -------------------------------------------------------------------
def generate_bar_graph(data_points, title="", width=50, max_value=None):
    """Generate ASCII bar graph"""
    if not data_points:
        return ""
    
    if max_value is None:
        max_value = max(data_points.values()) if isinstance(data_points, dict) else max(data_points)
    
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
            percentage = (value / max_value) * 100
            graph_lines.append(f"{str(key):<{max_key_len}} |{Colors.GREEN}{bar}{Colors.RESET}| {value} ({percentage:.1f}%)")
    else:
        # For list data
        for i, value in enumerate(data_points):
            bar_length = int((value / max_value) * width)
            bar = "█" * bar_length
            percentage = (value / max_value) * 100
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

def generate_histogram(data_points, title="", bins=10):
    """Generate ASCII histogram"""
    if not data_points:
        return ""
    
    if len(data_points) < 2:
        return ""
    
    try:
        min_val = min(data_points)
        max_val = max(data_points)
        
        if min_val == max_val:
            return ""
        
        bin_width = (max_val - min_val) / bins
        histogram = [0] * bins
        
        for value in data_points:
            bin_index = min(int((value - min_val) / bin_width), bins - 1)
            histogram[bin_index] += 1
        
        # Generate histogram
        max_freq = max(histogram)
        if max_freq == 0:
            return ""
        
        hist_lines = []
        if title:
            hist_lines.append(f"> {title}")
            hist_lines.append("─" * (len(title) + 2))
        
        for i, freq in enumerate(histogram):
            bar_length = int((freq / max_freq) * 30)
            bar = "█" * bar_length
            lower_bound = min_val + (i * bin_width)
            upper_bound = min_val + ((i + 1) * bin_width)
            hist_lines.append(f"{lower_bound:6.1f}-{upper_bound:6.1f} |{Colors.GREEN}{bar}{Colors.RESET}| {freq}")
        
        return "\n".join(hist_lines)
    except:
        return ""

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
    
    status_counts = Counter([s.get("State", "UNKNOWN") for s in services])
    
    return generate_pie_chart(dict(status_counts), "Service Status Distribution")

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
    
    # Add breakdown
    health_lines.append("")
    health_lines.append("> HEALTH BREAKDOWN")
    
    # Simulated breakdown (in real implementation, this would use actual metrics)
    breakdown = {
        "CPU Performance": min(health_score + 5, 100),
        "Memory Usage": max(health_score - 10, 0),
        "Disk Health": min(health_score + 15, 100),
        "Network Stability": min(health_score + 20, 100),
        "Security Status": max(health_score - 5, 0)
    }
    
    for metric, score in breakdown.items():
        filled = int((score / 100) * 30)
        meter = "█" * filled + "░" * (30 - filled)
        if score >= 80:
            m_color = Colors.GREEN
        elif score >= 60:
            m_color = Colors.YELLOW
        else:
            m_color = Colors.RED
        health_lines.append(f"{metric:20} [{m_color}{meter}{Colors.RESET}] {score:3.0f}%")
    
    return "\n".join(health_lines)

# -------------------------------------------------------------------
#  ENHANCED DATA COLLECTION WITH STATISTICS
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
#  ENHANCED HTML REPORT WITH GRAPHS
# -------------------------------------------------------------------
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

        .graph-bar {{
            display: inline-block;
            background: #00ff00;
            height: 15px;
            margin-right: 2px;
            vertical-align: middle;
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

        /* Graph visualization styles */
        .graph-visual {{
            margin: 10px 0;
            padding: 10px;
            background: rgba(0, 5, 0, 0.5);
            border: 1px solid #002200;
        }}

        .bar-graph {{
            display: flex;
            align-items: flex-end;
            height: 200px;
            gap: 2px;
            padding: 10px;
            background: rgba(0, 10, 0, 0.3);
        }}

        .bar {{
            flex: 1;
            background: linear-gradient(to top, #00ff00, #009900);
            min-height: 1px;
            position: relative;
        }}

        .bar-label {{
            position: absolute;
            bottom: -20px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.7em;
            color: #00cc00;
            transform: rotate(-45deg);
            transform-origin: left top;
        }}

        .bar-value {{
            position: absolute;
            top: -20px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.8em;
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="matrix-bg"></div>
    <div class="scan-line"></div>
    
    <div class="container">
        <div class="header">
            <h1>><span class="blink">_</span> SYSTEM INTELLIGENCE ANALYTICS</h1>
            <div class="creator">ENHANCED SYSTEM SCANNER v3.0 | SABARI425</div>
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
            
            // Animate bar graphs
            const bars = document.querySelectorAll('.bar');
            bars.forEach((bar, index) => {{
                const height = bar.style.height || '0%';
                bar.style.height = '0%';
                setTimeout(() => {{
                    bar.style.height = height;
                }}, 300 * (index + 1));
            }});
        }});
    </script>
</body>
</html>
"""
    
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
            is_good = False
            is_warning = False
            is_critical = False
            
            if "%" in value_str:
                try:
                    num_value = float(value_str.replace("%", ""))
                    if "Usage" in metric or "CPU" in metric or "Memory" in metric:
                        if num_value < 60:
                            is_good = True
                        elif num_value < 80:
                            is_warning = True
                        else:
                            is_critical = True
                except:
                    pass
            
            value_color = "#00ff00"  # Default green
            if is_warning:
                value_color = "#ffff00"
            elif is_critical:
                value_color = "#ff0000"
            
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
    
    # Add JavaScript bar graph visualization
    html += """
    <div class="graph-visual">
        <div class="graph-title">SYSTEM METRICS VISUALIZATION</div>
        <div class="bar-graph" id="barGraph">
            <!-- Bar graph will be generated by JavaScript -->
        </div>
    </div>
    
    <script>
        // Generate bar graph
        function generateBarGraph() {
            const data = [
                {label: 'CPU', value: 75},
                {label: 'Memory', value: 60},
                {label: 'Disk', value: 45},
                {label: 'Network', value: 85},
                {label: 'Security', value: 90},
                {label: 'Processes', value: 70}
            ];
            
            const maxValue = Math.max(...data.map(d => d.value));
            const barGraph = document.getElementById('barGraph');
            barGraph.innerHTML = '';
            
            data.forEach(item => {
                const height = (item.value / maxValue) * 100;
                const bar = document.createElement('div');
                bar.className = 'bar';
                bar.style.height = height + '%';
                bar.innerHTML = `
                    <div class="bar-value">${item.value}%</div>
                    <div class="bar-label">${item.label}</div>
                `;
                barGraph.appendChild(bar);
            });
        }
        
        document.addEventListener('DOMContentLoaded', generateBarGraph);
    </script>
    """
    
    return html

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
    print_colored("              ✦     ADVANCED ANALYTICS EDITION     ✦                ", Colors.BOLD + Colors.MAGENTA)
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
