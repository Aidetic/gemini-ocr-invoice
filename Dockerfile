# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies for Pillow and Streamlit image support
RUN apt-get update && apt-get install -y \
    curl \
    libgl1 libglx-mesa0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Expose Streamlit port
EXPOSE 8036

# Run Streamlit app
CMD ["streamlit", "run", "ui_invoice.py", "--server.port=8036", "--server.address=0.0.0.0"]
