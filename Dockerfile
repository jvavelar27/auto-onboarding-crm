FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

COPY . .

# Expose port for API
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "crm_automation.api:app", "--host", "0.0.0.0", "--port", "8000"]
