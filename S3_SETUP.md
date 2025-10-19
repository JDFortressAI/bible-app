# S3 Bible Cache Setup

This document explains how to configure the S3 Bible cache for both local development and AWS deployment.

## Overview

The application uses S3 to cache pre-processed Bible passages for the M'Cheyne reading plan. This improves performance and ensures consistent formatting with proper typography.

## Environment Variables

### Required Variables

- `S3_BUCKET`: The name of your S3 bucket for caching Bible passages
- `OPENAI_API_KEY`: Your OpenAI API key for the chat functionality

### Optional AWS Variables (for local development)

- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key  
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)

## Local Development Setup

### Prerequisites

1. Install uv (Python package manager):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or using pip
   pip install uv
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Option 1: Using AWS CLI Profile (Recommended)

1. Install and configure AWS CLI:
   ```bash
   aws configure
   ```

2. Set environment variables in `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   S3_BUCKET=your-s3-bucket-name-here
   ```

3. Test the S3 cache:
   ```bash
   uv run test_s3_cache.py
   ```

4. Run the application:
   ```bash
   uv run python run_local.py
   ```

### Option 2: Using Environment Variables

1. Set all variables in `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   S3_BUCKET=your-s3-bucket-name-here
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_DEFAULT_REGION=us-east-1
   ```

2. Test the S3 cache:
   ```bash
   uv run test_s3_cache.py
   ```

3. Run the application:
   ```bash
   uv run python run_local.py
   ```

## Docker Development

### Using Docker Compose

1. Ensure your `.env` file is configured (see above)

2. Build and run:
   ```bash
   docker-compose up --build
   ```

3. Access the application at http://localhost:8501

### Using Docker directly

1. Build the image:
   ```bash
   docker build -t bible-chat .
   ```

2. Run with environment variables:
   ```bash
   docker run -p 8501:8501 \
     -e OPENAI_API_KEY=your_key \
     -e S3_BUCKET=your_bucket \
     bible-chat
   ```

## AWS Deployment

The AWS deployment is handled automatically through Terraform:

1. The S3 bucket is created with a random suffix
2. The ECS task definition includes the S3_BUCKET environment variable
3. IAM roles provide necessary S3 permissions

### Terraform Configuration

The infrastructure includes:
- S3 bucket with versioning and encryption
- Lambda function for weekly Bible passage updates
- ECS task with S3 read/write permissions
- EventBridge rule for automated updates

## Cache Structure

Bible passages are cached in S3 with the following structure:

```
mcheyne_structured_MM_DD.json
```

Where MM is the month (01-12) and DD is the day (01-31).

### Cache File Format

```json
{
  "format_version": "1.0",
  "date": "10/19",
  "cached_at": "2024-10-19T12:00:00",
  "Family": [
    {
      "reference": "Genesis 1",
      "version": "NKJV",
      "verses": [...],
      "highlights": [],
      "fetched_at": "2024-10-19T12:00:00"
    }
  ],
  "Secret": [...]
}
```

## Fallback Behavior

The S3 cache includes intelligent fallback:

1. Try to load today's readings
2. If not found, try tomorrow's readings
3. If not found, try yesterday's readings
4. If none found, fall back to local cache or direct fetching

## Testing

Run the test script to verify S3 connectivity:

```bash
uv run test_s3_cache.py
```

This will:
- Check environment variables
- Test S3 connectivity
- Attempt to load cached readings
- Display passage information if successful

## Troubleshooting

### Common Issues

1. **S3_BUCKET not set**: Ensure the environment variable is configured
2. **AWS credentials not found**: Configure AWS CLI or set environment variables
3. **Permission denied**: Ensure your AWS credentials have S3 read/write permissions
4. **Bucket not found**: Verify the bucket name and region

### Debug Mode

Set logging level to DEBUG to see detailed S3 operations:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```