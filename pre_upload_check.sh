#!/bin/bash

echo "🔍 Pre-Upload Security Check"
echo "=============================="

# Check for real API keys (excluding example files and the script itself)
echo -n "✓ Checking for API keys... "
FOUND_KEYS=$(grep -r "sk-ant-api03-[a-zA-Z0-9_-]\{20,\}" . \
    --exclude-dir=.git \
    --exclude-dir=venv \
    --exclude-dir=trading-bot-env \
    --exclude="*.example" \
    --exclude="pre_upload_check.sh" \
    2>/dev/null)

if [ ! -z "$FOUND_KEYS" ]; then
    echo "❌ REAL API KEY FOUND!"
    echo "$FOUND_KEYS"
    exit 1
else
    echo "✓ Clean"
fi

# Check for .env file with real content
echo -n "✓ Checking .env file... "
if [ -f .env ]; then
    if grep -q "sk-ant-api03-[a-zA-Z0-9_-]\{20,\}" .env 2>/dev/null; then
        echo "❌ Real API key in .env!"
        exit 1
    else
        echo "✓ Safe (placeholder only)"
    fi
else
    echo "⚠️  No .env file (create from .env.example)"
fi

# Check .gitignore exists
echo -n "✓ Checking .gitignore exists... "
if [ -f .gitignore ]; then
    echo "✓ Present"
else
    echo "❌ Missing!"
fi

# Check LICENSE exists
echo -n "✓ Checking LICENSE exists... "
if [ -f LICENSE ]; then
    echo "✓ Present"
else
    echo "❌ Missing!"
fi

# Check requirements.txt
echo -n "✓ Checking requirements.txt... "
if [ -f requirements.txt ]; then
    echo "✓ Present"
else
    echo "❌ Missing!"
fi

# Check .env is gitignored
echo -n "✓ Checking .env is gitignored... "
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "✓ Safe"
else
    echo "⚠️  Warning: .env not explicitly in .gitignore"
fi

# Check .env.example exists
echo -n "✓ Checking .env.example exists... "
if [ -f .env.example ]; then
    echo "✓ Present (good for documentation)"
else
    echo "⚠️  Missing (recommended)"
fi

echo ""
echo "📊 Repository Stats:"
echo "===================="
echo -n "Python files: "
find . -name "*.py" -not -path "./venv/*" -not -path "./*env/*" -not -path "./.git/*" | wc -l
echo -n "Markdown files: "
find . -name "*.md" -not -path "./.git/*" | wc -l
echo -n "Total size: "
du -sh . 2>/dev/null | awk '{print $1}'

# Check for database files
echo ""
echo "⚠️  Files that should NOT be uploaded:"
echo "========================================"
if [ -f research_tasks.db ]; then
    echo "❌ research_tasks.db (contains your data)"
fi
if [ -f setup_env.sh ] && grep -q "api.*key\|password" setup_env.sh 2>/dev/null; then
    echo "❌ setup_env.sh (might contain credentials)"
fi
find . -name "*.backup" -o -name "*.bak" -o -name "*.old" 2>/dev/null | while read file; do
    echo "⚠️  $file (backup file)"
done

echo ""
echo "✅ Security check complete!"
echo ""
echo "Next steps:"
echo "1. Review the warnings above"
echo "2. Run: git status"
echo "3. Verify .env is NOT listed"
echo "4. If all clear: git add . && git commit"
