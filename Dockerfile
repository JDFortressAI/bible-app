FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY .env* ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY bible_chat.py ./

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["uv", "run", "streamlit", "run", "bible_chat.py", "--server.port=8501", "--server.address=0.0.0.0"]