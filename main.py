from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import psycopg2
import os
app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def load_movies():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            title,
            year,
            genre,
            director,
            poster,
            imdb_id
        FROM movies
        ORDER BY year
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "title": r[0],
            "year": r[1],
            "genre": r[2],
            "director": r[3],
            "poster": r[4],
            "imdbID": r[5],
        }
        for r in rows
    ]

# ---------- API ----------
@app.get("/api/movies")
def get_movies():
    return load_movies()

# ---------- vitejs ----------
BASE_DIR = Path(__file__).parent
dist_path = BASE_DIR / "dist"

app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    return FileResponse(dist_path / "index.html")
