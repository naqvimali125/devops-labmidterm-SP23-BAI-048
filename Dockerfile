FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Packages first, so this slow layer is cached between builds
COPY requirements.txt requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

COPY . .

# Retrain on the latest dataset while building the image
ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}
RUN python train.py

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
