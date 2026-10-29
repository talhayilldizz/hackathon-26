FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Install system dependencies needed for Playwright and chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    librandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Install Playwright and chromium browser
RUN playwright install --with-deps chromium

# Copy project files
COPY . .

# Expose port (7860 is default for Hugging Face Spaces, can be overridden by other platforms via PORT env var)
EXPOSE 7860

# Run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app
