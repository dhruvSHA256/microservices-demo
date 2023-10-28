import requests
from config import AUTH_SVC_URL


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
