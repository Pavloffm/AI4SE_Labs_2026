"""Focused checks for the chunk embedding store and retrieval."""

import json
import math
from pathlib import Path
import sqlite3
import tempfile
import unittest

from embed_chunks import CHUNKS, DIMENSIONS, embed_chunk, index_chunks, search


class EmbeddingTests(unittest.TestCase):
    def test_embedding_is_deterministic_and_normalized(self):
        vector = embed_chunk("reserveInventory reserve_inventory")
        self.assertEqual(len(vector), DIMENSIONS)
        self.assertEqual(vector, embed_chunk("reserveInventory reserve_inventory"))
        self.assertAlmostEqual(math.sqrt(sum(value * value for value in vector)), 1)
        self.assertEqual(embed_chunk(""), [0.0] * DIMENSIONS)

    def test_store_contains_every_chunk_and_searches_it(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "chunks.sqlite3"
            expected = len(CHUNKS.read_text(encoding="utf-8").splitlines())
            self.assertEqual(index_chunks(CHUNKS, database), expected)
            with sqlite3.connect(database) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], expected)
                chunk_id, text, embedding = connection.execute(
                    "SELECT id, text, embedding FROM chunks LIMIT 1"
                ).fetchone()
                self.assertTrue(chunk_id and text)
                self.assertEqual(len(json.loads(embedding)), DIMENSIONS)
            self.assertTrue(any("inventory.py" in result[2] for result in
                                search("inventory reservation and stock availability", database)))
            self.assertEqual(index_chunks(CHUNKS, database), expected)
            with sqlite3.connect(database) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], expected)


if __name__ == "__main__":
    unittest.main()
