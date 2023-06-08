import argparse
import configparser
import datetime
import GPUtil
import os
import socket
import smtplib
import platform
import psutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from collections import namedtuple


def import_config_values():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "config.ini")

    assert os.path.exists(config_file), "Config file not found. Please make a copy of config.example.ini and name it config.ini, then update the values appropriately."

    config = configparser.ConfigParser()
    config.read(config_file)

    for section in config.sections():
        for key, value in config.items(section):
            os.environ[key] = value


def disk_partitions(all=False):
    """Return all mounted partitions as a namedtuple.
    If all == False return physical partitions only.
    """
    partitions = psutil.disk_partitions(all=all)
    retlist = []
    for part in partitions:
        device = part.device
        mountpoint = part.mountpoint
        fstype = part.fstype
        ntuple = disk_ntuple(device, mountpoint, fstype)
        retlist.append(ntuple)
    return retlist


def disk_usage(path):
    """Return disk usage associated with the path in gigabytes."""
    usage = psutil.disk_usage(path)
    total = usage.total / (1024 ** 3)
    used = usage.used / (1024 ** 3)
    free = usage.free / (1024 ** 3)
    percent = usage.percent
    return usage_ntuple(total, used, free, round(percent, 1))


def write_disk_usage_info(file_path, contents):
    with open(file_path, "w") as f:
        f.write(contents)


def generate_usage_file(device=None, mountpoint=None, all_partitions=False, file_path=None):
    """Generate a disk usage file for the specified device(s) or mountpoint(s)."""
    file_contents = ''
    if file_path is None:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "disk_usage.txt")

    # Operating System information
    uptime = psutil.boot_time()
    uptime_dt = datetime.datetime.fromtimestamp(uptime)
    uptime_str = str(datetime.datetime.now() - uptime_dt)
    os_info = "OPERATING SYSTEM INFORMATION\n"
    os_info += f"    System: {platform.system()}\n"
    os_info += f"    Release: {platform.release()}\n"
    os_info += f"    Version: {platform.version()}\n"
    os_info += f"    Machine: {platform.machine()}\n"
    os_info += f"    Processor: {platform.processor()}\n"
    os_info += f"    Uptime: {uptime_str}\n\n"
    file_contents += os_info

    # CPU statistics
    cpu_freq = psutil.cpu_freq()

    cpu_percent = psutil.cpu_percent(interval=1)  # CPU usage as a percentage
    logical_cpu_count = psutil.cpu_count(logical=True)  # Number of logical CPUs
    physical_cpu_count = psutil.cpu_count(logical=False) # Number of physical CPUs
    cpu_usage_info = "CPU STATISTICS\n"
    cpu_usage_info += f"    Frequency: {cpu_freq.current:.2f} MHz\n"  # CPU frequency if available
    cpu_usage_info += f"    CPU Usage (at runtime): {cpu_percent:.1f}%\n"
    cpu_usage_info += f"    Number of CPUs (physical): {physical_cpu_count}\n"
    cpu_usage_info += f"    Number of CPUs (logical): {logical_cpu_count}\n"
    cpu_usage_info += f"    Number of Running Processes: {len(psutil.pids())}\n\n"
    file_contents += cpu_usage_info

    # System Security
    security_info = "SYSTEM SECURITY\n"
    users = psutil.users()
    security_info += "    Connected User Accounts:\n"
    for user in users:
        security_info += f"        Username: {user.name}\n"
        security_info += f"        Terminal: {user.terminal}\n"
        security_info += f"        Hostname: {user.host}\n"
        security_info += f"        Started: {user.started}\n\n"
    connections = psutil.net_connections()
    security_info += "    Active Network Connections:\n"
    for conn in connections:
        security_info += f"        Local Address: {conn.laddr}\n"
        security_info += f"        Remote Address: {conn.raddr}\n"
        security_info += f"        Status: {conn.status}\n\n"
    file_contents += security_info

    # Memory statistics
    memory = psutil.virtual_memory()
    total_memory = memory.total / (1024 * 1024 * 1024)  # Total physical memory in GB
    available_memory = memory.available / (1024 * 1024 * 1024)  # Available memory in GB
    used_memory = memory.used / (1024 * 1024 * 1024)  # Used memory in GB
    free_memory = memory.free / (1024 * 1024 * 1024)  # Free memory in GB
    cached_memory = (available_memory - free_memory)  # Cached memory estimate in GB
    memory_percent = memory.percent  # Memory usage as a percentage
    # Format memory statistics
    memory_usage_info = "MEMORY STATISTICS\n"
    memory_usage_info += f"    Total Memory: {total_memory:.2f} GB\n"
    memory_usage_info += f"    Available Memory: {available_memory:.2f} GB\n"
    memory_usage_info += f"    Used Memory: {used_memory:.2f} GB\n"
    memory_usage_info += f"    Free Memory: {free_memory:.2f} GB\n"
    memory_usage_info += f"    Cached Memory: {cached_memory:.2f} GB\n"
    memory_usage_info += f"    Memory Usage: {memory_percent}%\n"
    swap = psutil.swap_memory()
    memory_usage_info += f"    Swap Space:\n"
    memory_usage_info += f"        Total: {swap.total / 1024 / 1024 / 1024:.2f} GB\n"
    memory_usage_info += f"        Used: {swap.used / 1024 / 1024 / 1024:.2f} GB\n"
    memory_usage_info += f"        Free: {swap.free / 1024 / 1024 / 1024:.2f} GB\n\n"
    file_contents += memory_usage_info

    # Disk Statistics
    disk_usage_info = "DISK STATISTICS\n"
    partitions = disk_partitions(all=all_partitions)
    if mountpoint is None:  # No mount points specified, report all of them
        mount_points = [part.mountpoint for part in partitions]
    else:
        mount_points = mountpoint

    for part in partitions:
        if device and part.device not in device:
            continue
        if mountpoint and not any(
                os.path.normcase(os.path.normpath(mp)) == os.path.normcase(os.path.normpath(part.mountpoint)) for mp in
                mount_points):
            continue

        disk_usage_info += " " + str(part) + "\n"
        usage = disk_usage(part.mountpoint)
        disk_usage_info += f"    Total: {usage.total:.2f} GB\n"
        disk_usage_info += f"    Used: {usage.used:.2f} GB\n"
        disk_usage_info += f"    Free: {usage.free:.2f} GB\n"
        disk_usage_info += f"    Percent Used: {usage.percent:.2f}%\n"
        disk_usage_info += f"    Percent Free: {100 - usage.percent:.2f}%\n\n"
    file_contents += disk_usage_info

    # Hostname
    hostname = socket.gethostname()
    # IP address
    ip_address = socket.gethostbyname(hostname)
    # Network interfaces
    network_interfaces = psutil.net_if_addrs()

    # Format hostname and IP address
    host_info = "HOST INFORMATION\n"
    host_info += f"    Hostname: {hostname}\n"
    host_info += f"    IP Address: {ip_address}\n\n"
    file_contents += host_info

    # Format network interfaces
    network_info = "NETWORK INTERFACES\n"
    for interface, addresses in network_interfaces.items():
        network_info += f"    Interface: {interface}\n"
        for addr in addresses:
            if addr.family == socket.AF_INET:
                network_info += f"        IP Address: {addr.address}\n"
                network_info += f"        Netmask: {addr.netmask}\n"
                network_info += f"        Broadcast IP: {addr.broadcast}\n"
            elif addr.family == socket.AF_INET6:
                network_info += f"        IP Address (IPv6): {addr.address}\n"
                network_info += f"        Netmask (IPv6): {addr.netmask}\n"
            elif addr.family == psutil.AF_LINK:
                network_info += f"        MAC Address: {addr.address}\n"
        network_info += "\n"
    file_contents += network_info

    # GPU information
    gpus = GPUtil.getGPUs()
    gpu_info = "GPU INFORMATION\n"
    for idx, gpu in enumerate(gpus):
        gpu_info += f"    GPU {idx + 1}:\n"
        gpu_info += f"        Name: {gpu.name}\n"
        gpu_info += f"        UUID: {gpu.uuid}\n"
        gpu_info += f"        Load: {gpu.load * 100:.2f}%\n"
        gpu_info += f"        Memory Usage:\n"
        gpu_info += f"            Total: {gpu.memoryTotal/1024:.2f} GB\n"
        gpu_info += f"            Used: {gpu.memoryUsed/1024:.2f} GB\n"
        gpu_info += f"            Free: {gpu.memoryFree/1024:.2f} GB\n"
        gpu_info += f"        Temperature: {gpu.temperature:.2f} °C\n\n"  # GPU temperature if available
    file_contents += gpu_info




    print(file_contents)
    write_disk_usage_info(file_path, disk_usage_info)
    return file_path


