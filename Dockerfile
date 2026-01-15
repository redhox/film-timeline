# Étape 1 : build frontend Vite
FROM node:20-alpine AS frontend-build

WORKDIR /app

# Copier uniquement package.json et package-lock.json pour installer deps
COPY package*.json ./
RUN npm ci

# Copier le reste du frontend
COPY . .

# Build Vite
RUN npm run build

# Étape 2 : backend FastAPI
FROM python:3.13-slim

WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le build frontend + code backend
COPY --from=frontend-build /app/dist ./dist
COPY main.py ./

# Exposer le port
EXPOSE 8000

# Lancer l’application FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
