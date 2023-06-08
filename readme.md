# System Information Report Script
This script generates a system information report with various system statistics. It provides information about the operating system, CPU, memory, disk usage, network interfaces, and GPU. Additionally, it includes system security metrics such as connected user accounts and active network connections.
## Usage
To generate a information report, run the script with the following command:
```
python system_info.py [--send_email] [--mount_point MOUNT_POINTS] [--include_all_partitions] [--metrics METRICS]
```
### Optional Arguments
- `--send_email`: Enables sending an email with the generated report. Requires SMTP system configuration in the environment variables.
- `--mount_point MOUNT_POINTS`: Filters disk usage by specified mount points. Multiple mount points can be provided, separated by commas.
- `--include_all_partitions`: Includes all partitions, including network and virtual partitions, in the disk usage report.
- `--metrics METRICS`: Specifies the sections to include in the report. Multiple sections can be provided, separated by commas. Available sections: `os`, `cpu`, `sec`, `mem`, `dsk`, `net`, `gpu`.

  - Sub metrics for the `sec` section:
    - `cua`: Include connected user accounts.
    - `anc`: Include active network connections.
## Configuration
Before using the script, if you intend to email reports, make sure to create the valid config file. Copy config.example.ini to config.ini and set the following variables:
- `smtp_system`: SMTP system for sending emails.
- `smtp_port`: SMTP system port.
- `smtp_username`: SMTP username for authentication.
- `smtp_password`: SMTP password for authentication.
- `email_send_to`: Email recipient(s).
- `email_send_from`: Email sender.
## Examples
Generate a disk usage report including all sections:
```
python system_info.py
```
Generate a disk usage report and send it via email:
```
python system_info.py --send_email
```
Filter disk usage by specific mount points:
```
python system_info.py --mount_point "C:\\, D:\\" #windows
python system_info.py --mount_point "/,/nfs" #linux
```
Include all partitions in the disk usage report - by default, only physical partitions are reported. Use this to enable virtual partiaitions and network drives
```
python system_info.py --include_all_partitions
```
Generate a disk usage report with specific metrics:
```
python system_info.py --metrics os,cpu,mem
```
Generate a disk usage report with the `sec` section and its sub metrics:
```bash
python system_info.py --metrics sec:cua:anc
```
Combining arguments:
```bash
python system_info.py --metrics os,dsk,sec:cua --include_all_partitions --send_email
```
Output from above command would be an email containing an attachment titled 

