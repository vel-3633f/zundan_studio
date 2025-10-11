FROM python:3.11-slim

# Install system dependencies including Poetry and Japanese fonts
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-dri \
    curl \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fontconfig \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# Install Poetry
RUN pip install poetry

# Configure Poetry: Don't create virtual env since we're in Docker
RUN poetry config virtualenvs.create false

# Set working directory
WORKDIR /app

# Copy Poetry configuration files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies with Poetry
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/outputs /app/temp /app/assets/zundamon /app/assets/backgrounds

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run streamlit
CMD ["sh", "-c", "streamlit run main.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true --server.fileWatcherType=none"]