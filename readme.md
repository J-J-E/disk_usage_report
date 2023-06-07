# Disk Usage Script

This script provides functionality to generate a disk usage report and send it via email. It calculates disk usage f>

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
2. Open the `config.ini` file and provide the necessary SMTP configuration details and email addresses for sending t>

## Usage

To generate the disk usage report and send it via email, execute the script using the following command:
```
python3 disk_usage_report.py
```

The script will calculate the disk usage for the specified partitions, generate the usage report, and send it to the>

## Customization

- If you want to target specific partitions for disk usage calculation, update the `disk_partitions()` function in t>
- To modify the email subject and message, you can update the `subject` and `text` variables in the `send_email` fun>
- If you want to change the attachment filename or customize the email sending logic, you can modify the `send_email>

## Security Considerations

- Ensure that the SMTP credentials and sensitive information in the `config.ini` file are properly secured. Do not s>
- It is recommended to review and adjust the file permissions and access control for the script and associated files>

## License

This script is licensed under the [MIT License](LICENSE).
