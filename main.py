import os
import subprocess
import boto3
from datetime import datetime, timedelta
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

# Get the start and end hours in UTC from environment variables
start_hour_utc = int(os.environ.get('START_HOUR_UTC')) or 7
end_hour_utc = int(os.environ.get('END_HOUR_UTC')) or 8

# Maximum number of attempts to check MySQL availability
max_attempts = 10  # Adjust as needed

while True:
    current_time_utc = datetime.utcnow()

    # Check if the current time is within the specified time range
    if start_hour_utc <= current_time_utc.hour <= end_hour_utc:
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
            backup_filename = f"backup_{project_name}_{current_time_utc.strftime('%Y%m%d%H%M%S')}.sql"
            mysql_dump_command = f"mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} > {backup_filename}"
            subprocess.run(mysql_dump_command, shell=True, check=True)

            # Initialize the S3 client (specify the region if necessary)
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key,
                              aws_secret_access_key=aws_secret_key)

            # Upload the backup file to S3
            with open(backup_filename, 'rb') as backup_file:
                s3.upload_fileobj(backup_file, s3_bucket_name, backup_filename)

            print(f"Backup successfully uploaded to S3: {backup_filename}")
            # Sleep for one day before running the backup again
            time.sleep(24 * 60 * 60)  # 24 hours in seconds
        except subprocess.CalledProcessError:
            print("MySQL is not available. Retrying in 30 seconds...")
            time.sleep(30)
        
    else:
        # Calculate the time until the next backup window (in seconds)
        next_start_time = current_time_utc.replace(
            hour=start_hour_utc, minute=0, second=0, microsecond=0) + timedelta(days=1)

        time_until_next_backup = (
            next_start_time - current_time_utc).total_seconds()

        print(
            f"Next backup window at {next_start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC. Sleeping for {time_until_next_backup} seconds...")
        time.sleep(time_until_next_backup)
