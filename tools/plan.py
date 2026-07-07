import json
import os

TODO_FILE = ".agent/todos.json"


def load_todos():

    if not os.path.exists(TODO_FILE):
        return []

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):

    os.makedirs(".agent", exist_ok=True)

    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=4)


def add_todos(title, description, verification):

    todos = load_todos()

    todo = {
        "id": len(todos) + 1,
        "title": title,
        "description": description,
        "verification": verification,
        "status": "pending"
    }

    todos.append(todo)

    save_todos(todos)

    return todo


def get_todos():

    return load_todos()


def mark_todo(todo_id, status, evidence=""):

    todos = load_todos()

    for todo in todos:

        if todo["id"] == todo_id:

            if status == "completed" and evidence == "":
                return {
                    "error": "Evidence required before marking completed."
                }

            todo["status"] = status

            if evidence:
                todo["evidence"] = evidence

            save_todos(todos)

            return todo

    return {
        "error": "Todo not found."
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_todos",
            "description": "Add a new todo item.",
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
            "description": "Return all todos.",
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
            "description": "Update todo status.",
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


if __name__ == "__main__":

    print(add_todos(
        "Build Search Tool",
        "Complete grep implementation",
        "Run search.py successfully"
    ))

    print()

    print(get_todos())

    print()

    print(mark_todo(
        1,
        "in_progress"
    ))

    print()

    print(mark_todo(
        1,
        "completed",
        "search.py executed successfully"
    ))

    print()

    print(get_todos())