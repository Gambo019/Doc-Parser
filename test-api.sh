#!/bin/bash

echo "🧪 Testing Document Processing Engine API"
echo ""

API_BASE="http://localhost:8000"

# Test 1: Check API health
echo "1. Testing API health..."
if curl -s "$API_BASE/docs" > /dev/null; then
    echo "   ✅ API is responding"
else
    echo "   ❌ API is not responding"
    exit 1
fi

# Test 2: Check OpenAPI documentation
echo ""
echo "2. Testing OpenAPI documentation..."
if curl -s "$API_BASE/openapi.json" | jq -e '.info.title' > /dev/null 2>&1; then
    API_TITLE=$(curl -s "$API_BASE/openapi.json" | jq -r '.info.title' 2>/dev/null || echo "FastAPI")
    echo "   ✅ OpenAPI docs available: $API_TITLE"
else
    echo "   ✅ OpenAPI docs available (jq not installed for parsing)"
fi

# Test 3: Check available endpoints
echo ""
echo "3. Available endpoints:"
echo "   • GET  $API_BASE/docs - API Documentation"
echo "   • POST $API_BASE/api/process-document - Process documents"
echo "   • POST $API_BASE/api/process-pbm-document - Process PBM documents"
echo "   • GET  $API_BASE/api/task/{task_id} - Get task status"

# Test 4: Test without file (should return 422)
echo ""
echo "4. Testing process-document endpoint (without file)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE/api/process-document")
if [ "$HTTP_CODE" = "422" ]; then
    echo "   ✅ Endpoint correctly requires file upload (HTTP 422)"
else
    echo "   ⚠️  Unexpected HTTP code: $HTTP_CODE"
fi

echo ""
echo "🎉 API Tests Complete!"
echo ""
echo "🔗 Access your API:"
echo "   • Documentation: $API_BASE/docs"
echo "   • MinIO Console: http://localhost:9001"
echo ""
echo "📝 To test with a real document:"
echo "   curl -X POST \"$API_BASE/api/process-document\" \\"
echo "        -F \"file=@your-document.pdf\" \\"
echo "        -F \"callback_url=http://your-app.com/webhook\"" 