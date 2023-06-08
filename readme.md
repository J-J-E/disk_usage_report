# Disk Usage Script

This script provides functionality to generate a disk usage report and send it via email. It calculates disk usage for specified partitions and generates a usage report that includes information about total space, used space, free space, and the percentage of disk space used.

## Requirements

- Python 3.x
- Required Python packages (install using pip):
    - `psutil` - for retrieving disk usage information
    - `smtplib` - for sending email
    - `email` - for constructing email messages
    - `configparser` - for reading configuration files

## Installation

1. Clone the repository or download the script to your local machine.
2. Install the required Python packages by running the following command:
```
pip install -r requirements.txt
```


## Configuration

1. Rename the `config.example.ini` file to `config.ini`.
2. Open the `config.ini` file and provide the necessary SMTP configuration details and email addresses for sending the disk usage report.

## Usage

Example commands below


### This will run across all disk/partitions found
```
python3 disk-usage-report.py 
```

### specify mountpoint (windows)
```
python3 disk-usage-report.py --mount_point "C:\\, D:\\" 
```

### specify mountpoint (linux)
```
python3 disk-usage-report.py --mount_point "/, /nfs" 
```

### Sending emails (after SMTP server configured)
```
python3 disk-usage-report.py --send_email True #default value is false
```


## Customization

- If you want to target specific partitions for disk usage calculation, update the `disk_partitions()` function in the script accordingly.

## Security Considerations

- Ensure that the SMTP credentials and sensitive information in the `config.ini` file are properly secured. Do not share this information in publicly accessible repositories or directories.
- It is recommended to review and adjust the file permissions and access control for the script and associated files to maintain proper security.


