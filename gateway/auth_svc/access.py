import requests
from config import AUTH_SVC_URL


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
