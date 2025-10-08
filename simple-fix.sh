#!/bin/bash

echo "🔧 Quick fix for Bible Chat deployment"

# Step 1: Start Docker Desktop if available
echo "Starting Docker Desktop..."
open -a Docker || echo "Docker Desktop not found - you'll need to install it from docker.com"

# Wait for Docker to start
echo "Waiting for Docker to start..."
sleep 10

# Step 2: Build and push image
echo "Building Docker image..."
docker build -t bible-chat .

echo "Tagging image..."
docker tag bible-chat:latest 530256939177.dkr.ecr.eu-west-2.amazonaws.com/bible-chat:latest

echo "Logging into ECR..."
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 530256939177.dkr.ecr.eu-west-2.amazonaws.com

echo "Pushing image..."
docker push 530256939177.dkr.ecr.eu-west-2.amazonaws.com/bible-chat:latest

echo "Forcing ECS service update..."
aws ecs update-service --cluster bible-chat-cluster --service bible-chat-service --force-new-deployment --region eu-west-2

echo "✅ Image pushed! Now add DNS record:"
echo "   Type: CNAME"
echo "   Name: bible.jdfortress.com"
echo "   Value: bible-chat-alb-859806385.eu-west-2.elb.amazonaws.com"