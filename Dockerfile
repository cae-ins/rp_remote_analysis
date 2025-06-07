FROM python:3.9-slim-bookworm  
WORKDIR /app

# 1. Installer les dépendances système ESSENTIELLES
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Installer les pré-requis Python en premier
RUN pip install --upgrade pip && \
    pip install --no-cache-dir Cython>=0.28 wheel

# 3. Copier et installer les dépendances
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copier l'application
COPY ./app .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]