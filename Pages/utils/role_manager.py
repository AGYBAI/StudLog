import json
import os

def get_user_role():
    try:
        session_path = "session.json"
        if not os.path.exists(session_path):
            print(f"Session file not found at {os.path.abspath(session_path)}")
            return "student"
            
        with open(session_path, "r") as file:
            session = json.load(file)
            role = session.get("role", "student")
            print(f"Current user role from session: {role}")
            return role
    except Exception as e:
        print(f"Error reading user role: {str(e)}")
        return "student"

def is_admin():
    role = get_user_role()
    is_admin_user = role == "admin"
    print(f"is_admin check: {is_admin_user} (role={role})")
    return is_admin_user
