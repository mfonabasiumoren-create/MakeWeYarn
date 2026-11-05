FROM python:3.14-slim

# Set the working directory.
WORKDIR /app

# Create a non-root application user.
RUN useradd --create-home appuser

# Copy dependency definitions.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code.
COPY app/ ./app/

# Switch to non-root user.
USER appuser

# Expose Flask application port.
EXPOSE 8001

# Container health check.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health')"

# Start application using Gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "2", "app.app:app"]