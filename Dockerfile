FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt for dependency installation
COPY requirements.txt ./

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy all application files
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "src/bible_chat.py", "--server.port=8501", "--server.address=0.0.0.0"]