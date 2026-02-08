"""Simple smoke test for auth endpoints.

Usage:
  python backend/scripts/smoke_auth_test.py

Set API_BASE env var to point at your running backend (default http://localhost:5000/api/v1)
"""
import os
import requests

API_BASE = os.getenv('API_BASE', 'http://localhost:5000/api/v1')


def pretty(resp):
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text


def main():
    signup_url = f"{API_BASE}/auth/signup"
    login_url = f"{API_BASE}/auth/login"

    test_user = {
        'name': 'Smoke Tester',
        'email': 'smoke+tester@example.com',
        'password': 'smoke1234'
    }

    print('Signing up:', signup_url)
    r = requests.post(signup_url, json=test_user)
    print('Signup ->', pretty(r))

    print('Logging in:', login_url)
    r2 = requests.post(login_url, json={'email': test_user['email'], 'password': test_user['password']})
    print('Login ->', pretty(r2))


if __name__ == '__main__':
    main()
