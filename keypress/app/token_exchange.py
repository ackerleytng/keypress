import os
import requests

KEYPRESS_CLIENT_ID = os.getenv("KEYPRESS_CLIENT_ID")
KEYPRESS_CLIENT_SECRET = os.getenv("KEYPRESS_CLIENT_SECRET")
# Example: https://keycloak.localhost
KEYCLOAK_BASE_URL = os.getenv("KEYPRESS_BASE_URL")
# TODO configure this dynamically from .well-known
KEYCLOAK_TOKEN_EXCHANGE_PATH = KEYPRESS_BASE_URL + "/auth/realms/applications/protocol/openid-connect/token"

TOKEN_EXCHANGE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"


def exchange_for_app_token(keypress_token, audience):
    params = dict(
        client_id=KEYPRESS_CLIENT_ID,
        client_secret=KEYPRESS_CLIENT_SECRET,
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token=keypress_token,
        audience=audience,
    )

    r = requests.get(KEYCLOAK_TOKEN_EXCHANGE_PATH, params=params)
    ret = r.json()

    if r.status_code != requests.codes.ok:
        # TODO maybe use a more specific exception?
        if "error_description" in ret:
            raise Exception(ret["error_description"])

        raise Exception("Unknown error encountered while communicating with keycloak")

    if "access_token" in ret:
        return ret["access_token"]

    raise Exception("Could not obtain access_token")
