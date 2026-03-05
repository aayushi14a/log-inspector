FROM python:3.12-slim

WORKDIR /app

# Copy the entire repo (backend needs tools/ from root)
COPY . .

# Install backend dependencies only
RUN pip install --no-cache-dir -r backend/requirements.txt

# Work from the backend directory
WORKDIR /app/backend

EXPOSE 8000

CMD python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
