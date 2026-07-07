import os
import sys
import json

from dotenv import load_dotenv
from openai import OpenAI

from build1_sessions import (
    create_session,
    save_session,
    load_session,
)

# File tools
from tools.files import (
    read_file,
    write_file,
    edit_file,
    list_files,
)

# Web tools
from tools.web import (
    web_search,
    web_fetch,
)

# Paper tools
from tools.papers import (
    paper_search,
    read_paper,
)

# Week 4 tools
from tools.exec import run_command
from tools.search import (
    grep,
    list_definitions,
)
from tools.plan import (
    add_todos,
    get_todos,
    mark_todo,
)

from tools.skills import (
    list_skills,
    load_skill,
)

from tools.mcp import (
    list_mcps,
    get_mcp,
)

load_dotenv()

WORKSPACE_ROOT = os.path.abspath(
    os.environ.get(
        "WORKSPACE_ROOT",
        "."
    )
)

MAX_ITERATIONS = 10

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

MODEL = "nex-agi/nex-n2-pro:free"


TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Read webpage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string"
                    }
                },
                "required": ["url"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "paper_search",
            "description": "Search research papers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_paper",
            "description": "Read paper.",
            "parameters": {
                "type": "object",
                "properties": {
                    "arxiv_id": {
                        "type": "string"
                    }
                },
                "required": ["arxiv_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run terminal command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string"
                    }
                },
                "required": ["command"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search text in project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string"
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
            "description": "List functions and classes.",
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
    },

    {
        "type": "function",
        "function": {
            "name": "add_todos",
            "description": "Add todo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "verification": {
                        "type": "string"
                    }
                },
                "required": [
                    "title",
                    "description",
                    "verification"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_todos",
            "description": "Show todos.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "mark_todo",
            "description": "Update todo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer"
                    },
                    "status": {
                        "type": "string"
                    },
                    "evidence": {
                        "type": "string"
                    }
                },
                "required": [
                    "todo_id",
                    "status"
                ]
            }
        }
    }

]
class Agent:
    """Main agent class"""

    def __init__(self, workspace=".", session_id=None):

        self.workspace = os.path.abspath(workspace)

        if session_id:

            self.session_id = session_id

            try:

                session = load_session(session_id)

                self.messages = session["messages"]

            except Exception:

                self.messages = [
                    {
                        "role": "system",
                        "content": build_system_prompt()
                    }
                ]

        else:

            self.session_id = create_session()

            self.messages = [
                {
                    "role": "system",
                    "content": build_system_prompt()
                }
            ]


    def chat(self, user_message):

        self.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        answer = self._run_loop()

        save_session(
            self.session_id,
            self.messages,
            title="Research Session"
        )

        return answer


    def run_once(self, prompt):

        return self.chat(prompt)


    def _run_loop(self):

        for _ in range(MAX_ITERATIONS):

            response = client.chat.completions.create(

                model=MODEL,

                messages=self.messages,

                tools=TOOLS

            )

            message = response.choices[0].message

            finish_reason = response.choices[0].finish_reason


            if finish_reason == "tool_calls":

                self.messages.append(message)

                for tool_call in message.tool_calls:

                    result = self.dispatch(

                        {
                            "name": tool_call.function.name,

                            "arguments": json.loads(
                                tool_call.function.arguments
                            )
                        }

                    )

                    self.messages.append(

                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        }

                    )

                continue


            if finish_reason == "stop":

                answer = message.content

                self.messages.append(

                    {
                        "role": "assistant",
                        "content": answer
                    }

                )

                return answer

        return "Max iterations reached."


    def dispatch(self, tool_call):

        name = tool_call["name"]
        args = tool_call["arguments"]

        try:

            if name == "web_search":
                return json.dumps(
                    web_search(args["query"])
                )

            elif name == "web_fetch":
                return json.dumps(
                    web_fetch(args["url"])
                )

            elif name == "paper_search":
                return json.dumps(
                    paper_search(args["query"])
                )

            elif name == "read_paper":
                return json.dumps(
                    read_paper(args["arxiv_id"])
                )

            elif name == "read_file":
                return json.dumps(
                    read_file(**args)
                )

            elif name == "write_file":
                return json.dumps(
                    write_file(**args)
                )

            elif name == "edit_file":
                return json.dumps(
                    edit_file(**args)
                )

            elif name == "list_files":
                return json.dumps(
                    list_files(**args)
                )

            elif name == "run_command":
                return json.dumps(
                    run_command(**args)
                )

            elif name == "grep":
                return json.dumps(
                    grep(**args)
                )

            elif name == "list_definitions":
                return json.dumps(
                    list_definitions(**args)
                )

            elif name == "add_todos":
                return json.dumps(
                    add_todos(**args)
                )

            elif name == "get_todos":
                return json.dumps(
                    get_todos()
                )

            elif name == "mark_todo":
                return json.dumps(
                    mark_todo(**args)
                )

            elif name == "list_skills":
                return json.dumps(list_skills())

            elif name == "load_skill":
                return json.dumps(load_skill(args["name"]))

            elif name == "list_mcps":
                return json.dumps(list_mcps())

            elif name == "get_mcp":
                return json.dumps(get_mcp(args["name"]))

            else:

                return json.dumps(
                    {
                        "error": f"Unknown tool: {name}"
                    }
                )

        except Exception as e:

            return json.dumps(
                {
                    "error": str(e)
                }
            )


    def _emit(self, event, **data):
        pass

class REPLAgent(Agent):
    """Simple terminal interface"""

    def run(self):

        print(f"\nResearch Desk [{self.session_id}]")
        print("Type /quit to exit\n")

        while True:

            try:
                user = input("> ").strip()

            except (KeyboardInterrupt, EOFError):
                print()
                break

            if not user:
                continue

            if user in ("/quit", "/exit"):
                break

            if user == "/skills":
                print(list_skills())
                continue

            if user == "/mcp":
                print(list_mcps())
                continue

            print()
            print(self.chat(user))
            print()

    def _emit(self, event, **data):

        if event == "tool_call":

            print(
                f"[TOOL] {data.get('name')}",
                file=sys.stderr
            )


def build_system_prompt():

    prompt = (
        "You are Research Desk. "
        "Use tools whenever they help answer the user."
    )

    for path in (
        "AGENTS.md",
        ".agent/AGENTS.md",
    ):

        if os.path.exists(path):

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                prompt += "\n\n"
                prompt += f.read()

            break

    return prompt


def main():

    if "--tui" in sys.argv:

        from tui import ResearchDeskApp

        ResearchDeskApp().run()

        return

    session_id = None

    if "--session" in sys.argv:

        idx = sys.argv.index("--session")

        if idx + 1 < len(sys.argv):

            session_id = sys.argv[idx + 1]

            del sys.argv[idx:idx + 2]

    agent = REPLAgent(
        session_id=session_id
    )

    if len(sys.argv) > 1:

        print(
            agent.run_once(
                " ".join(sys.argv[1:])
            )
        )

        return

    agent.run()


if __name__ == "__main__":
    main()