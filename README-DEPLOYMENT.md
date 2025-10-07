# Bible Chat - AWS Deployment Guide

This guide will help you deploy your Bible Chat application to AWS with full CI/CD pipeline.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Domain name** registered and managed by Route53
3. **GitHub repository** for your code
4. **OpenAI API key**

## Required Tools

Install these tools on your local machine:

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Terraform
brew install terraform

# Docker
brew install docker
```

## Setup Steps

### 1. Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### 2. Prepare Configuration

```bash
# Copy and edit Terraform variables
cp aws/terraform.tfvars.example aws/terraform.tfvars

# Edit the file with your values:
# - domain_name: your-domain.com
# - openai_api_key: your-openai-api-key
# - aws_region: us-east-1 (or your preferred region)
```

### 3. Deploy Infrastructure

```bash
# Run the deployment script
./deploy.sh
```

This script will:
- Create all AWS infrastructure (VPC, ALB, ECS, ECR, etc.)
- Build and push your Docker image
- Deploy the application

### 4. Setup GitHub CI/CD

1. **Add GitHub Secrets** (Settings → Secrets and variables → Actions):
   ```
   AWS_ACCESS_KEY_ID: your-aws-access-key
   AWS_SECRET_ACCESS_KEY: your-aws-secret-key
   ```

2. **Update task-definition.json**:
   - Replace `YOUR_ACCOUNT_ID` with your AWS account ID
   - Replace `YOUR_OPENAI_API_KEY` with your actual API key

3. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add AWS deployment configuration"
   git push origin main
   ```

## Architecture Overview

```
Internet → Route53 → ALB → ECS Fargate → Streamlit App
                     ↓
                   ECR (Docker Images)
                     ↓
                 CloudWatch Logs
```

### Components Created

- **VPC**: Isolated network environment
- **Application Load Balancer**: HTTPS termination and traffic routing
- **ECS Fargate**: Serverless container hosting
- **ECR**: Docker image registry
- **Route53**: DNS management
- **ACM**: SSL certificate management
- **CloudWatch**: Logging and monitoring

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Triggers** on push to `main` branch
2. **Builds** Docker image
3. **Pushes** to ECR
4. **Updates** ECS service
5. **Deploys** new version

## Monitoring & Logs

- **Application logs**: CloudWatch → `/ecs/bible-chat`
- **Health checks**: ALB monitors `/_stcore/health`
- **Metrics**: ECS service metrics in CloudWatch

## Scaling

The current setup runs 1 container instance. To scale:

```bash
aws ecs update-service \
  --cluster bible-chat-cluster \
  --service bible-chat-service \
  --desired-count 3
```

## Cost Optimization

Current setup costs approximately:
- **ALB**: ~$16/month
- **ECS Fargate**: ~$6/month (1 task, 0.25 vCPU, 0.5GB RAM)
- **ECR**: ~$1/month
- **Route53**: ~$0.50/month
- **Total**: ~$23.50/month

## Troubleshooting

### Common Issues

1. **Domain not resolving**:
   - Ensure Route53 hosted zone exists
   - Check DNS propagation (can take up to 48 hours)

2. **SSL certificate issues**:
   - Verify domain ownership in ACM
   - Check certificate validation records in Route53

3. **ECS service not starting**:
   - Check CloudWatch logs for container errors
   - Verify environment variables are set correctly

4. **Health check failures**:
   - Ensure Streamlit health endpoint is accessible
   - Check security group rules

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster bible-chat-cluster --services bible-chat-service

# View logs
aws logs tail /ecs/bible-chat --follow

# Force new deployment
aws ecs update-service --cluster bible-chat-cluster --service bible-chat-service --force-new-deployment

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn $(aws elbv2 describe-target-groups --names bible-chat-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
```

## Security Best Practices

- ✅ HTTPS enforced with SSL certificate
- ✅ Security groups restrict access appropriately
- ✅ ECS tasks run with minimal IAM permissions
- ✅ Container images scanned for vulnerabilities
- ✅ Secrets managed through environment variables

## Cleanup

To destroy all resources:

```bash
cd aws
terraform destroy
```

**Warning**: This will permanently delete all resources and data.

## Support

For issues with this deployment:
1. Check CloudWatch logs first
2. Verify all configuration values
3. Ensure AWS permissions are correct
4. Check GitHub Actions logs for CI/CD issues