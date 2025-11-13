import platform

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


print("=== System Information ===")
print("System:", platform.system())
print("Node Name:", platform.node())
print("Release:", platform.release())
print("Version:", platform.version())
print("Machine:", platform.machine())
print("Processor:", platform.processor())

import psutil

print("\n=== CPU Info ===")
print("Physical cores:", psutil.cpu_count(logical=False))
print("Total cores:", psutil.cpu_count(logical=True))
print("CPU Frequency:", psutil.cpu_freq().current, "MHz")
print("CPU Usage per core:", psutil.cpu_percent(percpu=True, interval=1))
print("Total CPU Usage:", psutil.cpu_percent(), "%")

print("\n=== Memory Info ===")
mem = psutil.virtual_memory()
print("Total:", round(mem.total / (1024 ** 3), 2), "GB")
print("Available:", round(mem.available / (1024 ** 3), 2), "GB")
print("Used:", round(mem.used / (1024 ** 3), 2), "GB")
print("Percentage:", mem.percent, "%")

print("\n=== Disk Info ===")
for partition in psutil.disk_partitions():
    print(f"Device: {partition.device}, Mountpoint: {partition.mountpoint}, File system: {partition.fstype}")
    usage = psutil.disk_usage(partition.mountpoint)
    print("  Total:", round(usage.total / (1024 ** 3), 2), "GB")
    print("  Used:", round(usage.used / (1024 ** 3), 2), "GB")
    print("  Free:", round(usage.free / (1024 ** 3), 2), "GB")
    print("  Percentage:", usage.percent, "%")

print("\n=== Network Info ===")
for name, stats in psutil.net_if_stats().items():
    print(f"Interface: {name}, Is up: {stats.isup}, Speed: {stats.speed} Mbps")
