#!/bin/bash
# MVP Setup Script

echo "🚀 Setting up Job Hunt Agent MVP..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

echo "✅ MVP setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify your .env has OPENAI_API_KEY set"
echo "2. Run: python main.py"
