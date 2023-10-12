FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY api /code/api
COPY owen_counter /code/owen_counter
COPY owen_poller /code/owen_poller
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
