#!/bin/bash
# ROBO Trading System Cleanup Script
# Removes obsolete and duplicate files

set -e  # Exit on error

echo "🧹 ROBO Trading System Cleanup"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "ROBO_main.py" ]; then
    echo "❌ Error: Please run this script from the ROBO_trading_system directory"
    exit 1
fi

echo "📋 Files to be deleted:"
echo "  - src/dump/ (entire directory)"
echo "  - src/strategies/ROBO_base_strategyold.py"
echo "  - robo_config_conservative.txt"
echo ""

read -p "Continue with cleanup? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi

echo ""
echo "🗑️  Deleting obsolete files..."

# Remove dump directory
if [ -d "src/dump" ]; then
    rm -rf src/dump/
    echo "  ✓ Deleted src/dump/"
else
    echo "  ⊘ src/dump/ not found (already deleted)"
fi

# Remove old base strategy
if [ -f "src/strategies/ROBO_base_strategyold.py" ]; then
    rm src/strategies/ROBO_base_strategyold.py
    echo "  ✓ Deleted src/strategies/ROBO_base_strategyold.py"
else
    echo "  ⊘ ROBO_base_strategyold.py not found (already deleted)"
fi

# Remove old config
if [ -f "robo_config_conservative.txt" ]; then
    rm robo_config_conservative.txt
    echo "  ✓ Deleted robo_config_conservative.txt"
else
    echo "  ⊘ robo_config_conservative.txt not found (already deleted)"
fi

echo ""
echo "🧹 Cleaning old log files (>30 days)..."
if [ -d "logs" ]; then
    find logs/ -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    echo "  ✓ Cleaned old logs"
else
    echo "  ⊘ logs/ directory not found"
fi

echo ""
echo "📊 Cleaning __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ Cleaned Python cache files"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Run: python ROBO_main.py --test"
echo "  2. Verify system works correctly"
echo "  3. Commit changes: git add . && git commit -m 'Clean up obsolete files'"
echo ""
