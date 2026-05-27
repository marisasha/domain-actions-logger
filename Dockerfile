FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    vim \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/requirements_linux.txt /app/requirements/requirements_linux.txt

RUN pip install --no-cache-dir -r /app/requirements/requirements_linux.txt

COPY . .

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]