"""Unit tests for the util module."""
from __future__ import annotations

import unittest

from playground.util import chunked, ensure_positive_int, format_cents, normalize_sku


class NormalizeSkuTests(unittest.TestCase):
    def test_uppercases_and_strips(self) -> None:
        self.assertEqual(normalize_sku("  el-1001 "), "EL-1001")

    def test_accepts_minimum_length(self) -> None:
        self.assertEqual(normalize_sku("ABC"), "ABC")

    def test_accepts_maximum_length(self) -> None:
        self.assertEqual(normalize_sku("A" * 16), "A" * 16)

    def test_rejects_below_minimum_length(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            normalize_sku("AB")
        self.assertEqual(str(ctx.exception), "sku length must be 3..16")

    def test_rejects_above_maximum_length(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            normalize_sku("A" * 17)
        self.assertEqual(str(ctx.exception), "sku length must be 3..16")

    def test_length_checked_after_strip(self) -> None:
        with self.assertRaises(ValueError):
            normalize_sku("   ")

    def test_padding_does_not_count_toward_length(self) -> None:
        self.assertEqual(normalize_sku("   ABC   "), "ABC")

    def test_non_str_raises_type_error(self) -> None:
        for bad in (None, 1234, b"EL-1", ["EL-1001"]):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    normalize_sku(bad)  # type: ignore[arg-type]

    def test_invalid_characters_underscore(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            normalize_sku("EL_1001")
        self.assertEqual(str(ctx.exception), "invalid sku characters")

    def test_invalid_characters_inner_space(self) -> None:
        with self.assertRaises(ValueError):
            normalize_sku("EL 1001")

    def test_invalid_characters_punctuation(self) -> None:
        with self.assertRaises(ValueError):
            normalize_sku("EL.100")

    def test_invalid_characters_non_ascii(self) -> None:
        with self.assertRaises(ValueError):
            normalize_sku("\u00e9l-100")

    def test_allows_digits_and_dashes(self) -> None:
        self.assertEqual(normalize_sku("123-456"), "123-456")


class FormatCentsTests(unittest.TestCase):
    def test_zero(self) -> None:
        self.assertEqual(format_cents(0), "$0.00")

    def test_pads_single_digit_cents(self) -> None:
        self.assertEqual(format_cents(5), "$0.05")

    def test_typical_amount(self) -> None:
        self.assertEqual(format_cents(1234), "$12.34")

    def test_whole_dollars(self) -> None:
        self.assertEqual(format_cents(100), "$1.00")

    def test_large_amount(self) -> None:
        self.assertEqual(format_cents(1000000), "$10000.00")

    def test_bool_rejected(self) -> None:
        for bad in (True, False):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    format_cents(bad)  # type: ignore[arg-type]

    def test_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            format_cents(1.5)  # type: ignore[arg-type]

    def test_str_rejected(self) -> None:
        with self.assertRaises(TypeError):
            format_cents("5")  # type: ignore[arg-type]

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            format_cents(-1)


class EnsurePositiveIntTests(unittest.TestCase):
    def test_returns_value_when_positive(self) -> None:
        self.assertEqual(ensure_positive_int(1, "qty"), 1)
        self.assertEqual(ensure_positive_int(10 ** 6, "qty"), 10 ** 6)

    def test_bool_rejected_with_name_in_message(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            ensure_positive_int(True, "qty")
        self.assertEqual(str(ctx.exception), "qty must be int")

    def test_false_rejected(self) -> None:
        with self.assertRaises(TypeError):
            ensure_positive_int(False, "qty")

    def test_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            ensure_positive_int(2.0, "qty")

    def test_str_rejected(self) -> None:
        with self.assertRaises(TypeError):
            ensure_positive_int("2", "qty")

    def test_none_rejected(self) -> None:
        with self.assertRaises(TypeError):
            ensure_positive_int(None, "qty")

    def test_zero_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ensure_positive_int(0, "steps")
        self.assertEqual(str(ctx.exception), "steps must be positive")

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ensure_positive_int(-3, "steps")


class ChunkedTests(unittest.TestCase):
    def test_even_split(self) -> None:
        self.assertEqual(list(chunked([1, 2, 3, 4], 2)), [[1, 2], [3, 4]])

    def test_partial_final_chunk(self) -> None:
        self.assertEqual(list(chunked(range(5), 2)), [[0, 1], [2, 3], [4]])

    def test_size_larger_than_input(self) -> None:
        self.assertEqual(list(chunked([1, 2], 5)), [[1, 2]])

    def test_size_equal_to_input_length(self) -> None:
        self.assertEqual(list(chunked([1, 2, 3], 3)), [[1, 2, 3]])

    def test_empty_input_yields_nothing(self) -> None:
        self.assertEqual(list(chunked([], 3)), [])

    def test_size_one(self) -> None:
        self.assertEqual(list(chunked("ab", 1)), [["a"], ["b"]])

    def test_chunks_are_lists(self) -> None:
        for chunk in chunked(range(4), 3):
            self.assertIsInstance(chunk, list)

    def test_accepts_generator_input(self) -> None:
        gen = (i * i for i in range(3))
        self.assertEqual(list(chunked(gen, 2)), [[0, 1], [4]])

    def test_invalid_size_zero_raises_on_first_next(self) -> None:
        gen = chunked([1], 0)
        with self.assertRaises(ValueError):
            next(gen)

    def test_invalid_size_negative_raises_on_first_next(self) -> None:
        gen = chunked([1], -2)
        with self.assertRaises(ValueError):
            next(gen)

    def test_invalid_size_bool_raises_type_error(self) -> None:
        gen = chunked([1], True)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            next(gen)

    def test_invalid_size_float_raises_type_error(self) -> None:
        gen = chunked([1], 2.0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            next(gen)


if __name__ == "__main__":
    unittest.main()
