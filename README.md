# Language Asymmetry in Kazakhstan's E-Government Retrieval (Kazakh vs. Russian)

**Status: in progress.** Results below are from the current experiments; the analysis of *why* the gap exists is not done yet.

## Research question

eGov.kz publishes the same government services in Kazakh and Russian. Kazakh is a low-resource language. Does retrieval work equally well in both languages when the content is the same, and if not, does the gap come from the data or from the retrieval method?

## Approach

Two stages:

1. **Pipeline validation on KazQAD** (Kazakh QA dataset): compare retrieval methods and embedding models on labeled data, and pick the embedding model for the main experiment.
2. **Main experiment on eGov.kz**: run the validated methods on parallel Kazakh/Russian government service pages.

Methods: TF-IDF, BM25, hybrid (sparse + dense), and dense retrieval with sentence embeddings.
Metrics: precision@k, recall@k, MRR (k = 5).

## Data

- **KazQAD validation:** 548 queries, 5,701-passage pool.
- **eGov.kz:** crawled the full category tree (88 subcategories, 939 unique service codes, 0 failed fetches). Kazakh and Russian pages have near-identical length (median body-length ratio ~1.01).
- **Setup:** page title as the query, page body as the document to retrieve.
- **Robustness subset:** excluded 65 services where either language had a very short body (< 200 characters), leaving 874 queries per language (Kazakh: 1,348 chunks, Russian: 1,379 chunks).

## Results

### Stage 1: KazQAD validation (MRR)

| Method | MRR |
|---|---|
| TF-IDF | 0.434 |
| BM25 | 0.428 |
| Hybrid | 0.467 |
| Dense, all-MiniLM-L6-v2 (English-only) | 0.008 |
| Dense, paraphrase-multilingual-MiniLM-L12-v2 | 0.133 |
| Dense, multilingual-e5-large | 0.608 |

multilingual-e5-large was selected for the main experiment.

### Stage 2: eGov.kz, robustness subset (874 queries per language), MRR

| Method | Kazakh | Russian |
|---|---|---|
| TF-IDF | 0.165 | 0.169 |
| BM25 | 0.176 | 0.162 |
| Hybrid | 0.179 | 0.174 |
| Dense (multilingual-e5-large) | 0.158 | 0.222 |

For the dense model, Russian is also ahead on the other metrics (precision@5: 0.086 vs. 0.066, recall@5: 0.303 vs. 0.241).

### Main finding

Sparse methods show no consistent gap between the languages. The dense model does: Russian MRR is about 40% higher than Kazakh, computed as (0.222 - 0.158) / 0.158. Because the content is near-parallel and sparse retrieval shows no gap, the difference likely comes from how the embedding model handles Kazakh rather than from the data. This is a hypothesis, not yet tested.

## Limitations and next steps

- KazQAD is Wikipedia text, so it is an imperfect proxy for government-service text when choosing the embedding model.
- Only one dense model (multilingual-e5-large) was used on eGov.kz.
- Planned: compare tokenization of Kazakh vs. Russian, test a second multilingual embedding model, and test whether Kazakh lemmatization changes the gap.

## Repository structure

- `kazqad/`: Stage 1 validation
- `egov/`: crawler and Stage 2 experiments (notebook: `egov_exploration.ipynb`)
- `src/`: shared retrieval code
- `results/`: saved metrics
- `requirements.txt`: dependencies

## How to run

```bash
pip install -r requirements.txt
```

Run the experiments in `kazqad/` first (validation), then in `egov/` (main experiment).
