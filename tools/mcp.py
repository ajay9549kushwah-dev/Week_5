import json
import os


CONFIG = os.path.join(
    os.path.dirname(__file__),
    "..",
    "config.json"
)


def list_mcps():

    if not os.path.exists(CONFIG):
        return {"servers": []}

    with open(CONFIG, "r") as f:
        data = json.load(f)

    return {
        "servers": list(
            data.get(
                "mcpServers",
                {}
            ).keys()
        )
    }


def get_mcp(name):

    if not os.path.exists(CONFIG):
        return {"error": "config.json not found"}

    with open(CONFIG, "r") as f:
        data = json.load(f)

    server = data.get(
        "mcpServers",
        {}
    ).get(name)

    if server is None:
        return {"error": "Server not found"}

    return server