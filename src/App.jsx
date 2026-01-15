import { useEffect, useState, useRef } from "react";
import "./App.css";

function App() {
  const [movies, setMovies] = useState([]);
  const timelineRef = useRef(null);

  // Charger les films depuis l'API FastAPI
  useEffect(() => {
    fetch("/api/movies")
      .then((res) => res.json())
      .then((data) => setMovies(data));
  }, []);

  // Grouper les films par année
  const groupedByYear = movies.reduce((acc, movie) => {
    acc[movie.year] = acc[movie.year] || [];
    acc[movie.year].push(movie);
    return acc;
  }, {});

  // Trier les années numériquement
  const years = Object.keys(groupedByYear)
    .sort((a, b) => Number(a) - Number(b));

  // Générer la liste des décennies
  const decades = Array.from(
    new Set(years.map((y) => Math.floor(Number(y) / 10) * 10))
  );

  // Scroll vers une année spécifique
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
      {/* Barre des dizaines */}
      <div className="decade-bar">
        {decades.map((decade) => (
          <button
            key={decade}
            className="decade-btn"
            onClick={() => {
              // trouver la première année de cette décennie existante
              const targetYear = years.find(
                (y) => Number(y) >= decade
              );
              if (targetYear) scrollToYear(targetYear);
            }}
          >
            {decade}s
          </button>
        ))}
      </div>

      {/* Timeline principale */}
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
