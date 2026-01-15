import { useEffect, useState, useRef } from "react";
import "./App.css";

function App() {
  const [movies, setMovies] = useState([]);
  const [imdbID, setImdbID] = useState("");
  const timelineRef = useRef(null);

  const loadMovies = () => {
    fetch("/api/movies")
      .then((res) => res.json())
      .then((data) => setMovies(data));
  };

  useEffect(() => {
    loadMovies();
  }, []);

  const importMovie = async () => {
    if (!imdbID) return;

    await fetch(`/api/movies/import/${imdbID}`, {
      method: "POST",
    });

    setImdbID("");
    loadMovies();
  };

  const groupedByYear = movies.reduce((acc, movie) => {
    acc[movie.year] = acc[movie.year] || [];
    acc[movie.year].push(movie);
    return acc;
  }, {});

  const years = Object.keys(groupedByYear).sort((a, b) => Number(a) - Number(b));

  const decades = Array.from(
    new Set(years.map((y) => Math.floor(Number(y) / 10) * 10))
  );

  const scrollToYear = (year) => {
    const timeline = timelineRef.current;
    if (!timeline) return;
    const yearColumn = timeline.querySelector(`[data-year='${year}']`);
    if (yearColumn) {
      yearColumn.scrollIntoView({ behavior: "smooth", inline: "start" });
    }
  };

  return (
    <div className="container">
      {/* INPUT HAUT DROITE */}
      <div className="top-bar">
        <input
          type="text"
          placeholder="IMDb ID (ex: tt0017136)"
          value={imdbID}
          onChange={(e) => setImdbID(e.target.value)}
        />
        <button onClick={importMovie}>Importer</button>
      </div>

      {/* Barre des décennies */}
      <div className="decade-bar">
        {decades.map((decade) => (
          <button
            key={decade}
            className="decade-btn"
            onClick={() => {
              const targetYear = years.find((y) => Number(y) >= decade);
              if (targetYear) scrollToYear(targetYear);
            }}
          >
            {decade}s
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="timeline" ref={timelineRef}>
        {years.map((year) => (
          <div key={year} className="year-column" data-year={year}>
            <div className="year">{year}</div>
            <div className="movies">
              {groupedByYear[year].map((movie, i) => (
                <div key={i} className="movie">
                  <div className="poster-wrapper">
                    <img src={movie.poster} alt={movie.title} />
                    <div className="overlay">
                    <button
                        className="copy-btn"
                        onClick={() => navigator.clipboard.writeText(movie.title)}
                        title="Copier le titre"
                      >
                        ⧉
                      </button>
                      <a
                        className="title"
                        href={`https://www.imdb.com/title/${movie.imdbID}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {movie.title}
                      </a>
                      <div className="director">{movie.director}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
