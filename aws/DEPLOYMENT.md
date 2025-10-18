# AWS Deployment Guide for Bible Chat App

This guide explains how to deploy the Bible Chat application with automated daily M'Cheyne readings updates.

## Architecture Overview

- **ECS Fargate**: Runs the Streamlit application
- **S3**: Stores cached Bible readings
- **Lambda**: Updates readings daily at 4AM GMT
- **EventBridge**: Triggers Lambda on schedule
- **ALB**: Load balancer with HTTPS

## Prerequisites

1. AWS CLI configured with appropriate permissions
2. Terraform installed
3. Docker installed
4. Domain name configured in DNS

## Deployment Steps

### 1. Package Lambda Function

```bash
cd aws
./package_lambda.sh
```

This creates `mccheyne_lambda.zip` with the Lambda function and dependencies.

### 2. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="domain_name=your-domain.com" -var="openai_api_key=your-openai-key"

# Apply infrastructure
terraform apply -var="domain_name=your-domain.com" -var="openai_api_key=your-openai-key"
```

### 3. Build and Push Docker Image

```bash
# Get ECR repository URL from Terraform output
ECR_REPO=$(terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Build image
docker build -t bible-chat ../

# Tag and push
docker tag bible-chat:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

### 4. Configure DNS

Add these DNS records to your domain:

1. **A Record**: Point your domain to the ALB DNS name (from Terraform output)
2. **Certificate Validation**: Add the DNS validation records shown in AWS Certificate Manager

### 5. Initial Data Population

The Lambda function will run automatically at 4AM GMT daily. To populate initial data:

```bash
# Get Lambda function name
LAMBDA_NAME=$(terraform output -raw lambda_function_name)

# Trigger manual execution
aws lambda invoke --function-name $LAMBDA_NAME response.json
cat response.json
```

## Environment Variables

The application uses these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `S3_BUCKET`: S3 bucket for Bible readings cache (auto-configured)

## Monitoring

### CloudWatch Logs

- **ECS Logs**: `/ecs/bible-chat`
- **Lambda Logs**: `/aws/lambda/bible-chat-mccheyne-updater`

### Lambda Function

- **Schedule**: Daily at 4AM GMT (`cron(0 4 * * ? *)`)
- **Timeout**: 5 minutes
- **Memory**: 128MB (default)

## Troubleshooting

### Lambda Function Issues

```bash
# Check Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/bible-chat"

# View recent logs
aws logs filter-log-events --log-group-name "/aws/lambda/bible-chat-mccheyne-updater" --start-time $(date -d "1 hour ago" +%s)000
```

### ECS Service Issues

```bash
# Check ECS service status
aws ecs describe-services --cluster bible-chat-cluster --services bible-chat-service

# View ECS logs
aws logs filter-log-events --log-group-name "/ecs/bible-chat" --start-time $(date -d "1 hour ago" +%s)000
```

### S3 Cache Issues

```bash
# List cache files
aws s3 ls s3://$(terraform output -raw s3_bucket_name)/

# Download cache file for inspection
aws s3 cp s3://$(terraform output -raw s3_bucket_name)/mcheyne_structured_2025_10_18.json ./
```

## Manual Cache Update

If you need to manually update the cache:

```bash
# Run the M'Cheyne fetcher locally
cd ..
uv run -m src.mccheyne --structured

# Upload to S3
aws s3 cp mcheyne_structured_$(date +%Y_%m_%d).json s3://$(terraform output -raw s3_bucket_name)/
```

## Cost Optimization

- **ECS**: Uses Fargate Spot for cost savings
- **Lambda**: Only runs once daily (minimal cost)
- **S3**: Standard storage with lifecycle policies
- **ALB**: Shared across multiple services if needed

## Security Features

- **S3**: Server-side encryption enabled
- **ECS**: Tasks run with minimal IAM permissions
- **Lambda**: Isolated execution environment
- **ALB**: HTTPS-only with modern TLS policies

## Scaling

The current setup handles moderate traffic. For higher loads:

1. Increase ECS task count
2. Use Application Auto Scaling
3. Consider CloudFront CDN
4. Implement Redis caching

## Backup and Recovery

- **S3**: Versioning enabled for cache files
- **Infrastructure**: Terraform state in S3 (recommended)
- **Application**: Stateless design enables easy recovery

## Updates

### Application Updates

```bash
# Build new image
docker build -t bible-chat ../
docker tag bible-chat:latest $ECR_REPO:latest
docker push $ECR_REPO:latest

# Force ECS deployment
aws ecs update-service --cluster bible-chat-cluster --service bible-chat-service --force-new-deployment
```

### Lambda Updates

```bash
# Repackage Lambda
./package_lambda.sh

# Update function
aws lambda update-function-code --function-name $(terraform output -raw lambda_function_name) --zip-file fileb://mccheyne_lambda.zip
```

## Support

For issues:

1. Check CloudWatch logs
2. Verify S3 cache files exist
3. Test Lambda function manually
4. Ensure ECS service is healthy
5. Validate DNS configuration