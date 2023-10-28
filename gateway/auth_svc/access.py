import os
import requests

AUTH_SVC_HOST = os.environ.get("AUTH_SVC_HOST") or "auth"
AUTH_SVC_PORT = os.environ.get("AUTH_SVC_PORT") or "5000"
AUTH_SVC_URL = f"http://{AUTH_SVC_HOST}:{AUTH_SVC_PORT}"


def login(request):
    auth = request.authorization
    if not auth:
        return None, ({"service": "Gateway", "message": "Missing Credentials"}, 401)

    basic_auth = (auth.username, auth.password)
    response = requests.post(f"{AUTH_SVC_URL}/login", auth=basic_auth)

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
