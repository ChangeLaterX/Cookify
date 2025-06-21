#!/bin/bash

# OCR Security Test Script
# Tests rate limiting and security validation for OCR endpoints

echo "🔒 Testing OCR Security Implementation"
echo "======================================"

BASE_URL="http://localhost:8000/api/ocr"
TEST_IMAGE="data/sample_receipt.png"

# Check if test image exists
if [ ! -f "$TEST_IMAGE" ]; then
    echo "❌ Test image not found: $TEST_IMAGE"
    echo "Please ensure you have a test image in the data directory"
    exit 1
fi

echo "📋 Test 1: Normal OCR Request"
echo "-----------------------------"
curl -s -X POST "$BASE_URL/extract-text" \
     -F "image=@$TEST_IMAGE" \
     -H "Content-Type: multipart/form-data" | jq '.'

echo -e "\n📋 Test 2: Rate Limiting (5 rapid requests)"
echo "--------------------------------------------"
for i in {1..5}; do
    echo "Request $i:"
    response=$(curl -s -X POST "$BASE_URL/extract-text" \
                    -F "image=@$TEST_IMAGE" \
                    -H "Content-Type: multipart/form-data")
    
    # Check if rate limited
    if echo "$response" | grep -q "rate limit"; then
        echo "  ⚠️ Rate limited: $(echo "$response" | jq -r '.error // .message')"
    else
        echo "  ✅ Success"
    fi
    
    # Small delay between requests
    sleep 0.5
done

echo -e "\n📋 Test 3: Malicious File Detection"
echo "-----------------------------------"
# Create a test file with suspicious content
echo "<?php echo 'malicious'; ?>" > /tmp/malicious.jpg

response=$(curl -s -X POST "$BASE_URL/extract-text" \
                -F "image=@/tmp/malicious.jpg" \
                -H "Content-Type: multipart/form-data")

if echo "$response" | grep -q "MALICIOUS_CONTENT\|INVALID_IMAGE"; then
    echo "✅ Malicious content detected correctly"
    echo "   Response: $(echo "$response" | jq -r '.error // .message')"
else
    echo "❌ Malicious content not detected"
    echo "   Response: $response"
fi

# Cleanup
rm -f /tmp/malicious.jpg

echo -e "\n📋 Test 4: File Size Validation"
echo "-------------------------------"
# Create a large dummy file (6MB, over the 5MB limit)
dd if=/dev/zero of=/tmp/large.jpg bs=1M count=6 2>/dev/null

response=$(curl -s -X POST "$BASE_URL/extract-text" \
                -F "image=@/tmp/large.jpg" \
                -H "Content-Type: multipart/form-data")

if echo "$response" | grep -q "FILE_TOO_LARGE\|413"; then
    echo "✅ Large file rejected correctly"
    echo "   Response: $(echo "$response" | jq -r '.error // .message')"
else
    echo "❌ Large file not rejected"
    echo "   Response: $response"
fi

# Cleanup
rm -f /tmp/large.jpg

echo -e "\n📋 Test 5: Container Security Check"
echo "-----------------------------------"
if docker ps | grep -q "cookify_api"; then
    echo "✅ Container is running"
    
    # Check if running as non-root
    user=$(docker exec cookify_api whoami 2>/dev/null)
    if [ "$user" = "appuser" ]; then
        echo "✅ Running as non-root user: $user"
    else
        echo "❌ Running as root user: $user"
    fi
    
    # Check secure temp directory
    if docker exec cookify_api ls -ld /tmp/ocr_secure 2>/dev/null | grep -q "drwx------"; then
        echo "✅ Secure temp directory has correct permissions"
    else
        echo "⚠️ Secure temp directory permissions may be incorrect"
    fi
else
    echo "⚠️ Container not running - skipping container security checks"
fi

echo -e "\n🎯 Testing Complete!"
echo "===================="
echo "Review the results above to verify security implementation."
echo "Expected behavior:"
echo "  - Normal requests should succeed"
echo "  - Rapid requests should trigger rate limiting"
echo "  - Malicious files should be rejected"
echo "  - Large files should be rejected"
echo "  - Container should run as non-root user"
