FROM python:3.8

# Install MySQL client
# RUN apt-get update && apt-get install -y mysql-client && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*


# Set the working directory
WORKDIR /app

# Copy your backup script into the container
COPY main.py .

# Install any Python dependencies (if needed)
RUN pip install boto3

# Specify the command to run when the container starts
CMD ["python", "main.py"]
