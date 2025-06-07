# 🦆 projet-duckdb-fastapi

Ce projet est une API FastAPI conteneurisée qui permet d'interroger une base de données DuckDB en langage naturel via un LLM local (comme Ollama avec LLaMA 3). L'utilisateur peut envoyer des requêtes en français, qui sont traduites automatiquement en SQL.

---

## 🧩 Architecture du système

```text
 Utilisateur (curl / front)
          │
          ▼
   ┌────────────────────┐
   │     FastAPI        │
   │ (dans un conteneur)│
   └────────┬───────────┘
            │
     ┌──────▼───────┐
     │ DuckDB       │ ◄── Base de données locale (CSV, Parquet, etc.)
     └──────────────┘
            │
     ┌──────▼───────┐
     │ LLM local    │ ◄── Ollama avec Phi3-mini
     └──────────────┘
            │
            ▼
     Génération automatique de requête SQL
```

---

## ⚙️ Fonctionnalités

- Interrogation de DuckDB via langage naturel
- Traduction en SQL via un LLM local
- Limitation personnalisée (`limit`)
- Requête POST simple via `curl` ou front

---

## 📦 Prérequis

- [Docker](https://www.docker.com/)
- [Ollama](https://ollama.com/) installé et fonctionnel (`ollama serve` actif)
- Un modèle local (`phi3-mini`) téléchargé via :

```bash
ollama run phi3-mini
```

---

## 🚀 Déploiement

### 1. Cloner le projet

```bash
git clone https://github.com/cae-ins/rp_remote_analysis.git
cd rp_remote_analysis
```

### 2. Construire l’image Docker

```bash
sudo docker build -t projet-duckdb-fastapi .
```

### 3. Lancer le conteneur avec accès au réseau host

```bash
sudo docker run --network host projet-duckdb-fastapi
```

> Cela permet au conteneur d’accéder à `localhost:11434` (serveur Ollama).

---

## 🧪 Exemple d'utilisation

### ✅ Tester l’API `/ask/`

```bash
curl -X POST http://localhost:8000/ask/   -H "Content-Type: application/json"   -d '{"question": "Quels sont les 2 employés les mieux payés ?", "limit": 5}'
```

### ✅ Accéder à la documentation interactive

- Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON : [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 📁 Structure du projet

```text
rp_remote_analysis/
├── app/
│   ├── app.py             # Point d’entrée FastAPI, connexion duckdb
│   ├── Employee.sav       # jeu de données SPSS de base pour test, il sera remplacé par les données du RP21
│   ├── data.db            # base de données duckdb
│   └── index.html         # Interface HTML locale
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 💡 Améliorations possibles

- Authentification ou token API
- Traduction multilingue plus robuste
- Interface web avec formulaire intégré
- Log automatique des requêtes SQL générées

---

## 🧑‍💻 Auteurs

- **DataLab Anstat**
---

