#!/bin/bash
# MVP Setup Script

set -euo pipefail

echo "🚀 Setting up JobApply AI MVP..."

# Install Python dependencies
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  PYTHON_BIN="python"
fi

echo "📦 Installing Python packages..."
$PYTHON_BIN -m pip install --upgrade pip
$PYTHON_BIN -m pip install -r requirements.txt

# Initialize environment scaffold
if [ ! -f .env ]; then
  echo "📝 Creating .env from mvp.env"
  cp mvp.env .env
fi

# Install dashboard dependencies if npm/yarn is available
if command -v npm >/dev/null 2>&1; then
  echo "🛠️ Installing dashboard packages..."
  (cd dashboard && npm install)
else
  echo "⚠️ npm not found. Install Node.js to run the dashboard."
fi

echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Update .env with your OpenAI API key and job search preferences."
echo "2. Run the API: $PYTHON_BIN main.py"
echo "3. (Optional) Start the dashboard: cd dashboard && npm run dev"
