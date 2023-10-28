import os
import requests

AUTH_SVC_HOST = os.environ.get("AUTH_SVC_HOST") or "auth"
AUTH_SVC_PORT = os.environ.get("AUTH_SVC_PORT") or "5000"
AUTH_SVC_URL = f"http://{AUTH_SVC_HOST}:{AUTH_SVC_PORT}"


def token(request):
    jwt_token = request.headers.get("Authorization", None)
    if not token:
        return None, ({"service": "Gateway", "message": "Missing Credentials"}, 401)
    response = requests.post(
        f"{AUTH_SVC_URL}/validate",
        headers={"Authorization": jwt_token},
    )
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
