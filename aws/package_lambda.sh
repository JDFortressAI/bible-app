#!/bin/bash

# Package Lambda function for deployment
echo "📦 Packaging Lambda function..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Copy Lambda function
cp lambda_function.py "$TEMP_DIR/"

# Create requirements.txt for Lambda dependencies
cat > "$TEMP_DIR/requirements.txt" << EOF
requests>=2.31.0
beautifulsoup4>=4.12.0
boto3>=1.28.0
EOF

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r "$TEMP_DIR/requirements.txt" -t "$TEMP_DIR/"

# Create zip file
echo "🗜️ Creating deployment package..."
cd "$TEMP_DIR"
zip -r ../mccheyne_lambda.zip . -x "*.pyc" "*/__pycache__/*"

# Move zip file back to aws directory
cd - > /dev/null  # Go back to aws directory
mv "$TEMP_DIR/../mccheyne_lambda.zip" ./mccheyne_lambda.zip

echo "✅ Lambda package created: mccheyne_lambda.zip"
echo "📁 Package size: $(du -h mccheyne_lambda.zip | cut -f1)"

# Cleanup
rm -rf "$TEMP_DIR"

echo "🚀 Ready for Terraform deployment!"