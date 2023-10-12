FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
