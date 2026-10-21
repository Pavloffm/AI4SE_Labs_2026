import tempfile
import unittest
from pathlib import Path

from requirements_network import load_documents, quality_gate, render_markdown


class RequirementsNetworkTests(unittest.TestCase):
    def test_load_documents_recurses_and_uses_relative_source_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sub").mkdir()
            (root / "sub" / "mail.eml").write_text("From: someone\nNeed a report.", encoding="utf-8")
            (root / "ignored.csv").write_text("skip", encoding="utf-8")
            self.assertEqual(load_documents(root), [{"source_id": "sub/mail.eml", "text": "From: someone\nNeed a report."}])

    def test_quality_gate_assigns_ids_and_accepts_valid_review(self):
        state = {
            "documents": [{"source_id": "source.txt", "text": "source"}],
            "requirements": [{"name": "Branch reports", "description": "The system shall provide a detailed report for each branch so library staff can audit missing items and monitor collection trends over time.", "source_ids": ["source.txt"], "evidence": ["report per branch"], "priority": "Should", "priority_basis": "Repeated operational need"}],
            "discarded": [], "review": {"complete": True, "issues": []}, "revision": 0,
        }
        result = quality_gate(state)
        self.assertEqual(result["requirements"][0]["id"], "REQ-001")
        self.assertEqual(result["status"], "reviewed")

    def test_quality_gate_rejects_dangling_source_and_caps_feedback(self):
        state = {
            "documents": [{"source_id": "source.txt", "text": "source"}],
            "requirements": [{"name": "A requirement", "description": "The system should offer a capability for managing library records and provide users with access to relevant operational information.", "source_ids": ["missing.txt"], "evidence": []}],
            "discarded": [], "review": {"complete": True, "issues": []}, "revision": 0,
        }
        result = quality_gate(state)
        self.assertEqual(result["status"], "revise")
        self.assertTrue(any("unknown source IDs" in issue for issue in result["issues"]))
        state["revision"] = 2
        self.assertEqual(quality_gate(state)["status"], "needs_human_review")

    def test_quality_gate_does_not_accept_unreconciled_candidates(self):
        result = quality_gate({
            "documents": [{"source_id": "source.txt", "text": "source"}],
            "requirements": [], "discarded": [],
            "pending_candidates": [{"name": "Found later", "description": "Candidate not yet reconciled", "source_ids": ["source.txt"]}],
            "review": {"complete": True, "issues": []}, "revision": 0,
        })
        self.assertEqual(result["status"], "revise")
        self.assertTrue(result["pending_candidates"])

    def test_markdown_includes_scale_traceability_and_discarded_section(self):
        content = render_markdown({"requirements": [], "discarded": [], "status": "needs_human_review", "issues": ["unresolved conflict"]}, Path("input"))
        self.assertIn("## Priority scale", content)
        self.assertIn("## Discarded candidates", content)
        self.assertIn("unresolved conflict", content)


if __name__ == "__main__":
    unittest.main()
