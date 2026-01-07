FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY streamlit_app/ .
EXPOSE 8501

RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]