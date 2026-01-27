#!/bin/bash
# Integration test to verify apidiscovery definitions are included in processed spec

set -e

echo "Integration Test: Verifying apidiscovery definitions in processed spec"
echo "========================================================================"

# Create a test directory
TEST_DIR=$(mktemp -d)
trap "rm -rf $TEST_DIR" EXIT

# Download a real swagger.json
echo "1. Downloading swagger.json from kubernetes/kubernetes master..."
curl -sL "https://raw.githubusercontent.com/kubernetes/kubernetes/master/api/openapi-spec/swagger.json" \
  -o "$TEST_DIR/swagger_input.json"

echo "   ✓ Downloaded $(wc -c < "$TEST_DIR/swagger_input.json") bytes"

# Process it with our preprocess_spec.py
echo "2. Processing spec with preprocess_spec.py..."
python3 preprocess_spec.py python master "$TEST_DIR/swagger_output.json" kubernetes kubernetes \
  > /dev/null 2>&1 || true

# Check if output was created
if [ ! -f "$TEST_DIR/swagger_output.json" ]; then
  echo "   ✗ FAILED: Output file not created"
  exit 1
fi

echo "   ✓ Processed $(wc -c < "$TEST_DIR/swagger_output.json") bytes"

# Verify apidiscovery definitions are present
echo "3. Verifying apidiscovery definitions..."
APIDISCOVERY_COUNT=$(jq '[.definitions | keys[] | select(contains("Discovery") and (contains("v2beta1") or contains("APIGroup")))] | length' "$TEST_DIR/swagger_output.json")

if [ "$APIDISCOVERY_COUNT" -ge 5 ]; then
  echo "   ✓ Found $APIDISCOVERY_COUNT apidiscovery definitions"
  jq -r '.definitions | keys[] | select(contains("Discovery") and (contains("v2beta1") or contains("APIGroup")))' "$TEST_DIR/swagger_output.json" | head -10 | while read def; do
    echo "     - $def"
  done
  echo ""
  echo "========================================================================"
  echo "✓ Integration test PASSED"
  exit 0
else
  echo "   ✗ FAILED: Expected at least 5 apidiscovery definitions, found $APIDISCOVERY_COUNT"
  exit 1
fi
