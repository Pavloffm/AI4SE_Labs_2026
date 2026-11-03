# Embedding matching design

`match_embeddings.py` accepts a precomputed task embedding as a JSON array of 384 finite numbers, matching Task 3's hashed embedding format. It reads the chunk–embedding pairs from `../Task_3/chunk_embeddings.sqlite3` without rebuilding or changing the database. Example from this directory:

```bash
python ../Task_3/embed_chunks.py embed 'inventory reservation and stock availability' > /tmp/task_embedding.json
python match_embeddings.py /tmp/task_embedding.json --top 5
python -m unittest test_match_embeddings.py
```

The query is normalized before scoring; Task 3 stores unit-length chunk vectors. Their dot product is therefore cosine similarity, so query magnitude does not affect ranking. The script sorts by descending score, breaking ties by chunk ID, and returns up to `--top` results as JSON with the source path, line range, text, embedding and score. It rejects malformed, zero or non-finite query vectors and nonpositive `--top` values. A full SQLite scan is simple and exact for the current small collection (73 chunks); an approximate vector index would add complexity without a useful speedup here. Matching remains limited by Task 3's lexical hashed embeddings: synonyms without shared terms may not rank highly.
