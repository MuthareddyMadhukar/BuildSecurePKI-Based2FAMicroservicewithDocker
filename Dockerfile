############################
# Stage 1: Builder
############################
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


############################
# Stage 2: Runtime
############################
FROM python:3.11-slim AS runtime

ENV TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps: cron + timezone
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Copy entire app source
COPY . /app

# (Extra safety) ensure cron script exists explicitly
COPY scripts/log_2fa_cron.py /app/scripts/log_2fa_cron.py

# Create data + cron dirs
RUN mkdir -p /data /cron && \
    chmod 755 /data /cron

# Install cron job
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron && \
    touch /var/log/cron.log

# Volumes
VOLUME ["/data", "/cron"]

# Expose API port
EXPOSE 8080

# Start cron and API
CMD ["sh", "-c", "cron && uvicorn main:app --host 0.0.0.0 --port 8080"]

