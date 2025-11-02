#!/bin/bash
# MVP Setup Script

set -euo pipefail

echo "🚀 Setting up JobApply AI Agent MVP..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Prepare data directories
echo "📁 Creating data directories..."
mkdir -p data/applications

# Provide guidance for embeddings model download
echo "🧠 Downloading sentence-transformer model (first run may take a while during execution)."

cat <<'MSG'
✅ Setup complete!
Next steps:
1. Copy mvp.env to .env and fill in credentials (OPENAI_API_KEY, job titles, feeds).
2. Place your resume PDF at the path configured in .env (default: data/resume.pdf).
3. Run the API server:
   python main.py serve --host 0.0.0.0 --port 8000
4. Open http://localhost:8000 to view the dashboard UI.
MSG
