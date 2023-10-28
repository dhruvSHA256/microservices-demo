import requests
from config import AUTH_SVC_URL, SERVICE_NAME
import sys


def login(request):
    auth = request.authorization
    if not auth:
        return None, ({"service": SERVICE_NAME, "message": "Missing Credentials"}, 401)

    basic_auth = (auth.username, auth.password)
    response = requests.post(f"{AUTH_SVC_URL}/login", auth=basic_auth)

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)


def validate(request):
    resp = request.headers.get("Authorization", None)
    print(resp, file=sys.stderr)
    if not resp:
        return None, ({"service": SERVICE_NAME, "message": "Missing Credentials"}, 401)
    response = requests.post(
        f"{AUTH_SVC_URL}/validate",
        headers={"Authorization": resp},
    )
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
