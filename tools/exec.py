

import os
import shlex
import subprocess

WORKSPACE_ROOT = os.path.abspath(os.environ.get("WORKSPACE_ROOT", "."))
TIMEOUT_DEFAULT = 10
MAX_OUTPUT_CHARS = 8_000

READ_ONLY_PREFIXES = (
    "dir",
    "grep", "find", "ls", "cat", "head", "tail", "wc",
    "git log", "git diff", "git status", "git blame", "git show",
    "pytest", "python -m pytest", "ruff", "flake8", "mypy",
)

# Known-destructive: always ask, even if they'd otherwise look harmless.
DESTRUCTIVE_PATTERNS = (
    "rm ", "mv ", ">", ">>", "git commit", "git push", "git checkout --",
    "pip install", "npm install", "curl ", "sudo ", "chmod ",
)


def paths_within_sandbox(command: str, workspace_root: str) -> bool:

    tokens = shlex.split(command)

    for token in tokens:

        if (
            "/" in token
            or "\\" in token
            or token.startswith(".")
        ):

            path = os.path.abspath(
                os.path.join(workspace_root, token)
            )

            if not path.startswith(
                workspace_root
            ):
                return False

    return True


def classify_command(command: str) -> str:

    command = command.strip()

    for pattern in DESTRUCTIVE_PATTERNS:

        if pattern in command:
            return "ask"

    for prefix in READ_ONLY_PREFIXES:

        if command.startswith(prefix):
            return "read_only"

    return "ask"


def run_command(
    command: str,
    cwd: str = WORKSPACE_ROOT,
    timeout: int = TIMEOUT_DEFAULT
) -> dict:

    if not paths_within_sandbox(
        command,
        cwd
    ):
        return {
            "error": "Command escapes workspace."
        }

    mode = classify_command(command)

    if mode == "ask":

        print("\nWARNING!")
        print(command)

        ans = input(
            "Run this command? (y/n): "
        ).strip().lower()

        if ans != "y":
            return {
                "error": "Command cancelled."
            }

    try:

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True,
        )

        stdout = result.stdout[:MAX_OUTPUT_CHARS]
        stderr = result.stderr[:MAX_OUTPUT_CHARS]

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": result.returncode,
        }

    except subprocess.TimeoutExpired:

        return {
            "error": "Command timed out."
        }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a shell command in the workspace and return its output. "
                "Use this to search (grep/find), inspect history (git log/diff), "
                "run tests, or make a change. Read-only commands run immediately. "
                "Anything that writes, deletes, or installs will pause and ask the "
                "human operator for approval — expect that pause, it's not a failure."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": f"Seconds before the command is killed. Default {TIMEOUT_DEFAULT}.",
                    },
                },
                "required": ["command"],
            },
        },
    }
]


if __name__ == "__main__":

    print("Read-only command:")
    print(run_command("dir"))

    print("\nDestructive command:")
    print(run_command("del test.txt"))