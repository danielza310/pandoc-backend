FROM python:3.9-slim

# Install system dependencies including Pandoc and LaTeX for PDF support
RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads output

# Test Pandoc installation
RUN pandoc --version

# Expose port (will be overridden by Railway's PORT env var)
EXPOSE 3000

# Run the application using Railway's PORT environment variable
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "--workers", "1", "--log-level", "info", "app:app"] 