"""Solve the missing methods using the Task 3/4 RAG index and an allowed LLM.

Run from any directory: python solve_tasks.py
Uses OPENAI_API_KEY from the environment or a local .env file; without a key,
falls back to the configured OpenCode CLI.
"""

import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
from urllib.request import Request, urlopen


ASSIGNMENTS = Path(__file__).resolve().parent.parent
REPOSITORY = ASSIGNMENTS / "Task_1" / "AI4SE_Playground"
MANIFEST = ASSIGNMENTS / "missing_code.json"
ALLOWED_MODELS = {
    "gpt-6-luna", "gpt-5.6-luna", "gpt-5.4-nano", "gpt-5-nano",
    "gpt-5-mini", "gpt-4.1-nano", "gpt-4o-mini",
}


def api_key():
    """Use the environment first, then the untracked .env beside this script."""
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() == "OPENAI_API_KEY":
                return value.strip().strip('"\'')
    return None


def generate_code(prompt, model, key):
    """Return model text from the OpenAI Responses API or OpenCode CLI."""
    if key:
        request = Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps({"model": model, "input": prompt}).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=120) as response:
            result = json.load(response)
        if result.get("status") != "completed":
            raise ValueError(f"model response not completed: {result.get('status')}")
        return "".join(
            part["text"] for item in result["output"] if item["type"] == "message"
            for part in item["content"] if part["type"] == "output_text"
        )
    result = subprocess.run(
        ["opencode", "run", "--model", f"openai/{model}", prompt],
        cwd=Path(__file__).resolve().parent, capture_output=True, text=True,
        check=True,
    )
    return result.stdout

sys.path.insert(0, str(ASSIGNMENTS / "Task_3"))
sys.path.insert(0, str(ASSIGNMENTS / "Task_4"))
from embed_chunks import embed_chunk  # noqa: E402
from match_embeddings import match_embeddings  # noqa: E402


def find_method(source, class_name, method_name):
    """Find exactly one direct method of the requested class."""
    tree = ast.parse(source)
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == class_name]
    if len(classes) != 1:
        raise ValueError(f"expected one class {class_name}")
    methods = [node for node in classes[0].body
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
               and node.name == method_name]
    if len(methods) != 1:
        raise ValueError(f"expected one method {class_name}.{method_name}")
    return methods[0]


def solve_task(task, model="gpt-6-luna", key=None):
    """Retrieve five chunks, ask the LLM for a method, and replace its stub."""
    if model not in ALLOWED_MODELS:
        raise ValueError(f"model must be one of {sorted(ALLOWED_MODELS)}")
    path = (REPOSITORY / task["file"]).resolve()
    if not path.is_relative_to(REPOSITORY.resolve()) or not path.is_file():
        raise ValueError(f"invalid target file: {task['file']}")
    source = path.read_text(encoding="utf-8")
    method = find_method(source, task["class"], task["method"])
    lines = source.splitlines(keepends=True)
    original = "".join(lines[method.lineno - 1:method.end_lineno])
    description = (f"File: {task['file']}\nClass: {task['class']}\n"
                   f"Method: {task['method']}\nRequirement: {task['docstring']}")
    matches = match_embeddings(embed_chunk(description), limit=5)
    if len(matches) != 5:
        raise ValueError("expected five indexed chunks; rebuild the Task 3 index")
    context = "\n\n".join(
        f"[{item['path']}:{item['start_line']}-{item['end_line']}]\n{item['text']}"
        for item in matches
    )
    prompt = (
        "Implement ONLY the indicated Python instance method. Return ONLY its complete "
        "def block, without decorators, markdown, explanations, imports, or changes to "
        "other code. Keep the exact existing signature. Use the surrounding code to "
        "respect the repository's behavior.\n\n"
        f"Task:\n{description}\n\nExisting method:\n{original}\n"
        f"Target source file:\n{source}\n\nTop 5 retrieved chunks:\n{context}"
    )
    code = generate_code(prompt, model, key).strip()
    if code.startswith("```python") and code.endswith("```"):
        code = code[len("```python"):-3].strip()
    elif code.startswith("```") and code.endswith("```"):
        code = code[3:-3].strip()
    code = textwrap.dedent(code).strip()
    parsed = ast.parse(code)
    if (len(parsed.body) != 1 or not isinstance(parsed.body[0], type(method))
            or parsed.body[0].name != method.name
            or ast.dump(parsed.body[0].args) != ast.dump(method.args)
            or parsed.body[0].decorator_list):
        raise ValueError(f"LLM returned something other than {task['class']}.{method.name}")
    body = code.splitlines(keepends=True)
    extra = min(len(line) - len(line.lstrip()) for line in body[1:] if line.strip()) - 4
    if extra > 0:
        body[1:] = [line[extra:] if line.strip() else line for line in body[1:]]
        code = "".join(body)
    replacement = textwrap.indent(code, " " * method.col_offset) + "\n"
    updated = "".join(lines[:method.lineno - 1]) + replacement + "".join(lines[method.end_lineno:])
    ast.parse(updated)
    path.write_text(updated, encoding="utf-8")
    print(f"Implemented {task['class']}.{task['method']} in {task['file']}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(ALLOWED_MODELS))
    args = parser.parse_args()
    key = api_key()
    model = args.model or ("gpt-5-mini" if key else "gpt-6-luna")
    for task in json.loads(MANIFEST.read_text(encoding="utf-8")):
        solve_task(task, model, key)


if __name__ == "__main__":
    main()
