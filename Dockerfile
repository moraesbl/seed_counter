FROM python:3.9-slim

# Instala dependências de sistema para OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

WORKDIR /app

# Copia e instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Expõe a porta (Informativo)
EXPOSE 8000

# Roda o app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
