# Liminal Python SDK

[![CI][ci-badge]][ci]
[![PyPI][pypi-badge]][pypi]
[![Version][version-badge]][version]
[![License][license-badge]][license]

The Liminal SDK for Python provides a clean, straightforward, `asyncio`-based interface
for interacting with the Liminal API.

- [Installation](#installation)
- [Python Versions](#python-versions)
- [Usage](#usage)
- [Contributing](#contributing)

# Installation

TBD

# Python Versions

`liminal` is currently supported on:

- Python 3.11
- Python 3.12

# Quickstart

Presuming the use of Microsoft Entra ID as your auth provider, instantiating a Liminal
API object is easy:

```python
import asyncio

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.DEBUG)

    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = MicrosoftAuthProvider("<TENANT_ID>", "<CLIENT_ID>")

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, "<API_SERVER_URL>")


asyncio.run(main())
```

You can see several examples of how to use this API object via the [`examples`][examples]
folder in this repo.

# Authentication

Liminal supports the concept of authenticating via various auth providers. Currently,
the following auth providers are supported:

- Microsoft Entra ID

## Microsoft Entra ID

Liminal authenticates with Microsoft Entra ID via an
[OAuth 2.0 Device Authorization Grant][oauth-device-auth-grant]. This flow requires you
to start your app, retrieve a device code from the logs produced by this SDK, and
provide that code to Microsoft via a web browser. Once you complete the login process,
the SDK will be authenticated for use with your Liminal instance.

### Finding your Entra ID Tenant and Client IDs

- Log into your [Azure portal][azure-portal].
- Navigate to `Microsoft Entra ID`.
- Click on `App registrations`.
- Either create a new app registration or select an existing one.
- In the `Overview` of the registration, look for the `Application (client) ID` and
  `Directory (tenant) ID` values.

# Contributing

Thanks to all of [our contributors][contributors] so far!

1. [Check for open features/bugs][issues] or [initiate a discussion on one][new-issue].
2. [Fork the repository][fork].
3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`
4. (_optional, but highly recommended_) Enter the virtual environment: `source ./.venv/bin/activate`
5. Install the dev environment: `script/setup`
6. Code your new feature or bug fix on a new branch.
7. Write tests that cover your new functionality.
8. Run tests and ensure 100% code coverage: `poetry run pytest --cov aionotion tests`
9. Update `README.md` with any new documentation.
10. Submit a pull request!

[azure-portal]: https://portal.azure.com
[ci-badge]: https://github.com/liminal-ai-security/liminal-sdk-python/workflows/CI/badge.svg
[ci]: https://github.com/liminal-ai-security/liminal-sdk-python/actions
[contributors]: https://github.com/liminal-ai-security/liminal-sdk-python/graphs/contributors
[fork]: https://github.com/liminal-ai-security/liminal-sdk-python/fork
[issues]: https://github.com/liminal-ai-security/liminal-sdk-python/issues
[license-badge]: https://img.shields.io/pypi/l/aionotion.svg
[license]: https://github.com/liminal-ai-security/liminal-sdk-python/blob/main/LICENSE
[new-issue]: https://github.com/liminal-ai-security/liminal-sdk-python/issues/new
[notion]: https://getnotion.com
[oauth-device-auth-grant]: https://oauth.net/2/grant-types/device-code/
[pypi-badge]: https://img.shields.io/pypi/v/aionotion.svg
[pypi]: https://pypi.python.org/pypi/aionotion
[version-badge]: https://img.shields.io/pypi/pyversions/aionotion.svg
[version]: https://pypi.python.org/pypi/aionotion
