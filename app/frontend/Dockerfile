# app/frontend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["streamlit", "run", "app/frontend/streamlit.py", "--server.port", "8001", "--server.address", "0.0.0.0"]