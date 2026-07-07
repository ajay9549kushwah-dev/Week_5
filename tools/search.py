import os
import re
import ast

WORKSPACE_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

MAX_GREP_RESULTS = 50

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build"
}


def resolve_path(path):

    full_path = os.path.abspath(
        os.path.join(
            WORKSPACE_ROOT,
            path
        )
    )

    if not full_path.startswith(WORKSPACE_ROOT):
        return None

    return full_path


def grep(
    pattern,
    path=".",
    case_sensitive=False,
    max_results=MAX_GREP_RESULTS
):

    root = resolve_path(path)

    if root is None:
        return {
            "error": "Invalid path"
        }

    flags = 0

    if not case_sensitive:
        flags = re.IGNORECASE

    matches = []
    total = 0

    for root_dir, dirs, files in os.walk(root):

        dirs[:] = [
            d for d in dirs
            if d not in EXCLUDE_DIRS
        ]

        for file in files:

            file_path = os.path.join(
                root_dir,
                file
            )

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    for line_no, line in enumerate(f, 1):

                        if re.search(
                            pattern,
                            line,
                            flags
                        ):

                            total += 1

                            if len(matches) < max_results:

                                matches.append(
                                    {
                                        "file": os.path.relpath(
                                            file_path,
                                            WORKSPACE_ROOT
                                        ),
                                        "line": line_no,
                                        "text": line.strip()
                                    }
                                )

            except Exception:
                continue

    return {
        "matches": matches,
        "total_matches": total,
        "truncated": total > max_results
    }
def list_definitions(path):

    file_path = resolve_path(path)

    if file_path is None:
        return {
            "error": "Invalid path"
        }

    if not os.path.exists(file_path):
        return {
            "error": "File not found"
        }

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            source = f.read()

        tree = ast.parse(source)

    except SyntaxError as e:
        return {
            "error": str(e)
        }

    definitions = []

    for node in tree.body:

        if isinstance(node, ast.FunctionDef):

            definitions.append({
                "kind": "function",
                "name": node.name,
                "line": node.lineno,
                "end_line": node.end_lineno
            })

        elif isinstance(node, ast.AsyncFunctionDef):

            definitions.append({
                "kind": "async function",
                "name": node.name,
                "line": node.lineno,
                "end_line": node.end_lineno
            })

        elif isinstance(node, ast.ClassDef):

            definitions.append({
                "kind": "class",
                "name": node.name,
                "line": node.lineno,
                "end_line": node.end_lineno
            })

            for child in node.body:

                if isinstance(
                    child,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):

                    definitions.append({
                        "kind": "method",
                        "name": child.name,
                        "line": child.lineno,
                        "end_line": child.end_lineno
                    })

    return {
        "definitions": definitions
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search text in files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string"
                    },
                    "path": {
                        "type": "string"
                    },
                    "case_sensitive": {
                        "type": "boolean"
                    },
                    "max_results": {
                        "type": "integer"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_definitions",
            "description": "List classes and functions in a Python file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    }
                },
                "required": ["path"]
            }
        }
    }
]


if __name__ == "__main__":

    print("Searching Flask repository...\n")

    result = grep(
        "def",
        path="target_repo/flask",
        max_results=10
    )

    print(result)

    if result["matches"]:

        first_file = result["matches"][0]["file"]

        print("\nFirst matched file:\n")

        print(first_file)

        print("\nDefinitions:\n")

        print(
            list_definitions(first_file)
        )