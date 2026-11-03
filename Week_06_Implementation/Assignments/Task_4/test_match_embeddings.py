"""Checks for embedding-to-chunk matching against the Task 3 schema."""

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from match_embeddings import DIMENSIONS, match_embeddings


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.database = Path(self.directory.name) / "chunks.sqlite3"
        with sqlite3.connect(self.database) as connection:
            connection.execute("""CREATE TABLE chunks (
                id TEXT PRIMARY KEY, path TEXT, start_line INTEGER, end_line INTEGER,
                text TEXT, embedding TEXT
            )""")
            for chunk_id, first, second in (("b", 1, 0), ("a", 1, 0), ("c", -1, 0)):
                vector = [first, second] + [0] * (DIMENSIONS - 2)
                connection.execute("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?)",
                                   (chunk_id, f"{chunk_id}.py", 1, 2, chunk_id,
                                    json.dumps(vector)))

    def test_ranks_and_limits_with_deterministic_ties(self):
        query = [3, 0] + [0] * (DIMENSIONS - 2)
        results = match_embeddings(query, self.database, 2)
        self.assertEqual([row["id"] for row in results], ["a", "b"])
        self.assertEqual([row["score"] for row in results], [1, 1])
        self.assertEqual(results[0]["text"], "a")
        self.assertEqual(results[0]["embedding"], [1, 0] + [0] * (DIMENSIONS - 2))
        self.assertEqual([row["id"] for row in match_embeddings(query, self.database, 10)],
                         ["a", "b", "c"])

    def test_invalid_queries(self):
        for query in ([], [0] * DIMENSIONS, [float("nan")] * DIMENSIONS,
                      [True] + [0] * (DIMENSIONS - 1)):
            with self.subTest(query=query[:2]), self.assertRaises(ValueError):
                match_embeddings(query, self.database)
        with self.assertRaises(ValueError):
            match_embeddings([1] * DIMENSIONS, self.database, 0)

    def test_missing_database_is_not_created(self):
        missing = Path(self.directory.name) / "missing.sqlite3"
        with self.assertRaises(sqlite3.OperationalError):
            match_embeddings([1] + [0] * (DIMENSIONS - 1), missing)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
