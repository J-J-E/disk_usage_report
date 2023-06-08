import argparse
import configparser
import os
import socket
import smtplib
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
    if file_path is None:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "disk_usage.txt")

    disk_usage_info = ""
    partitions = disk_partitions(all=all_partitions)
    for part in partitions:
        if device and part.device not in device:
            continue
        if mountpoint and not any(
                os.path.normcase(os.path.normpath(mp)) == os.path.normcase(os.path.normpath(part.mountpoint)) for mp in
                mountpoint):
            continue

        disk_usage_info += str(part) + "\n"
        usage = disk_usage(part.mountpoint)
        disk_usage_info += f"    Total: {usage.total:.2f} GB\n"
        disk_usage_info += f"    Used: {usage.used:.2f} GB\n"
        disk_usage_info += f"    Free: {usage.free:.2f} GB\n"
        disk_usage_info += f"    Percent Used: {usage.percent:.2f}%\n"
        disk_usage_info += f"    Percent Free: {100 - usage.percent:.2f}%\n\n"

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
