
# MySQL Database Backup Image

This script allows you to automatically back up your MySQL database and store the backups in an Amazon S3 bucket. You can use it in a Docker container and configure it to run backups on demand or on a schedule.

## Getting Started

Follow these steps to set up and use the MySQL Database Backup script.

### Prerequisites

Before you begin, ensure you have the following prerequisites:

-   AWS account with S3 bucket for backup storage
-   MySQL server accessible from the container

### Usage
### Scheduled Backups with Docker Compose

To schedule backups with Docker Compose, you can define a service for the backup script and use Docker Compose's scheduling capabilities.

Here's an example `docker-compose.yml` file:


```yaml
version: '3'
services:
  mysql-backup:
    image: pythonicrahul/mysql-backup:latest
    environment:
      - NAME=YourProject
      - DB_HOST=your-mysql-host
      - DB_PORT=3306
      - DB_USER=your-db-user
      - DB_PASSWORD=your-db-password
      - DB_NAME=your-db-name
      - AWS_ACCESS_KEY=your-aws-access-key
      - AWS_SECRET_KEY=your-aws-secret-key
      - S3_BUCKET_NAME=your-s3-bucket
    depends_on:
      - mysql_container
    networks:
      - commong_network
    restart:  on-failure
```
