#!/bin/bash

echo "🚀 Starting TD25 Money Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Create necessary directories
mkdir -p data

# Start the stack
echo "📦 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Wait for Ollama to be ready
echo "🤖 Waiting for Ollama to be ready..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "   Waiting for Ollama..."
    sleep 10
done

echo "📥 Downloading Llama 3.1 model..."
docker exec ollama ollama pull llama3.1

echo "✅ Setup complete!"
echo ""
echo "🌐 Access the services:"
echo "   • Jupyter Notebook: http://localhost:8888"
echo "   • Flask API: http://localhost:5000"
echo "   • Dify Web UI: http://localhost:3000"
echo "   • Ollama API: http://localhost:11434"
echo ""
echo "📊 Test the API:"
echo "   curl http://localhost:5000/health"
