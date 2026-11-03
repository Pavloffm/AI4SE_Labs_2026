"""Split the Task 1 repository into line-addressable JSONL chunks."""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent / "Task_1" / "AI4SE_Playground"
OUTPUT = HERE / "chunks.jsonl"
CHUNK_LINES = 80
OVERLAP_LINES = 10


def main():
    records = []
    for path in sorted(REPOSITORY.rglob("*")):
        if not path.is_file() or (path.suffix != ".py" and path.name != ".gitignore"):
            continue

        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        relative_path = path.relative_to(REPOSITORY).as_posix()
        start = 0
        while start < len(lines):
            end = min(start + CHUNK_LINES, len(lines))
            records.append(
                {
                    "id": f"{relative_path}:{start + 1}-{end}",
                    "path": relative_path,
                    "start_line": start + 1,
                    "end_line": end,
                    "text": "".join(lines[start:end]),
                }
            )
            if end == len(lines):
                break
            start = end - OVERLAP_LINES

    OUTPUT.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    print(f"Wrote {len(records)} chunks to {OUTPUT}")


if __name__ == "__main__":
    main()
