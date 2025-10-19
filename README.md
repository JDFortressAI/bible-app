# Bible Chat

A comprehensive Bible-focused chat application with M'Cheyne reading plan integration and OpenAI-powered conversations.

## Features

- **M'Cheyne Reading Plan**: Daily Bible readings with proper typography and formatting
- **Bible-grounded chat**: AI conversations with explicit NKJV Bible references
- **S3 Cache Integration**: Fast loading of pre-processed Bible passages
- **Proper Typography**: Smart quotes, em dashes, and divine name formatting
- **Question suggestions**: UI includes helpful prompts for different types of biblical inquiries
- **Chat history**: Maintains conversation context
- **NKJV focus**: Uses New King James Version text exclusively
- **AWS Deployment**: Production-ready with ECS, Lambda, and S3

## Quick Start

1. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key and S3 bucket (optional)
   ```

4. **Run the application:**
   ```bash
   make run
   # or
   uv run python run_local.py
   ```

## Development Commands

Use the included Makefile for common tasks:

```bash
make help          # Show all available commands
make install       # Install dependencies
make test          # Run tests
make test-s3       # Test S3 cache functionality
make run           # Run the application locally
make docker-build  # Build Docker image
make docker-run    # Run with Docker Compose
make clean         # Clean up cache files
make dev           # Full development setup
```

## Usage

1. Open the app in your browser (typically http://localhost:8501)
2. Check the sidebar for question suggestions across different categories
3. Type your Bible-related question in the chat input
4. Receive Scripture-grounded responses with explicit NKJV references
5. Continue the conversation - chat history is maintained

## Question Categories

The app handles various types of biblical inquiries:
- **Spiritual Growth**: Prayer, closeness to God, handling difficulties
- **Life Guidance**: Relationships, love, work, decision-making
- **Faith Questions**: Salvation, Gospel, God's love, afterlife
- **Character Development**: Patience, forgiveness, anger, humility
- **Biblical Topics**: Money, suffering, wisdom, temptation

## Architecture

### Local Development
- **uv**: Modern Python package manager for dependency management
- **Streamlit**: Web interface for Bible chat and reading plan
- **OpenAI API**: LLM-powered Bible conversations
- **Local Cache**: JSON files for Bible passages when S3 is unavailable

### AWS Production
- **ECS Fargate**: Containerized application hosting
- **S3**: Bible passage cache with proper typography
- **Lambda**: Weekly M'Cheyne reading updates
- **EventBridge**: Automated scheduling for reading updates
- **ALB**: Load balancing with SSL termination

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for chat functionality
- `S3_BUCKET`: Optional S3 bucket for Bible passage cache
- `AWS_*`: AWS credentials (optional for local development)

See [S3_SETUP.md](S3_SETUP.md) for detailed configuration instructions.

## Deployment

### Local Development
```bash
make dev  # Install, test, and run locally
```

### Docker
```bash
make docker-run  # Run with Docker Compose
```

### AWS
The application deploys to AWS using Terraform. See `aws/` directory for infrastructure configuration.

## Technical Features

- **Proper Typography**: Smart quotes, em dashes, small caps for divine names
- **Intelligent Caching**: S3-first with local fallback
- **Performance Optimized**: Pre-processed Bible passages for fast loading
- **Scalable Architecture**: AWS-native with auto-scaling capabilities
- **Health Monitoring**: Built-in health checks and logging