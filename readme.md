# Server Information Report Script
This script generates a server information report with various system statistics. It provides information about the operating system, CPU, memory, disk usage, network interfaces, and GPU. Additionally, it includes system security metrics such as connected user accounts and active network connections.
## Usage
To generate a information report, run the script with the following command:
```
python server_info.py [--send_email] [--mount_point MOUNT_POINTS] [--include_all_partitions] [--metrics METRICS]
```
### Optional Arguments
- `--send_email`: Enables sending an email with the generated report. Requires SMTP server configuration in the environment variables.
- `--mount_point MOUNT_POINTS`: Filters disk usage by specified mount points. Multiple mount points can be provided, separated by commas.
- `--include_all_partitions`: Includes all partitions, including network and virtual partitions, in the disk usage report.
- `--metrics METRICS`: Specifies the sections to include in the report. Multiple sections can be provided, separated by commas. Available sections: `os`, `cpu`, `sec`, `mem`, `dsk`, `net`, `gpu`.

  - Sub metrics for the `sec` section:
    - `cua`: Include connected user accounts.
    - `anc`: Include active network connections.
## Configuration
Before using the script, make sure to set the following environment variables:
- `smtp_server`: SMTP server for sending emails.
- `smtp_port`: SMTP server port.
- `smtp_username`: SMTP username for authentication.
- `smtp_password`: SMTP password for authentication.
- `email_send_to`: Email recipient(s).
- `email_send_from`: Email sender.
## Examples
Generate a disk usage report including all sections:
```
python server_info.py
```
Generate a disk usage report and send it via email:
```
python server_info.py --send_email
```
Filter disk usage by specific mount points:
```
python server_info.py --mount_point "C:\\, D:\\" #windows
python server_info.py --mount_point "/,/nfs" #linux
```
Include all partitions in the disk usage report - by default, only physical partitions are reported. Use this to enable virtual partiaitions and network drives
```
python server_info.py --include_all_partitions
```
Generate a disk usage report with specific metrics:
```
python server_info.py --metrics os,cpu,mem
```
Generate a disk usage report with the `sec` section and its sub metrics:
```bash
python server_info.py --metrics sec:cua:anc
```
Combining arguments:
```bash
python server_info.py --metrics os,dsk,sec:cua --include_all_partitions --send_email
```
Output from above command would be an email containing an attachment titled 
## License
This script is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
