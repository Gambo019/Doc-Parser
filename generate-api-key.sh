#!/bin/bash

echo "🔐 Generating secure API key for local development..."
echo ""

# Generate a random UUID-style API key
API_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || head -c 32 /dev/urandom | xxd -p)

if [ -z "$API_KEY" ]; then
    # Fallback method using /dev/random
    API_KEY=$(head -c 32 /dev/urandom | base64 | tr -d '/+=' | head -c 32)
fi

echo "✅ Generated API key: $API_KEY"
echo ""
echo "💡 Add this to your .env file:"
echo "   API_KEY=$API_KEY"
echo ""
echo "🔒 Keep this key secure and don't share it publicly!" 