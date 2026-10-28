
# Personalized Movie Recommendation & Content Analytics Engine

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)

A modular Python recommendation system and data analysis pipeline that ingests raw movie catalog records and user rating histories to generate popularity metrics, genre aggregations, and personalized content recommendations.

---

## Technical Architecture & Features

```text
  [ Raw Data Ingestion ]
   ├── Pipe-delimited catalog parsing (moviesSample.txt)
   └── CSV user ratings ingestion (ratingsSample.csv)
             │
             ▼
  [ In-Memory Data Structuring ]
   ├── Indexing: pandas.DataFrame & inverted dict mappings
   └── Vectorized aggregations: Mean ratings per movie/genre
             │
             ▼
  [ Recommendation & Analytics Engine ]
   ├── Popularity Carousel: Top-N global ratings & threshold filters
   ├── Historical Ranking: Highest-rated movie by release year
   ├── User Profile Analysis: Weighted genre preference extraction
   └── Content Recommendation: Top-N unrated movies within user's preferred genre
