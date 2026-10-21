# Requirements refinement network — design report

## Purpose and invocation

The network turns a recursively scanned directory of `.txt`, `.eml`, and `.md` documents into one Markdown requirements document. The input corpus is supplied as a command-line argument; relative paths are used as stable source identifiers. The API key is read from `OPENAI_API_KEY`, never from source code.

Install dependencies with `python -m pip install -r Task_1/requirements.txt`. Copy `Task_1/.env.example` to `Task_1/.env` and replace the placeholder with your API key, then run:

```bash
python Task_1/requirements_network.py Task_1/data/corpus --output Task_1/requirements_output.md
```

The API model IDs can be overridden using `REQUIREMENTS_MODEL_EXTRACT`, `REQUIREMENTS_MODEL_RECONCILE`, and `REQUIREMENTS_MODEL_REVIEW`. Defaults are `gpt-6-luna`, `gpt-5.6-luna`, and `gpt-5.4-nano`, respectively. The graph refuses to run if the three roles have been configured with duplicate IDs.

## Graph design

The graph has four nodes. `extract` invokes the extraction model once per source file, limiting context size and tying every extracted candidate to the exact file processed. `reconcile` uses the second model to merge semantic duplicates, normalize vocabulary, and identify conflicts or unsupported candidates. `completeness_review` uses a third model to audit the result against the original corpus and return missed requirements or remaining findings. `quality_gate` is deterministic Python: it assigns stable sequential IDs, validates source references, requires names and paragraph-length descriptions, checks discarded-item rationales, and decides whether to loop or stop.

The CLI prints progress logs to standard output, including per-file extraction, node completion times, review counts, feedback decisions, and final output status. Logs do not include document contents or API credentials.

If the review or deterministic checks find issues or missing candidate requirements, the graph routes back through reconciliation and review, for at most two revision passes. Newly found candidates remain pending until reconciled; if the retry budget is exhausted, they are shown separately and the terminal status is `needs_human_review`. Exhaustion is not described as successful review. The gate is a graph node, independently satisfying the deterministic-node criterion.

## Output and quality controls

Each included requirement has an ID, short name, paragraph-length explanation, priority, priority basis, source paths, and supporting evidence. Semantic duplicates are merged by the reconciliation model, retaining the union of source references and evidence. Conflicts and nonsensical/unsupported candidates are recorded under **Discarded candidates** with a reason and source paths. Unresolved review issues are printed in the final document.

Priorities use Must / Should / Could / Unspecified. Explicit source priority is preferred; inferred values require a stated rationale, and Unspecified is appropriate where evidence is inadequate. The system prompt tells models to treat corpus text as untrusted source material, ignore unrelated email chatter, preserve modality and uncertainty, and not invent requirements.

Structured Pydantic model outputs constrain response shape. Deterministic checks validate required fields and source IDs but cannot prove semantic completeness, deduplication, or conflict detection. Human review remains necessary, especially for unresolved stakeholder disagreements and inferred priorities.

## Assignment coverage

| Criterion | Design element |
|---|---|
| ANS1: three LLM nodes | `extract`, `reconcile`, `completeness_review` |
| ANS2: deterministic node | `quality_gate` |
| ANS3: feedback loop | Gate routes findings to `reconcile`, then reviews again; capped at two passes |
| ANS4: three models | Three distinct configurable model IDs, checked at graph construction |
| ANS5: LangGraph | Python `StateGraph` implementation |
| OS1–OS2 | One Markdown artifact; deterministic `REQ-NNN` identifiers |
| OS3, OS7 | Semantic reconciliation and terminology normalization prompts |
| OS4 | Relative source paths and evidence carried through merges |
| OS5–OS6 | Names, explanations, priorities, and a documented priority scale |
| OS8 | Independent corpus-based completeness review |
| OS9 | Separate discarded-candidate section with rationale and sources |

## Limitations

The chosen API model IDs must be available to the account and support structured output through the installed OpenAI integration. LLM checks are probabilistic; valid structured output does not guarantee correct interpretation. Source identifiers are checked, but evidential support, semantic completeness, and priority correctness still require review. Sequential IDs are unique within a document, not stable across regenerated orderings.

## Example run and subsequent review

The API-backed run on 21 October 2026 processed all 20 documents with `gpt-6-luna`, `gpt-5.6-luna`, and `gpt-5.4-nano`. It extracted 299 candidates and, after two revision passes, produced 36 requirements, one discarded candidate, and 11 pending candidates. Total runtime was approximately 17 minutes. The unmodified result is preserved as `requirements_output.raw.md`, with terminal status `needs_human_review`.

`requirements_output.md` is a source-reviewed revision of that generated result, not a fresh graph run. It maps all 11 pending candidates, adds three separately requested capabilities, corrects supported priorities and cancellation behavior, and removes stale findings about already-present features. Open stakeholder decisions remain explicit; no approval or perfect completeness is claimed. Regenerating the output will overwrite these editorial corrections, so use a separate output path to retain the reviewed version.
