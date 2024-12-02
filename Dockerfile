# Stage 1: Build stage with dependencies
FROM python:3.10-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache libffi-dev gcc musl-dev

# Copy and install Python dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage with only runtime dependencies
FROM python:3.10-alpine

EXPOSE 8000
WORKDIR /app

# Copy only necessary runtime libraries from the builder stage
RUN apk add --no-cache libffi

# Copy application files and dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app

# Make the entrypoint script executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set entrypoint and default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-w", "8","--timeout","600", "reform_crm.wsgi"]