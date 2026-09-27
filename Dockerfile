# Lightweight, reproducible Linux environment for Wiki Market Analyst
FROM python:3.11-slim

# Install system dependencies & TrueType Unicode fonts for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications and install
COPY wiki_market_analyst/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Set UTF-8 environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8

# Default entrypoint runs main.py
ENTRYPOINT ["python", "wiki_market_analyst/main.py"]
CMD ["--topic", "Intermittent fasting", "--langs", "pl,cs", "--years", "2"]
