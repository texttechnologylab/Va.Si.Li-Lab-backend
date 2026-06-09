
FROM python:3.13-slim

WORKDIR /app


RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV API_BASE="http://host.docker.internal:11434/v1"
ENV API_KEY="ollama"
ENV MODEL_NAME="gpt-oss:20b"

EXPOSE 5000


ENTRYPOINT ["python", "app.py"]

CMD ["--server"]