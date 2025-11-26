#!/bin/bash
#
# Helper script to prepare the IPEDS migration with correct revision IDs
# Run this from your campusconnect-backend directory
#
# Usage: ./prepare_ipeds_migration.sh
#

set -e

echo "=============================================="
echo "IPEDS Migration Preparation Helper"
echo "=============================================="
echo ""

# Check we're in the right directory
if [ ! -f "alembic.ini" ]; then
    echo "ERROR: alembic.ini not found"
    echo "Please run this script from your campusconnect-backend directory"
    exit 1
fi

echo "✓ Found alembic.ini"
echo ""

# Get current migration head
echo "Checking current migration status..."
CURRENT_HEAD=$(alembic current | grep -oP '(?<=\(head\), )[\w]+' || echo "")

if [ -z "$CURRENT_HEAD" ]; then
    echo "Getting head from history..."
    CURRENT_HEAD=$(alembic history | grep "(head)" | awk '{print $1}' || echo "")
fi

if [ -z "$CURRENT_HEAD" ]; then
    echo "WARNING: Could not determine current head revision"
    echo "You'll need to manually update the migration file"
    echo ""
    echo "Run: alembic current"
    echo "Or: alembic history | head -5"
    echo ""
else
    echo "✓ Current head revision: $CURRENT_HEAD"
    echo ""
fi

# Generate new revision ID
echo "Generating new revision ID..."
NEW_REVISION=$(python3 -c "import uuid; print(str(uuid.uuid4())[:12])")
echo "✓ New revision ID: $NEW_REVISION"
echo ""

# Check if migration file exists
MIGRATION_FILE="add_ipeds_data_fields_and_completeness_scoring.py"
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "ERROR: Migration file not found: $MIGRATION_FILE"
    echo "Please copy it to this directory first"
    exit 1
fi

echo "✓ Found migration file: $MIGRATION_FILE"
echo ""

# Create the properly named migration file
NEW_FILENAME="alembic/versions/${NEW_REVISION}_add_ipeds_data_fields_and_completeness_scoring.py"

echo "Creating properly named migration file..."
echo "Target: $NEW_FILENAME"
echo ""

# Copy and update the file
cp "$MIGRATION_FILE" "$NEW_FILENAME"

# Update revision IDs in the file
if [ -n "$CURRENT_HEAD" ]; then
    sed -i.bak "s/revision = 'XXXXXX_ipeds_data'/revision = '${NEW_REVISION}'/" "$NEW_FILENAME"
    sed -i.bak "s/down_revision = '<previous_revision>'/down_revision = '${CURRENT_HEAD}'/" "$NEW_FILENAME"
    rm "${NEW_FILENAME}.bak"
    
    echo "✓ Updated revision IDs in migration file"
    echo "  revision: $NEW_REVISION"
    echo "  down_revision: $CURRENT_HEAD"
else
    echo "⚠ Could not automatically update revision IDs"
    echo "Please manually update these lines in: $NEW_FILENAME"
    echo "  revision = '${NEW_REVISION}'"
    echo "  down_revision = '<YOUR_CURRENT_HEAD>'"
fi

echo ""
echo "=============================================="
echo "Next Steps:"
echo "=============================================="
echo ""
echo "1. Verify the migration file:"
echo "   cat $NEW_FILENAME | head -20"
echo ""
echo "2. Test the migration locally:"
echo "   alembic upgrade head"
echo ""
echo "3. Verify database changes:"
echo "   psql -U postgres -d unified_db"
echo "   \\d institutions"
echo ""
echo "4. If successful, commit and push:"
echo "   git add $NEW_FILENAME"
echo "   git commit -m 'Add IPEDS data fields and completeness scoring'"
echo "   git push origin main"
echo ""
echo "5. Then proceed with IPEDS data import"
echo ""
