#!/bin/bash

# Bible Chat Deployment Script
set -e

echo "🚀 Starting Bible Chat deployment..."

# Check if required tools are installed
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed. Aborting." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }

# Check if terraform.tfvars exists
if [ ! -f "aws/terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found. Please copy terraform.tfvars.example and fill in your values."
    exit 1
fi

# Navigate to AWS directory
cd aws

echo "📋 Initializing Terraform..."
terraform init

echo "📋 Planning Terraform deployment..."
terraform plan

echo "🏗️  Applying Terraform configuration..."
terraform apply -auto-approve

echo "📝 Getting outputs..."
ECR_REPO=$(terraform output -raw ecr_repository_url)
DOMAIN_URL=$(terraform output -raw domain_url)

echo "✅ Infrastructure deployed successfully!"
echo "📦 ECR Repository: $ECR_REPO"
echo "🌐 Application URL: $DOMAIN_URL"

# Go back to root directory
cd ..

echo "🐳 Building and pushing initial Docker image..."

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push image
docker build -t bible-chat .
docker tag bible-chat:latest $ECR_REPO:latest
docker push $ECR_REPO:latest

echo "🔄 Updating ECS service..."
aws ecs update-service --cluster bible-chat-cluster --service bible-chat-service --force-new-deployment --region $AWS_REGION

echo "✅ Deployment complete!"
echo "🌐 Your Bible Chat app will be available at: $DOMAIN_URL"
echo "⏳ It may take a few minutes for the service to start and health checks to pass."