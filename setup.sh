#!/bin/bash

# AI Marketing Council - Setup Script
# This script sets up the project and checks all dependencies

echo "🤖 AI Marketing Council - Setup"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "   ❌ Python 3.10+ required"
    exit 1
fi
echo "   ✅ Python version OK"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   ⚠️  Virtual environment already exists"
else
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✅ Dependencies installed"
else
    echo "   ❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p outputs/generated_images
mkdir -p outputs/debate_logs
echo "   ✅ Directories created"
echo ""

# Check .env file
echo "🔑 Checking environment variables..."
if [ ! -f ".env" ]; then
    echo "   ⚠️  .env file not found"
    echo "   📝 Creating from template..."
    cp .env.example .env
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env file with your API keys!"
    echo "   Required keys:"
    echo "   - GROQ_API_KEY (get from https://console.groq.com/)"
    echo "   - HUGGINGFACE_TOKEN (get from https://huggingface.co/settings/tokens)"
    echo ""
else
    echo "   ✅ .env file exists"
    
    # Check if keys are set
    if grep -q "your_groq_api_key_here" .env; then
        echo "   ⚠️  GROQ_API_KEY not configured"
    else
        echo "   ✅ GROQ_API_KEY configured"
    fi
    
    if grep -q "your_huggingface_token_here" .env; then
        echo "   ⚠️  HUGGINGFACE_TOKEN not configured"
    else
        echo "   ✅ HUGGINGFACE_TOKEN configured"
    fi
fi
echo ""

# Test imports
echo "🧪 Testing imports..."
python3 << EOF
try:
    import groq
    print("   ✅ groq")
except ImportError:
    print("   ❌ groq - reinstall dependencies")

try:
    import streamlit
    print("   ✅ streamlit")
except ImportError:
    print("   ❌ streamlit - reinstall dependencies")

try:
    from huggingface_hub import InferenceClient
    print("   ✅ huggingface_hub")
except ImportError:
    print("   ❌ huggingface_hub - reinstall dependencies")

try:
    import plotly
    print("   ✅ plotly")
except ImportError:
    print("   ❌ plotly - reinstall dependencies")
EOF
echo ""

# Final message
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: streamlit run app.py"
echo ""
echo "For help, see README.md"
echo ""