# Stage 1: Build & Dependency Gathering
FROM python:3.10-slim AS builder

WORKDIR /app

# Install native compiler tools for heavy scientific modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root to cache dependency wheels cleanly
COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Clean Lightweight Runtime Environment
FROM python:3.10-slim AS runner

WORKDIR /app

# Import compiled libraries from builder stage safely
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy the actual application resource source code tree
COPY . .

EXPOSE 8000

CMD ["uvicorn", "classical_bridge.app:app", "--host", "0.0.0.0", "--port", "8000"]