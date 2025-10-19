# GitHub CI/CD Deployment Fix

## Issues Found and Fixed

### 1. **Docker Build Failure** ❌ → ✅
**Problem**: Docker build was failing because `pyproject.toml` references `README.md` but the README file wasn't copied into the container before the `uv pip install` step.

**Error**:
```
OSError: Readme file does not exist: README.md
```

**Solution**: Updated `Dockerfile` to copy both `pyproject.toml` and `README.md` before running the install step:

```dockerfile
# Before (broken)
COPY pyproject.toml ./
RUN uv pip install --system -e .

# After (fixed)
COPY pyproject.toml README.md ./
RUN uv pip install --system -e .
```

### 2. **Missing S3_BUCKET Environment Variable** ❌ → ✅
**Problem**: The GitHub Actions workflow was only setting `OPENAI_API_KEY` but not `S3_BUCKET` in the ECS task definition.

**Solution**: Updated `.github/workflows/deploy.yml` to include both environment variables:

```yaml
environment-variables: |
  OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
  S3_BUCKET=${{ secrets.S3_BUCKET }}
```

## Required GitHub Secrets

Make sure these secrets are configured in your GitHub repository:

1. `AWS_ACCESS_KEY_ID` - AWS access key for deployment
2. `AWS_SECRET_ACCESS_KEY` - AWS secret key for deployment  
3. `OPENAI_API_KEY` - OpenAI API key for the application
4. `S3_BUCKET` - S3 bucket name (should be: `bible-chat-cache-9ec8fb6b`)

## Verification

✅ **Docker Build**: Tested locally and confirmed working
✅ **Environment Variables**: Both `OPENAI_API_KEY` and `S3_BUCKET` are now included
✅ **Workflow Syntax**: YAML is properly formatted
✅ **Dependencies**: All required files are copied in correct order

## Next Steps

1. Push these changes to trigger the CI/CD pipeline
2. Verify that the deployment completes successfully
3. Check that the application starts with both environment variables set
4. Confirm S3 cache is working in the deployed environment

The deployment should now work correctly! 🚀