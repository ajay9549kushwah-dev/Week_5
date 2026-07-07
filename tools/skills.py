import os

SKILLS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "skills"
)


def list_skills():

    skills = []

    if not os.path.exists(SKILLS_DIR):
        return {"skills": []}

    for folder in os.listdir(SKILLS_DIR):

        skill = os.path.join(
            SKILLS_DIR,
            folder,
            "SKILL.md"
        )

        if os.path.isfile(skill):
            skills.append(folder)

    return {"skills": skills}


def load_skill(name):

    skill = os.path.join(
        SKILLS_DIR,
        name,
        "SKILL.md"
    )

    if not os.path.exists(skill):
        return {"error": "Skill not found"}

    with open(skill, "r", encoding="utf-8") as f:
        return {"content": f.read()}