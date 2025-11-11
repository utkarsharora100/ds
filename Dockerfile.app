# Dockerfile for Application Server
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
# Increase pip timeout for large packages like torch (670MB)
RUN pip install --no-cache-dir --default-timeout=1000 --retries 5 -r requirements.txt

# Copy application code
COPY Application_server/ ./Application_server/
COPY llm/ ./llm/
COPY proto/ ./proto/
COPY raft/ ./raft/

# Expose port
EXPOSE 9000

# Run the application server
CMD ["python", "-m", "uvicorn", "Application_server.Application_server:app", "--host", "0.0.0.0", "--port", "9000"]
