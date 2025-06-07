from fastapi import FastAPI, HTTPException
import duckdb
import pyreadstat
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement de la base de données
sav_file = "Employee.sav"
df, meta = pyreadstat.read_sav(sav_file)

# Connexion à DuckDB
conn = duckdb.connect('data.db')
conn.register("data", df)

class NLQueryModel(BaseModel):
    question: str
    limit: Optional[int] = 100

class QueryModel(BaseModel):
    sql: str
    limit: Optional[int] = 100

def is_safe_sql(sql: str) -> bool:
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "ATTACH", "DETACH"]
    return not any(word in sql.upper() for word in forbidden)

@app.get("/")
def read_root():
    return {"message": "API pour interroger les données employés"}

@app.post("/query/")
def execute_sql(query: QueryModel):
    try:
        sql = query.sql
        if not is_safe_sql(sql):
            raise HTTPException(status_code=400, detail="Requête SQL non autorisée")

        if "LIMIT" not in sql.upper() and query.limit is not None:
            sql += f" LIMIT {query.limit}"

        result = conn.execute(sql).fetchdf()
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


import requests

@app.post("/ask/")
def ask_question(input: NLQueryModel):
    try:
        sql = ask_llm_ollama(input.question)

        if not is_safe_sql(sql):
            raise HTTPException(status_code=400, detail="Requête SQL générée non autorisée")

        if "LIMIT" not in sql.upper() and input.limit:
            sql += f" LIMIT {input.limit}"

        result = conn.execute(sql).fetchdf()
        return {
            "question": input.question,
            "interpreted_sql": sql,
            "data": result.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import os

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

def ask_llm_ollama(question: str) -> str:
    prompt = f"""
Tu es un assistant SQL pour une base DuckDB. Ta tâche est de transformer les questions en langage naturel en requêtes SQL valides.

Voici les colonnes disponibles :
- datenais (date) : date de naissance
- educ (float) : nombre d'années d'éducation
- sexe (string) : m = masculin, f = féminin
- salact (float) : salaire actuel
- saldeb (float) : salaire de debut de carrière
- exp (float) : nombre de mois d'expérience

Exemples :
- "Quels sont les employés de plus de 50 ans ?" => SELECT * FROM data WHERE age > 50
- "Les salariés ayant plus de 10 ans d'ancienneté" => SELECT * FROM data WHERE exp > 10 * 12
- "Quel est le salaire moyen des employés ?" => SELECT AVG(salact) FROM data
- "Quel est le salaire moyen des employés de sexe masculin ?" => SELECT AVG(salact) FROM data WHERE sexe = 'm'
- "Quel est le salaire moyen des employés de sexe féminin ?" => SELECT AVG(salact) FROM data WHERE sexe = 'f'


N’inclus jamais de texte naturel, uniquement du SQL.
Ajoute LIMIT {input.limit} à la fin si nécessaire.

Maintenant, question : {question}
Requête SQL :
"""
    response = requests.post(OLLAMA_API_URL, json={
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"].strip()   
    

