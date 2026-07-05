# Rice Productivity Clustering — Deli Serdang

A Streamlit application that clusters the 22 districts (kecamatan) of Kabupaten Deli Serdang, Indonesia, by rice productivity and flags statistically unusual districts using Isolation Forest. Built as an undergraduate thesis project, with a focus on turning five years of raw government agricultural reports into something a policymaker could actually use.

![Dashboard](dashboard.png)

## Why this exists

Local agriculture offices publish yearly harvest reports per district, but the raw spreadsheets don't make it obvious which districts are underperforming, which are outliers worth investigating, and which are doing well enough to study as a model. This project turns that raw data into an interactive clustering tool: pick a year, tune the model, and get districts grouped into High / Medium / Low productivity plus a separate Anomaly group for data points that don't fit any cluster.

## How it works

1. **Ingestion** — parses the Dinas Pertanian's report format (12 months × 3 metrics per district) directly from CSV, computing productivity as Produksi ÷ Luas Panen and validating it against a realistic range (with a fallback correction for reports that report yield in quintals instead of tons).
2. **Aggregation** — rolls monthly figures up to yearly totals per district, using a harvest-area-weighted average rather than a naive mean of monthly ratios.
3. **Anomaly detection** — an Isolation Forest scores every district on productivity, harvest area, and production volume; the lowest-scoring fraction (tunable, default 15%) is flagged as anomalous.
4. **Clustering** — the remaining districts are grouped with K-Means (2-3 clusters) and labeled High/Medium/Low based on their actual productivity, so the label always tracks the number rather than an arbitrary cluster ID.
5. **Reporting** — results, charts, and per-cluster policy recommendations, all exportable as CSV.

![Results](result.png)

## Features

- Session-based login (swap in your own users via Streamlit secrets, see below)
- Yearly and monthly data views with filtering and CSV export
- Adjustable Isolation Forest parameters (contamination rate, estimator count)
- Cluster + anomaly visualization: pie chart, sorted bar chart, scatter plot
- Per-cluster statistics and recommendation text

## Tech stack

| Layer | Tool |
|---|---|
| UI / app framework | Streamlit |
| Data wrangling | pandas, NumPy |
| Modeling | scikit-learn (IsolationForest, KMeans, StandardScaler) |
| Charts | Matplotlib |

## Project structure

```
.
├── main.py                  # entry point: auth + navigation shell
├── auth.py                  # login (reads credentials from st.secrets/env)
├── pages/
│   ├── 1_dashboard.py       # overview + yearly trend
│   ├── 2_data.py            # yearly/monthly data browser
│   ├── 3_perhitungan.py     # clustering parameters + run
│   └── 4_hasil.py           # results, charts, recommendations
├── utils/
│   ├── data_loader.py       # CSV parsing + aggregation
│   └── anomaly_detector.py  # Isolation Forest + KMeans pipeline
├── data/                    # yearly CSV reports (2020-2024)
└── requirements.txt
```

## Running locally

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
streamlit run main.py
```

The app opens at `http://localhost:8501`. Default demo login is `admin` / `admin123` (see **Credentials** below to change this before deploying anywhere public).

### Credentials

Login credentials are no longer hardcoded in source. Set them up one of two ways:

**Option A — Streamlit secrets (recommended)**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml with your own username/password
```

**Option B — environment variables**
```bash
export APP_USERNAME=youruser
export APP_PASSWORD=yourpassword
```

If neither is set, the app falls back to the demo credentials above so it still runs out of the box.

## Dataset

Five yearly CSV reports (2020-2024) from Kabupaten Deli Serdang's agriculture office, covering 22 districts with monthly planting area, harvest area, and production volume. Place them in `data/` using the filenames already in this repo.

## A note on the analysis

The clustering thresholds shown in earlier drafts of this project (e.g. "productivity > 6.2 t/ha = High") were specific to one parameter combination and year — they'll shift depending on the contamination rate and estimator count you choose in the app, since both directly affect which districts get flagged as anomalies before clustering even runs. Rather than hardcode those numbers here, the app always recomputes and displays them live.

There's also a "demo variation" toggle on the clustering page that injects small random noise into productivity before analysis — this exists only to make the tool explorable with a very homogeneous slice of data, and defaults to off so the reported results reflect the real dataset.

## License

Built for academic purposes (undergraduate thesis, Informatics Engineering, Universitas Malikussaleh). Reuse elsewhere should credit the original author.

## Author

**Ardi Wirya Indarto**
Informatics Engineering, Universitas Malikussaleh
[LinkedIn](https://id.linkedin.com/in/ardiwiryaindarto) · ardiwiryaindarto1@gmail.com
