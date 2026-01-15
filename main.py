from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import psycopg2
import os
import requests

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- ENV ----------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
OMDB_URL = "https://www.omdbapi.com/"
# -------------------------

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def to_int(v):
    try:
        return int(v)
    except:
        return None

def to_float(v):
    try:
        return float(v)
    except:
        return None

# ---------- API ----------
@app.get("/api/movies")
def get_movies():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT title, year, genre, director, poster, imdb_id
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

# ---------- NOUVELLE ROUTE ----------
@app.post("/api/movies/import/{imdb_id}")
def import_movie(imdb_id: str):
    params = {
        "apikey": OMDB_API_KEY,
        "i": imdb_id,
        "r": "json"
    }

    response = requests.get(OMDB_URL, params=params)
    response.raise_for_status()
    data = response.json()

    if data.get("Response") != "True":
        raise HTTPException(status_code=404, detail=data.get("Error"))

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO movies (
            title, year, rated, released, runtime, genre, director,
            writer, actors, plot, language, country, awards, poster,
            metascore, imdb_rating, imdb_votes, imdb_id, boxoffice
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (imdb_id) DO UPDATE SET
            title = EXCLUDED.title,
            year = EXCLUDED.year,
            genre = EXCLUDED.genre,
            director = EXCLUDED.director,
            poster = EXCLUDED.poster,
            imdb_rating = EXCLUDED.imdb_rating
    """, (
        data.get("Title"),
        to_int(data.get("Year")),
        data.get("Rated"),
        data.get("Released"),
        data.get("Runtime"),
        data.get("Genre"),
        data.get("Director"),
        data.get("Writer"),
        data.get("Actors"),
        data.get("Plot"),
        data.get("Language"),
        data.get("Country"),
        data.get("Awards"),
        data.get("Poster"),
        to_int(data.get("Metascore")),
        to_float(data.get("imdbRating")),
        data.get("imdbVotes"),
        data.get("imdbID"),
        data.get("BoxOffice")
    ))

    conn.commit()
    cur.close()
    conn.close()

    return data

# ---------- FRONT ----------
BASE_DIR = Path(__file__).parent
dist_path = BASE_DIR / "dist"

app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    return FileResponse(dist_path / "index.html")
