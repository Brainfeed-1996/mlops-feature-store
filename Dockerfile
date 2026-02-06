FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "feature_store_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
