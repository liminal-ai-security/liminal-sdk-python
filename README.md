# Liminal Python SDK

[![CI][ci-badge]][ci]
[![PyPI][pypi-badge]][pypi]
[![Version][version-badge]][version]
[![License][license-badge]][license]

The Liminal SDK for Python provides a clean, straightforward, `asyncio`-based interface
for interacting with the Liminal API.

- [Installation](#installation)
- [Python Versions](#python-versions)
- [Quickstart](#quickstart)
- [Authentication](#authentication)
  - [Via Auth Provider](#via-auth-provider)
    - [Microsoft Entra ID](#microsoft-entra-id)
  - [Via Session ID](#via-session-id)
  - [Via Liminal-Provided Environment Token](#via-liminal-provided-environment-token)
- [Endpoints](#endpoints)
  - [Getting Model Instances](#getting-model-instances)
  - [Managing Threads](#managing-threads)
  - [Submitting Prompts](#submitting-prompts)
- [Connection Pooling](#connection-pooling)
- [Running Examples](#running-examples)
- [Contributing](#contributing)

# Installation

```sh
pip install liminal-sdk-python
```

# Python Versions

`liminal` is currently supported on:

- Python 3.11
- Python 3.12
- Python 3.13

# Quickstart

You can see several examples of how to use this API object via the [`examples`][examples]
folder in this repo.

# Authentication

## Via Auth Provider

Liminal supports the concept of authenticating via various auth providers. Currently,
the following auth providers are supported:

- Microsoft Entra ID

### Microsoft Entra ID

#### Device Code Flow

This authentication process with Microsoft Entra ID involves an
[OAuth 2.0 Device Authorization Grant][oauth-device-auth-grant]. This flow requires you
to start your app, retrieve a device code from the logs produced by this SDK, and
provide that code to Microsoft via a web browser. Once you complete the login process,
the SDK will be authenticated for use with your Liminal instance.

To authenticate with this flow, you will need an Entra ID client and tenant ID:

- Log into your [Azure portal][azure-portal].
- Navigate to `Microsoft Entra ID`.
- Click on `App registrations`.
- Either create a new app registration or select an existing one.
- In the `Overview` of the registration, look for the `Application (client) ID` and
  `Directory (tenant) ID` values.

With a client ID and tenant ID, you can create a Liminal client object and authenticate
it:

```python
import asyncio

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider


async def main() -> None:
    """Run!"""
    # Create an auth provider to authenticate the user:
    auth_provider = DeviceCodeFlowProvider("<TENANT_ID>", "<CLIENT_ID>")

    # Create the liminal SDK instance and authenticate it:
    liminal = await Client.authenticate_from_auth_provider()(
        "https://api.my-tenant.liminal.ai", auth_provider
    )


asyncio.run(main())
```

In your application logs, you will see a message that looks like this:

```
INFO:liminal:To sign in, use a web browser to open the page
https://microsoft.com/devicelogin and enter the code XXXXXXXXX to authenticate.
```

Leaving your application running, open a browser at that URL and input the code as
instructed. Once you successfully complete authentication via Entra ID, your Liminal
client object will automatically authenticate with your Liminal API server.

## Via Session ID

After the initial authentication with your auth provider, the Liminal client object will
internally manage sessions to ensure the ongoing ability to communicate with your
Liminal API server. The client object will automatically handle using the stored refresh
token to request new access tokens as appropriate.

The Liminal client object will have a `session_id` property that contains the session
info. **Maintain careful control of this session ID, as it can be used to repeat
authentication with your Liminal API server.**

Assuming you have a session ID, it is simple to create a new Liminal client using that
ID:

```python
import asyncio

from liminal import Client


async def main() -> None:
    """Run!"""
    # Create the client:
    liminal = await Client.authenticate_from_session_id(
        "https://api.my-tenant.liminal.ai", "my-session-id"
    )


asyncio.run(main())
```

## Via Liminal-Provided Environment Token

Presuming you have received one from Liminal, you may also used an environment token to
create an authenticated client object:

```python
import asyncio

from liminal import Client


async def main() -> None:
    """Run!"""
    # Create the client:
    liminal = await Client.authenticate_from_token(
        "https://api.my-tenant.liminal.ai", "my-token"
    )


asyncio.run(main())
```

# Endpoints

## Getting Model Instances

Every LLM instance connected in the Liminal admin dashboard is referred to as a "model
instance." The SDK provides several methods to interact with model instances:

```python
# Get all available model instances:
model_instances = await liminal.llm.get_available_model_instances()
# >>> [ModelInstance(...), ModelInstance(...)]

# Get a specific model instance (if it exists):
model_instance = await liminal.llm.get_model_instance("My Model")
# >>> ModelInstance(...)
```

## Managing Threads

Threads are conversations with an LLM instance:

```python
# Get all available threads:
threads = await liminal.thread.get_available()
# >>> [Thread(...), Thread(...)]

# Get a specific thread by ID:
thread = await liminal.thread.get_by_id(123)
# >>> Thread(...)

# Some operations require a model instance:
model_instance = await liminal.llm.get_model_instance("My Model")

# Create a new thread:
thread = await liminal.thread.create(model_instance.id, "New Thread")
# >>> Thread(...)
```

## Submitting Prompts

```python
# Prompt operations require a model instance:
model_instance = await liminal.llm.get_model_instance(model_instance_name)

# Prompt operations optionally take an existing thread:
thread = await liminal.thread.get_by_id(123)
# >>> Thread(...)

# Analayze a prompt for sensitive info:
findings = await liminal.prompt.analyze(model_instance.id, "Here is a sensitive prompt")
# >>> AnalyzeResponse(...)

# Cleanse input text by applying the policies defined in the Liminal admin
# dashboard. You can optionally provide existing analysis finidings; if not
# provided, analyze is # called automatically):
cleansed = await liminal.prompt.cleanse(
    model_instance.id,
    "Here is a sensitive prompt",
    findings=findings,
    thread_id=thread.id,
)
# >>> CleanseResponse(...)

# Submit a prompt to an LLM, cleansing it in the process (once again, providing optional
# findings), and receive the whole response:
response = await liminal.prompt.submit(
    model_instance.id,
    "Here is a sensitive prompt",
    findings=findings,
    thread_id=thread.id,
)
# >>> SubmitResponse(...)

# Submit a prompt, but this time, stream the response back chunk by chunk:
response = liminal.prompt.stream(
    model_instance.id,
    "Here is a sensitive prompt",
    findings=findings,
    thread_id=thread.id,
)
async for chunk in resp:
    # Each chunk is a liminal.endpoints.prompt.models.StreamResponseChunk object:
    print(chunk.content)
    print(chunk.finish_reason)

# Rehydrate a response with sensitive data:
hydrated = await liminal.prompt.hydrate(
    model_instance.id, "Here is a response to rehdyrate", thread_id=thread.id
)
# >>> HydrateResponse(...)
```

# Connection Pooling

By default, the library creates a new connection to the Liminal API server with each
coroutine. If you are calling a large number of coroutines (or merely want to squeeze
out every second of runtime savings possible), an [`httpx`][httpx] `AsyncClient` can be
used for connection pooling:

```python
import asyncio

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider


async def main() -> None:
    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = MicrosoftAuthProvider("<TENANT_ID>", "<CLIENT_ID>")

    # Create the liminal SDK instance with a shared HTTPX AsyncClient:
    async with httpx.AsyncClient() as client:
        liminal = Client(
            microsoft_auth_provider, "<LIMINAL_API_SERVER_URL>", httpx_client=client
        )

        # Get to work!
        # ...


asyncio.run(main())
```

Check out the examples, the tests, and the source files themselves for method
signatures and more examples.

# Running Examples

You can see examples of how to use this SDK via the [`examples`][examples] folder in
this repo. Each example follows a similar "call" format by asking for inputs via
environment variables; for example:

```sh
LIMINAL_API_SERVER_URL=https://api.DOMAIN.liminal.ai \
CLIENT_ID=xxxxxxxxxxxxxxxx \
TENANT_ID=xxxxxxxxxxxxxxxx \
MODEL_INSTANCE_NAME=model-instance-name \
python3 examples/quickstart_with_microsoft.py
```

# Contributing

Thanks to all of [our contributors][contributors] so far!

1. [Check for open features/bugs][issues] or [initiate a discussion on one][new-issue].
2. [Fork the repository][fork].
3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`
4. (_optional, but highly recommended_) Enter the virtual environment: `source ./.venv/bin/activate`
5. Install the dev environment: `./scripts/setup.sh`
6. Code your new feature or bug fix on a new branch.
7. Write tests that cover your new functionality.
8. Run tests and ensure 100% code coverage: `pytest --cov liminal tests`
9. Update `README.md` with any new documentation.
10. Submit a pull request!

[azure-portal]: https://portal.azure.com
[ci-badge]: https://img.shields.io/github/actions/workflow/status/liminal-ai-security/liminal-sdk-python/test.yml
[ci]: https://github.com/liminal-ai-security/liminal-sdk-python/actions
[contributors]: https://github.com/liminal-ai-security/liminal-sdk-python/graphs/contributors
[examples]: https://github.com/liminal-ai-security/liminal-sdk-python/tree/development/examples
[fork]: https://github.com/liminal-ai-security/liminal-sdk-python/fork
[httpx]: https://www.python-httpx.org/
[issues]: https://github.com/liminal-ai-security/liminal-sdk-python/issues
[license-badge]: https://img.shields.io/pypi/l/liminal-sdk-python.svg
[license]: https://github.com/liminal-ai-security/liminal-sdk-python/blob/main/LICENSE
[new-issue]: https://github.com/liminal-ai-security/liminal-sdk-python/issues/new
[notion]: https://getnotion.com
[oauth-device-auth-grant]: https://oauth.net/2/grant-types/device-code/
[pypi-badge]: https://img.shields.io/pypi/v/liminal-sdk-python.svg
[pypi]: https://pypi.python.org/pypi/liminal-sdk-python
[version-badge]: https://img.shields.io/pypi/pyversions/liminal-sdk-python.svg
[version]: https://pypi.python.org/pypi/liminal-sdk-python
