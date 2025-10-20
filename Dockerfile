FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
  libnss3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
  libdrm2 libgtk-3-0 libpango-1.0-0 libxshmfence1 wget ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt && python -m playwright install --with-deps chromium

COPY app /app/app
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]