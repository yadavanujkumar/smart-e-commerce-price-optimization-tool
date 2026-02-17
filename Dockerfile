# Stage 1: Base image for building the application
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Build the frontend assets
FROM node:16-alpine as frontend

# Set working directory
WORKDIR /frontend

# Copy frontend files
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install --no-cache

COPY frontend/ ./
RUN npm run build

# Stage 3: Final image for running the application
FROM base as final

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/ ./

# Copy built frontend assets
COPY --from=frontend /frontend/build ./frontend/build

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]