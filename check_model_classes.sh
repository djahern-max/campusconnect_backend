#!/bin/bash
# Run this in ~/projects/college-backend to find the actual class names

echo "=== Checking all model class names ==="
echo ""

for file in app/models/*.py; do
    if [ -f "$file" ] && [ "$(basename $file)" != "__init__.py" ]; then
        echo "📄 $(basename $file):"
        grep "^class " "$file" | sed 's/class /  - /' | sed 's/(.*$//'
        echo ""
    fi
done

echo "=== Now checking __init__.py exports ==="
echo ""
cat app/models/__init__.py
