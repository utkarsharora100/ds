# Optimized Dockerfile for Application Server
# Serves both API and Frontend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy ONLY base requirements (no LLM dependencies)
COPY requirements/requirements-base.txt .

# Install Python dependencies quickly (no timeout issues!)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-base.txt

# Copy application code
COPY Application_server/ ./Application_server/
COPY llm/ ./llm/
COPY proto/ ./proto/
COPY raft/ ./raft/

# Copy frontend files
COPY web/ ./web/

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Run the application server
CMD ["python", "-m", "uvicorn", "Application_server.Application_server:app", "--host", "0.0.0.0", "--port", "9000"]
