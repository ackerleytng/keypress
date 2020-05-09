import os
import requests

DEV_MODE = bool(os.getenv("DEV_MODE"))
KEYPRESS_CLIENT_ID = os.getenv("KEYPRESS_CLIENT_ID")
KEYPRESS_CLIENT_SECRET = os.getenv("KEYPRESS_CLIENT_SECRET")
# Example: https://keycloak.localhost
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")
# Example: exp-extension
KEYCLOAK_EXTENSION_SCOPE = os.getenv("KEYCLOAK_EXTENSION_SCOPE")
# TODO configure this dynamically from .well-known
KEYCLOAK_TOKEN_EXCHANGE_PATH = KEYCLOAK_BASE_URL + "/auth/realms/applications/protocol/openid-connect/token"

TOKEN_EXCHANGE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"


def exchange_for_app_token(keypress_token, audience, scope=None):
    if scope is None:
        scope = audience

    scope += " " + KEYCLOAK_EXTENSION_SCOPE

    data = dict(
        client_id=KEYPRESS_CLIENT_ID,
        client_secret=KEYPRESS_CLIENT_SECRET,
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        scope=scope,
        subject_token=keypress_token,
        audience=audience,
    )

    r = requests.post(
        KEYCLOAK_TOKEN_EXCHANGE_PATH,
        data=data,
        verify=(not DEV_MODE)
    )
    ret = r.json()

    if r.status_code != requests.codes.ok:
        # TODO maybe use a more specific exception?
        if "error_description" in ret:
            raise Exception(ret["error_description"])

        if "error" in ret:
            raise Exception(ret["error"])

        raise Exception("Unknown error encountered while communicating with keycloak")

    if "access_token" in ret:
        return ret["access_token"]

    raise Exception("Could not obtain access_token")


if __name__ == "__main__":
    import sys
    print(exchange_for_app_token(sys.argv[1], sys.argv[2]))
