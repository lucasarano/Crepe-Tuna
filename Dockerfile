FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    portaudio19-dev \
    python3-pyaudio \
    libhdf5-dev \
    libportaudio2 \
    libhdf5-103 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn

# Copy application
COPY ./app .

# Expose port
EXPOSE 8080

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app.main:app
