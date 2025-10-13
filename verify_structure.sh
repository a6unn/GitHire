#!/bin/bash
# Verify the source code structure before Docker build

echo "Verifying source code structure..."

# Check critical directories
for dir in "src" "src/github_sourcer" "src/github_sourcer/lib" "src/contact_enrichment/lib"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: Missing directory: $dir"
        exit 1
    fi
    echo "✓ $dir exists"
done

# Check critical __init__.py files
for init in "src/__init__.py" "src/github_sourcer/__init__.py" "src/github_sourcer/lib/__init__.py" "src/contact_enrichment/lib/__init__.py"; do
    if [ ! -f "$init" ]; then
        echo "ERROR: Missing __init__.py: $init"
        exit 1
    fi
    echo "✓ $init exists"
done

# Check fuzzy_matcher.py specifically
if [ ! -f "src/github_sourcer/lib/fuzzy_matcher.py" ]; then
    echo "ERROR: Missing fuzzy_matcher.py"
    exit 1
fi
echo "✓ src/github_sourcer/lib/fuzzy_matcher.py exists"

echo ""
echo "✅ All required files and directories present!"
echo ""
echo "Directory structure:"
tree -L 3 src/ | head -50
