# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /Ecommerce

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd gcc libpq-dev

# Install Python dependencies
COPY requirements.txt /Ecommerce/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all files, including entrypoint
COPY . /Ecommerce/

# Make entrypoint executable
RUN chmod +x /Ecommerce/entrypoint.sh

# Expose port
EXPOSE 8000

# Entrypoint script
CMD ["sh", "/Ecommerce/entrypoint.sh"]