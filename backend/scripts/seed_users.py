"""Seed script to create test users with bcrypt-hashed passwords.

Run with the project's virtualenv active:

    python backend/scripts/seed_users.py

This uses `create_user` to insert users and will populate the new `password_hash` column.
"""
from models.user_model import create_user

def main():
    users = [
        ("Alice Manager", "alice@example.com", "password123"),
        ("Bob Manager", "bob@example.com", "password123"),
        ("Carol Manager", "carol@example.com", "password123"),
    ]

    for name, email, pw in users:
        res = create_user(name, email, pw)
        print("Created:", res.get("user"))

if __name__ == '__main__':
    main()
