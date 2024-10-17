FROM python:3.9-slim
RUN apt-get update && apt-get install -y python3-venv

WORKDIR /app
COPY requirements.txt .

RUN python3 -m venv .venv
RUN . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

COPY . .
CMD ["/bin/bash", "-c", ". .venv/bin/activate && python main.py"]