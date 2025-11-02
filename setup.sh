#!/bin/bash
# MVP Setup Script

echo "🚀 Setting up Job Hunt Agent MVP..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Prepare directories for local storage
echo "📁 Ensuring data and output directories exist..."
mkdir -p data output/resumes output/cover_letters output/logs

if [ ! -f ".env" ]; then
  echo "📄 Copying mvp.env to .env (edit as needed)"
  cp mvp.env .env
fi

echo "✅ MVP setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your resume PDF to data/resume.pdf or update RESUME_PDF_PATH"
echo "2. Review data/user_profile.json to ensure skills and experience are current"
echo "3. Start the API with: python main.py"
