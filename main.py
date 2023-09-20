import os
import subprocess
import boto3
from datetime import datetime
import time

# Get environment variables
project_name = os.environ.get('NAME')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_name = os.environ.get('DB_NAME')
aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')
s3_bucket_name = os.environ.get('S3_BUCKET_NAME')

# Maximum number of attempts to check MySQL availability
max_attempts = 10  # Adjust as needed
attempt = 0

while attempt < max_attempts:
    time.sleep(30)
    try:
        # Try to connect to the MySQL server
        subprocess.run(
            f"mysql -h {db_host} -P {db_port} -u {db_user} -p{db_password} -e 'SELECT 1'",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # If the connection succeeds, create a backup
        backup_filename = f"backup_{project_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.sql"
        mysql_dump_command = f"mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} > {backup_filename}"
        subprocess.run(mysql_dump_command, shell=True, check=True)

        # Initialize the S3 client (specify the region if necessary)
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key,
                          aws_secret_access_key=aws_secret_key)

        # Upload the backup file to S3
        with open(backup_filename, 'rb') as backup_file:
            s3.upload_fileobj(backup_file, s3_bucket_name, backup_filename)

        print(f"Backup successfully uploaded to S3: {backup_filename}")
        break  # Exit the loop if backup is successful

    except subprocess.CalledProcessError:
        # MySQL is not yet available, wait and retry
        attempt += 1
        print(
            f"Attempt {attempt}/{max_attempts}: MySQL is not available. Retrying in 5 seconds...")
        time.sleep(5)

if attempt >= max_attempts:
    print("Max attempts reached. Backup process failed.")
