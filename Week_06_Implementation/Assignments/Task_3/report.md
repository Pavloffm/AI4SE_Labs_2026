# Chunk embedding and retrieval design

`embed_chunks.py` reads the 73 records in `../Task_2/chunks.jsonl` and creates `chunk_embeddings.sqlite3` here. Each database row pairs the original chunk ID, file path, inclusive line range and full text with its 384-dimensional embedding (JSON array). The committed database is the generated chunk–embedding store; rebuild it after regenerating Task 2 chunks.

From this directory, using Python 3 with no third-party packages:

```bash
python embed_chunks.py index
python embed_chunks.py embed 'reserve inventory'
python embed_chunks.py search 'inventory reservation and stock availability' --top 5
python -m unittest test_embed_chunks.py
```

The embedding includes the source path plus chunk text, so filename clues and code content both contribute. It extracts identifiers and numbers, splits compound snake_case/camelCase identifiers, weights repeated terms logarithmically, and hashes terms with a stable BLAKE2b digest into a signed 384-element vector. L2 normalization makes the dot product a cosine similarity. The same function embeds a problem statement at search time. SQLite stores the vectors alongside their source chunks and permits a simple full scan, scored and ranked by cosine similarity; 73 chunks are too few to justify an approximate-nearest-neighbor service or external database. Reindexing replaces stale entries.

This dependency-free approach is reproducible offline and keeps the generated store small. It is **lexical rather than pretrained semantic**: synonyms without shared tokens can be missed, hashing can collide, and long chunks may dilute important terms. A pretrained code/text embedding model would be a sensible upgrade for larger repositories or more conceptual questions, but would require model downloads and additional dependencies. For this dataset, searching for `inventory reservation and stock availability` ranks `inventory.py` chunks among the top matches.
