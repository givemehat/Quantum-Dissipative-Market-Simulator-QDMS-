FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project (needs q_engine and classical_bridge)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "classical_bridge.app:app", "--host", "0.0.0.0", "--port", "8000"]
