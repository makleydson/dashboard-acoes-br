# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard is served at `http://localhost:8501`.

## Architecture

Three-file architecture with clear separation of concerns:

- **`data.py`** — Data layer. Fetches OHLCV data from Yahoo Finance via `yfinance`, calculates technical indicators (20/50-day moving averages, cumulative returns, daily variance), and computes KPIs. Contains the `TICKERS` and `COLORS` constants. All fetches are cached for 1 hour with `@st.cache_data(ttl=3600)`.
- **`charts.py`** — Charting layer. Four Plotly functions: `candlestick_chart()`, `line_chart()`, `performance_chart()` (multi-stock overlay), and `heatmap_chart()` (monthly returns). All use dark Plotly templates.
- **`app.py`** — UI orchestration. Renders the Streamlit sidebar (stock selector, date range, chart type toggle, data table toggle), calls `data.py` for data, passes results to `charts.py`, and displays KPIs and charts.

**Data flow:** sidebar inputs → `get_stock_data()` → technical indicator enrichment → `get_kpis()` / chart functions → Plotly figures rendered by Streamlit.

## Tracked Assets

Hardcoded in `data.py`:
- PETR4.SA (Petrobrás) — `#009B3A`
- ITUB4.SA (Itaú) — `#003087`
- VALE3.SA (Vale) — `#0066CC`

Default date range is full-year 2025 (`2025-01-02` to `2025-12-31`). UI text is in Portuguese.

## No Test Suite

There are no automated tests. Validate changes by running the app and exercising the UI.
