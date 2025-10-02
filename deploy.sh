#!/bin/bash

# AI Cover Image Generator - Railway Deployment Script
echo "🚀 Deploying AI Cover Image Generator to Railway"
echo "==============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "📦 Please install Railway CLI first:"
    echo "   npm install -g @railway/cli"
    echo "   or visit: https://railway.app/cli"
    exit 1
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway first:"
    echo "   railway login"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Please create .env with your configuration before deploying."
    exit 1
fi

# Validate required environment variables
echo "🔍 Validating environment variables..."

# Read .env file and check required variables
REQUIRED_VARS=("SUPABASE_URL" "SUPABASE_SERVICE_ROLE_KEY" "SUPABASE_STORAGE_BUCKET")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$var=" .env; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo "📝 Please add these to your .env file before deploying."
    exit 1
fi

echo "✅ Environment variables validated"

# Build and test locally first
echo "🧪 Testing build locally..."
if ! docker build -t ai-cover-generator-test . > /dev/null 2>&1; then
    echo "❌ Docker build failed! Please fix build issues before deploying."
    exit 1
fi

echo "✅ Local build successful"

# Deploy to Railway
echo "🚀 Deploying to Railway..."

# Link project (if not already linked)
if [ ! -f railway.json ]; then
    echo "🔗 Linking Railway project..."
    railway link
fi

# Set environment variables from .env
echo "🔧 Setting environment variables..."
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    if [[ $key == \#* ]] || [[ -z $key ]]; then
        continue
    fi
    
    # Remove surrounding quotes if present
    value=$(echo $value | sed 's/^["'"'"']//;s/["'"'"']$//')
    
    echo "   Setting $key..."
    railway variables set "$key=$value"
done < .env

# Deploy
echo "🚀 Starting deployment..."
railway up

echo ""
echo "🎉 Deployment initiated!"
echo "📊 Check deployment status:"
echo "   railway status"
echo ""
echo "📡 Once deployed, your API will be available at:"
echo "   railway domain"
echo ""
echo "🏥 Health check endpoint:"
echo "   curl \$(railway domain)/health"