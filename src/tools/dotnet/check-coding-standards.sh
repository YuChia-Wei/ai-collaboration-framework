#!/bin/bash
# Source-checkout structural checks only; not C# semantic or target-adoption validation.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
KNOWLEDGE_DIR="$BASE_DIR/src/knowledge/dotnet"
INDEX_FILE="$KNOWLEDGE_DIR/README.md"

if [ ! -d "$KNOWLEDGE_DIR" ] || [ ! -f "$INDEX_FILE" ]; then
    echo "Self-check failed: .NET knowledge source or README is missing."
    exit 1
fi
echo "Self-check passed: source resources resolve from the script location."

ERRORS=0
echo "1. Checking Main File and Canonical Resources"
REQUIRED_FILES=(
    "content-package.yaml"
    "engineering-rule-catalog.yaml"
    "core/csharp-conventions.md"
    "core/host-configuration.md"
    "architecture/ddd-cqrs/aggregate-standards.md"
    "architecture/ddd-cqrs/usecase-standards.md"
    "architecture/ddd-cqrs/reactor-standards.md"
    "application-types/web-api/controller-standards.md"
    "integration/persistence/repository-standards.md"
    "integration/persistence/projection-standards.md"
    "integration/persistence/mapper-standards.md"
    "integration/persistence/archive-standards.md"
    "testing/test-standards.md"
)
for member in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$KNOWLEDGE_DIR/$member" ]; then
        echo "Missing required source resource: $member"
        ERRORS=$((ERRORS + 1))
    fi
done

# The README selects a topic; deeper owners select their own detailed references.
# Check actual entry links without imposing headings or document-length rules.
ENTRY_ROUTES=(
    "core/csharp-conventions.md"
    "core/host-configuration.md"
    "architecture/ddd-cqrs/overview.md"
    "application-types/web-api/controller-standards.md"
    "integration/persistence/configuration.md"
    "integration/messaging/transactional-messaging-standards.md"
    "testing/test-standards.md"
)
for member in "${ENTRY_ROUTES[@]}"; do
    if [ ! -f "$KNOWLEDGE_DIR/$member" ] ||
       { ! grep -Fq "]($member)" "$INDEX_FILE" && ! grep -Fq "](./$member)" "$INDEX_FILE"; }; then
        echo "Missing exact catalog route in README.md: $member"
        ERRORS=$((ERRORS + 1))
    fi
done

echo "2. Source Script Syntax"
TOTAL_SCRIPTS=0
for script in "$SCRIPT_DIR"/*.sh; do
    [ -f "$script" ] || continue
    TOTAL_SCRIPTS=$((TOTAL_SCRIPTS + 1))
    if ! bash -n "$script"; then
        ERRORS=$((ERRORS + 1))
    fi
done
echo "Total scripts: $TOTAL_SCRIPTS"
if [ "$ERRORS" -ne 0 ]; then
    echo "Structural check failed: $ERRORS error(s)."
    exit 1
fi
echo "Structural integrity passed for required resources, entry routes and shell syntax."
echo "This result does not establish C# semantics, architecture completeness or target technology adoption."
