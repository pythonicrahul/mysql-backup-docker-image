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
restore_backup = os.environ.get('RESTORE_BACKUP')  # Get the restore flag
backup_file_name = os.environ.get('BACKUP_FILE_NAME')  # Get the backup file name


def database_exists(database_name):
    try:
        subprocess.run(
            f"mysql -h {db_host} -P {db_port} -u {db_user} -p{db_password} -e 'USE {database_name}'",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def restore_database(database_name, sql_backup_file):
    subprocess.run(
        f"mysql -h {db_host} -P {db_port} -u {db_user} -p{db_password} {database_name} < {sql_backup_file}",
        shell=True,
        check=True,
    )

if restore_backup.lower() == 'true':
    sql_backup_file = f"{backup_file_name}.sql"

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key,
                      aws_secret_access_key=aws_secret_key)
    s3.download_file(s3_bucket_name, sql_backup_file, sql_backup_file)

    if not database_exists(db_name):
        restore_database(db_name, sql_backup_file)
        print(f"{db_name} restored successfully.")

max_attempts = 10 
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

        # Create a backup
        backup_filename = f"{backup_file_name}_{project_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.sql"
        mysql_dump_command = f"mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} > {backup_filename}"
        subprocess.run(mysql_dump_command, shell=True, check=True)

        # Upload the backup file to S3
        s3.upload_file(backup_filename, s3_bucket_name, backup_filename)
        print(f"Backup successfully uploaded to S3: {backup_filename}")

        os.remove(backup_filename)

        break  

    except subprocess.CalledProcessError:
        # MySQL is not yet available, wait and retry
        attempt += 1
        print(
            f"Attempt {attempt}/{max_attempts}: MySQL is not available. Retrying in 5 seconds...")
        time.sleep(5)

if attempt >= max_attempts:
    print("Max attempts reached. Backup process failed.")
