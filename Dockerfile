FROM python:3.11-slim

# Install Node.js, npm and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies for the WhatsApp Gateway
COPY bridge/package.json bridge/.npmrc ./bridge/
RUN cd bridge && npm install --allow-git=all

# Copy entire repository source code
COPY . .

# Create startup script for dual processes (FastAPI + Node WhatsApp Gateway)
RUN printf '#!/bin/sh\npython -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &\ncd bridge && node server.js\n' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 10000

CMD ["/app/start.sh"]
