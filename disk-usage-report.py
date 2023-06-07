import configparser, os, socket, smtplib
from collections import namedtuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def import_config_values():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "config.ini")

    config = configparser.ConfigParser()
    config.read(config_file)

    for section in config.sections():
        for key, value in config.items(section):
            os.environ[key] = value


def disk_partitions(all=False):
    """Return all mounted partitions as a namedtuple.
    If all == False return physical partitions only.
    """
    phydevs = []
    with open("/proc/filesystems", "r") as f:
        for line in f:
            if not line.startswith("nodev"):
                phydevs.append(line.strip())

    retlist = []
    with open('/etc/mtab', "r") as f:
        for line in f:
            if not all and line.startswith('none'):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == 'none':
                device = ''
            ntuple = disk_ntuple(device, mountpoint, fstype)
            retlist.append(ntuple)
    return retlist

def disk_usage(path):
    """Return disk usage associated with the path in gigabytes."""
    st = os.statvfs(path)
    block_size = st.f_frsize
    total = (st.f_blocks * block_size) / (1024 ** 3)
    used = ((st.f_blocks - st.f_bfree) * block_size) / (1024 ** 3)
    free = (st.f_bavail * block_size) / (1024 ** 3)
    try:
        percent = (used / total) * 100
    except ZeroDivisionError:
        percent = 0
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
        if mountpoint and part.mountpoint not in mountpoint:
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
    smtp_server = 'smtp.postmarkapp.com'
    port = 587
    username = os.environ.get("smtp_username")
    pw = os.environ.get("smtp_password")
    attachment_name = os.path.basename(attachment)

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.login(username, pw)

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = send_to.replace(" ", "")
        print(msg['To'])
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(attachment, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
        msg.attach(part)

        server.sendmail(send_from, send_to, msg.as_string())
        server.close()

        return True

    except Exception as e:
        print("Failed to send email:", e)
        return False



if __name__ == '__main__':
    import_config_values()
    hostname = socket.gethostname()

    disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
    usage_ntuple = namedtuple('usage', 'total used free percent')

    file_path = generate_usage_file(mountpoint='/,/nfs', all_partitions=True)

    send_to = os.environ.get("email_send_to")
    send_from = os.environ.get("email_send_from")
    subject=hostname + ' - Disk Usage Report'
    text='Please see the attached file.'
    attachment=file_path
    send_email(send_to, send_from, subject, text, attachment)

