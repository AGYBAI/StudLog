import json

def get_user_role():
    try:
        with open("session.json", "r") as file:
            session = json.load(file)
            return session.get("role", "student")
    except:
        return "student"

def is_admin():
    return get_user_role() == "admin"
