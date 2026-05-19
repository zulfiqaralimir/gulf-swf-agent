FROM python:3.11-slim

# Install Node.js 20 for MongoDB MCP Server
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache the MCP server binary so cold starts are fast
RUN npm install -g mongodb-mcp-server

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
