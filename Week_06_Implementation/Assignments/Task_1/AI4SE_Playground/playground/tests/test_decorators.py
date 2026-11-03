"""Unit tests for the decorators module."""
from __future__ import annotations

import unittest

from playground.decorators import AuditTrail


class AuditTrailConstructionTests(unittest.TestCase):
    def test_default_label_and_empty(self) -> None:
        trail = AuditTrail()
        self.assertEqual(len(trail), 0)
        self.assertEqual(trail.entries, ())

    def test_custom_label_accepted(self) -> None:
        self.assertIsInstance(AuditTrail("ops"), AuditTrail)

    def test_non_str_label_rejected(self) -> None:
        with self.assertRaises(TypeError):
            AuditTrail(5)  # type: ignore[arg-type]

    def test_empty_label_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AuditTrail("")

    def test_blank_label_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AuditTrail("   ")


class AuditTrailCallTests(unittest.TestCase):
    def test_non_callable_rejected(self) -> None:
        trail = AuditTrail()
        with self.assertRaises(TypeError):
            trail(42)  # type: ignore[arg-type]

    def test_success_records_ok_and_returns_result(self) -> None:
        trail = AuditTrail("audit")

        @trail
        def add(a: int, b: int) -> int:
            return a + b

        self.assertEqual(add(2, 3), 5)
        self.assertEqual(trail.entries, ("audit:add:ok",))

    def test_exception_records_error_and_reraises(self) -> None:
        trail = AuditTrail("audit")

        @trail
        def fail() -> None:
            raise ValueError("bad")

        with self.assertRaises(ValueError):
            fail()
        self.assertEqual(trail.entries, ("audit:fail:error:ValueError",))

    def test_error_type_name_reflects_exception_class(self) -> None:
        trail = AuditTrail("t")

        @trail
        def boom() -> None:
            raise KeyError("x")

        with self.assertRaises(KeyError):
            boom()
        self.assertEqual(trail.entries, ("t:boom:error:KeyError",))

    def test_wrapper_preserves_metadata(self) -> None:
        trail = AuditTrail()

        @trail
        def documented(x: int) -> int:
            """Doc string."""
            return x

        self.assertEqual(documented.__name__, "documented")
        self.assertEqual(documented.__doc__, "Doc string.")

    def test_passes_args_and_kwargs(self) -> None:
        trail = AuditTrail()

        @trail
        def f(a: int, *rest: int, key: str = "k") -> str:
            return f"{a}-{len(rest)}-{key}"

        self.assertEqual(f(1, 2, 3, key="z"), "1-2-z")

    def test_multiple_calls_accumulate_in_order(self) -> None:
        trail = AuditTrail("x")

        @trail
        def ok() -> None:
            return None

        @trail
        def bad() -> None:
            raise RuntimeError()

        ok()
        with self.assertRaises(RuntimeError):
            bad()
        ok()
        self.assertEqual(
            trail.entries,
            ("x:ok:ok", "x:bad:error:RuntimeError", "x:ok:ok"),
        )
        self.assertEqual(len(trail), 3)

    def test_same_trail_shared_between_functions(self) -> None:
        trail = AuditTrail("s")

        @trail
        def one() -> int:
            return 1

        @trail
        def two() -> int:
            return 2

        one()
        two()
        self.assertEqual(trail.entries, ("s:one:ok", "s:two:ok"))

    def test_base_exception_not_caught_but_not_recorded(self) -> None:
        trail = AuditTrail()

        @trail
        def interrupt() -> None:
            raise KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            interrupt()
        self.assertEqual(trail.entries, ())


class AuditTrailEntriesClearTests(unittest.TestCase):
    def test_entries_is_snapshot_tuple(self) -> None:
        trail = AuditTrail("a")

        @trail
        def f() -> None:
            return None

        f()
        snap = trail.entries
        f()
        self.assertEqual(snap, ("a:f:ok",))
        self.assertEqual(trail.entries, ("a:f:ok", "a:f:ok"))

    def test_clear_empties(self) -> None:
        trail = AuditTrail("a")

        @trail
        def f() -> None:
            return None

        f()
        f()
        trail.clear()
        self.assertEqual(len(trail), 0)
        self.assertEqual(trail.entries, ())

    def test_clear_on_empty_is_noop(self) -> None:
        trail = AuditTrail()
        trail.clear()
        self.assertEqual(len(trail), 0)

    def test_recording_resumes_after_clear(self) -> None:
        trail = AuditTrail("a")

        @trail
        def f() -> None:
            return None

        f()
        trail.clear()
        f()
        self.assertEqual(trail.entries, ("a:f:ok",))


if __name__ == "__main__":
    unittest.main()
