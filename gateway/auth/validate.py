import os
import requests


def token(request):
    jwt = request.headers.get("Authorization", None)
    if not token:
        return None, ({"service": "Gateway", "message": "Missing Credentials"}), 401
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": jwt},
    )
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