def send_email(send_to, send_from, subject, text, attachment):
    smtp_server = os.environ.get("smtp_server")
    port = os.environ.get("smtp_port")
    username = os.environ.get("smtp_username")
    pw = os.environ.get("smtp_password")
    attachment_name = os.path.basename(attachment)
    recipients = send_to.split(",")

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.login(username, pw)

        for r in recipients:
            msg = MIMEMultipart()
            msg['From'] = send_from
            msg['To'] = r.strip()

            msg['Subject'] = subject

            msg.attach(MIMEText(text))

            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(attachment, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
            msg.attach(part)
            server.sendmail(send_from, msg['To'], msg.as_string())
        server.close()

    except Exception as e:
        print("Failed to send email:", e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--send_email", help="Send email report if set to True", default=False, type=bool)
    parser.add_argument("--mount_point", help='Filter disk usage by mount points (comma-separated, enclosed in quotes)', default=None)
    args = parser.parse_args()

    import_config_values()
    hostname = socket.gethostname()

    disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
    usage_ntuple = namedtuple('usage', 'total used free percent')

    mount_points = None
    if args.mount_point:
        mount_points = args.mount_point.split(',')
        # Strip whitespace and remove the enclosing quotes
        mount_points = [mp.strip().strip("'").strip('"') for mp in mount_points]

    file_path = generate_usage_file(mountpoint=mount_points, all_partitions=True)

    if args.send_email:
        send_to = os.environ.get("email_send_to")
        send_from = os.environ.get("email_send_from")
        subject = hostname + ' - Disk Usage Report'
        text = 'Please see the attached file.'
        attachment = file_path
        send_email(send_to, send_from, subject, text, attachment)
