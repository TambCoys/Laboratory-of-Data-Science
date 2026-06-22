# Laboratory of Data Science — Decision Support System for a Music Streaming Company

> Project for the course **Decision Support Systems – Laboratory of Data Science (Module II)**
> University of Pisa · A.Y. 2025/2026
> Instructors: Anna Monreale, Cristiano Landi

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?logo=microsoftsqlserver&logoColor=white)
![SSIS](https://img.shields.io/badge/SSIS-ETL-0078D4)
![MDX](https://img.shields.io/badge/MDX-SSAS%20Cube-512BD4)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)

---

## What this is

The goal of the project is to simulate a **decision support system** for a music streaming company:
starting from two raw datasets, we clean and enrich them, build a **data warehouse**, populate it via
both Python and SSIS, build an **OLAP cube** on top of it queried through **MDX**, and finally
communicate the results with **interactive Power BI dashboards**.

In short, the full lifecycle of a DSS: *raw data -> ETL -> DW -> cube -> BI.*

### Group 4
- Fabrizio Anelli
- Emanuele Nardi
- Marco Tamberi

---

## The source data

| File | Content |
|------|---------|
| `tracks.json` | Main dataset: song details, audio features, lyrics information, and number of streams one month after release |
| `artists.xml` | Artist information: gender, age, birthplace, and a short description |


---

## Data Warehouse architecture

A star schema with a central fact table and dedicated dimensions, plus a **bridge table** to handle the
*many-to-many* relationship between songs and featured artists.

- **Fact:** `PublishedSong_Fact` — measures on duration, first-month streams, popularity, category, etc.
- **Dimensions:** `Dim_Album`, `Dim_Artist`, `Dim_Date`, `Dim_Symphony` (melodic/rhythmic features), `Dim_Text` (lyrics info)
- **Geography:** `Dim_Artist_Geography`, connected directly to `Dim_Artist`
- **Featuring:** `Dim_Feats` + `Feats_Bridge` for each track's collaborators

**Main hierarchies**
- *Date:* Day -> Month -> Year
- *Artist Geography:* City -> Province -> Region -> Country

---

## Project pipeline

The work is organized into **22 incremental assignments**, grouped into three phases.

### Phase 1 — Python (Assignments 1–7)
Data understanding, cleaning, and preparation (without pandas, except where explicitly allowed).

- **A1 – Data Understanding:** check for duplicates and missing values, first visualizations (artist distribution by region), proposal of new variables (*Aggressiveness*, *debut age*).
- **A2 – Data Cleaning:** geocoding of birthplaces via **Nominatim/OpenStreetMap**, computation of the **H3** index, date conversion to `YYYYMMDD`, recovery of missing years, derivation of the *season* variable and time keys.
- **A3 – Song Profiling:** clustering of songs on audio features (bpm, rolloff, flux, rms, flatness, spectral complexity, pitch, loudness). Comparison of *hierarchical*, *HDBSCAN*, and *K-Means* -> final choice **K-Means with K = 7**.
- **A4 – DW Schema:** design of the schema with dimensions, hierarchies, and bridge table.
- **A5 – Data Preparation:** split of the data into CSVs, one per DW table, with surrogate-key handling.
- **A6 – Data Uploading (Python):** load into SQL Server via ODBC, using `IDENTITY_INSERT` and a logical load order.
- **A7 – Data Uploading (SSIS):** duplication of the tables (`*_SSIS`) and population with a **30%** sample of the fact table only, to preserve referential integrity.

#### The 7 music categories derived from clustering
| Category | Distinctive trait |
|----------|-------------------|
| **Minimal** | lowest spectral complexity (low loudness/rms/flux) |
| **Fast-Flow** | highest bpm |
| **Melodic** | high average pitch |
| **Slow Dark** | lowest bpm and rolloff |
| **Clean** | lowest flatness |
| **Warm Bangers** | highest loudness, rms, and pitch |
| **Hype** | highest spectral complexity and rolloff, high loudness |

### Phase 2 — SSIS (Assignments 8–13)
ETL and business questions solved client-side with native SSIS components (preferring *Lookup* over *Merge Join* where possible).

- **A8:** for each year, artists ordered by number of published songs.
- **A9:** *summer–winter score* per region (by number of songs and by streams).
- **A10:** ratio of streams per category/region vs. total streams for that category across other regions.
- **A11:** *trending/flopping* statistics per artist (with edge-case handling for artists with 1 or 2 songs).
- **A12:** *Singles Performance* — how much singles outperform other release types.
- **A13:** relationship between number of featurings and *trending* tracks (record-label consultancy).

### Phase 3 — MDX & Power BI (Assignments 14–22)
OLAP cube construction, analytical MDX queries, and interactive dashboards.

- **A14:** construction of the **datacube** (`Group4_DSV`), hierarchies, many-to-many handling, and calculated measures.
- **A15:** monthly streams per region + Italy total.
- **A16:** *Average Weighted Streams* (weight 0.8 for main artist, 0.2 for featured).
- **A17:** year-over-year percentage change in streams per category.
- **A18:** categories exceeding the previous year's same-season average.
- **A19:** artist-level **seasonality** effects (a non-trivial insight for release timing).
- **A20:** dashboard — total streams by artist birthplace, segmented by category.
- **A21:** dashboard — relationship between *swear words* in lyrics and streaming performance (a power law was spotted along the way).
- **A22:** *ribbon chart* — evolution of category popularity over time.

---

## Repository structure

> The structure below reflects the project phases; adjust it to the actual folder names if they differ.

```
Laboratory-of-Data-Science/
├── python/                 # Assignments 1–7: data understanding, cleaning, profiling, prep & upload
│   ├── data_understanding/
│   ├── data_cleaning/
│   ├── song_profiling/
│   └── data_preparation/
├── ssis/                   # Assignments 7–13: SSIS project (.dtsx) and ETL
├── mdx/                    # Assignments 15–19: MDX queries
│   ├── Assignment15.mdx
│   ├── Assignment16.mdx
│   ├── Assignment17.mdx
│   ├── Assignment18.mdx
│   └── Assignment19.mdx
├── powerbi/                # Assignments 20–22: interactive dashboards
│   ├── Assignment_20.pbix
│   ├── Assignment_21.pbix
│   └── Assignment_22.pbix
├── report/                 # Project PDF report
└── README.md
```

---

## Tech stack

- **Python** — data understanding, cleaning, and preparation (geocoding with Nominatim, H3 indices, K-Means clustering)
- **SQL Server (SSMS)** — data warehouse and database management
- **SQL Server Integration Services (SSIS)** — ETL and client-side business queries
- **SQL Server Analysis Services (SSAS) + MDX** — OLAP cube and multidimensional queries
- **Power BI** — interactive dashboards

---

## A few interesting insights

- In the **Melodic** genre, tracks with many swear words consistently perform poorly: better to avoid them.
- **Warm Bangers** perform best with very few swear words, yet they also have the smallest share of fully "clean" songs — a trade-off between style and commercial performance.
- **Warm Bangers** have dominated the charts in recent years, while **Fast-Flow** is losing ground to **Slow Dark**.
- Lombardy, Lazio, and Campania concentrate most of the streams by artist birthplace.

---

## Report

The full report, with all design choices, schemas, and visualizations, is available in the `report/`
folder.

---

<p align="center"><i>Made by Group 4, University of Pisa</i></p>
