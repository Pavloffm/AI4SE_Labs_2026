# Repository chunking design

`chunk_repository.py` reads the Task 1 clone at `../Task_1/AI4SE_Playground` and writes `chunks.jsonl` in this directory. From `Task_2`, create the local environment and run the script with uv:

```bash
uv venv .venv
uv run --no-project python chunk_repository.py
```

The script has no third-party dependencies. The repository ignores `.venv`, so only the script, data, and report need to be submitted. Input and output paths are resolved relative to the script, not the current working directory.

The script includes Python source and tests plus `.gitignore`, which are the nonempty text files relevant to this clone, and skips empty files. It splits each file independently into at most **80 lines**, overlapping adjacent chunks by **10 lines**. Eighty lines keep chunks small enough to select a few for a coding task while preserving nearby definitions or test cases; the overlap retains context at boundaries. This is a line limit, not a guaranteed token limit, and a long function can still be split across chunks. A line-based method is intentionally simpler than language-aware parsing for this assignment.

Each JSONL record stores a stable `id`, a repository-relative `path`, inclusive `start_line` and `end_line`, and the original `text`. These fields let a later retrieval step identify a chunk and locate it in the source. Files are sorted before processing, so regenerating the dataset from unchanged inputs gives identical output. The current clone produces **73 chunks from 27 nonempty files**.
