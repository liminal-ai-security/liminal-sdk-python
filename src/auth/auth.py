from msal.authority import AuthorityBuilder
from msal import PublicClientApplication, TokenCache


class _LoginService:
    def __init__(self) -> None:
        pass

    async def login(self):
        try:
            # TODO - fix this, from Nich's repo.
            # Use MSAL to get a token or the endpoint nick provided for checks?
            # https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/dev/sample/device_flow_sample.py
            # https://learn.microsoft.com/en-us/javascript/api/overview/msal-overview?view=msal-js-latest
            #
            client_id = ""
            tenant_id = ""
            authority = AuthorityBuilder(
                "https://login.microsoftonline.com/", tenant_id
            )
            self._app = PublicClientApplication(
                client_id,
                authority=authority,  # f"https://login.microsoftonline.com/{tenant_id}/v2.0",
            )
            result = await self._app.acquire_token_by_device_flow(scopes=["User.Read"])
            # TODO - do some stuff here to validate the token we get back
            return result
        except:
            # TODO - temporary fix, get bearer token from webapp
            return "YOUR-BEARER-TOKEN-HERE"
