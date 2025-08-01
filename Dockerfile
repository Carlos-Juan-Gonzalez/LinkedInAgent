FROM python:latest

WORKDIR /LinkedIn_Agent

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]