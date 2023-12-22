from auth.auth import _LoginService
import requests


class LiminalSDK:
    def __init__(
        self,
        liminal_client_url,
        authentication_service_type,
        client_id,
        client_secret,
        username,
    ):
        # TODO - The client url may not be the same as server URL.
        # We ping the server with the 8000 endpoint essentially for all of these calls
        # Make sure that's the case.
        self.liminal_client_url = liminal_client_url
        self.__auth_token = _LoginService(
            liminal_client_url,
            authentication_service_type,
            client_id,
            client_secret,
            username,
        )
        self.source = "SDK"
        self.llm_model = None
        self.thread_id = None

    def get_available_threads(self):
        # TODO - Probably may not want the pure requests.get,
        # but rather a helper function that does the requests.get and then parses the response.
        # Like we only really need the threadId from here, everything else is serverside.
        resp = requests.get(
            f"{self.liminal_client_url}/sdk/threads?source={self.source}",
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        resp = resp.json()
        # TODO - Probably want to save this for the user, to do cross checking if he has access.
        # So if user runs set_thread, it should cross validated
        return resp

    def get_thread(self):
        # Probably good enough - just let user know what thread he's working on?
        return self.thread_id

    def set_thread(self, thread_id):
        # TODO - Cross validate here
        if thread_id not in self.get_available_threads():
            raise Exception("Thread ID not available to user")
        # or something like that
        self.thread_id = thread_id

    def create_thread(self, name, llm_key):
        resp = requests.post(
            f"{self.liminal_client_url}/sdk/threads?source={self.source}",
            data={
                "name": name,
                "llmServiceModelKey": llm_key,
            },
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        if resp.status_code == 200:
            self.set_current_thread(resp.json().get("thread_id"))
        else:
            # TODO Catch better errors.
            raise
        return resp.json().get("threadId", None)  # or self.thread_id

    def get_available_llms(self):
        # TODO - make sure you have correct url here
        # Not sure exactly how we handle getting the models as of right now.
        resp = requests.get(
            f"https://{self.liminal_client_url}/v1/models",
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            # Catch better errors.
            raise

    def cleanse_prompt(self, prompt_text):
        if self.thread_id is None or self.llm_model is None:
            raise Exception("Thread ID and Model not set")

        resp = requests.post(
            f"{self.liminal_client_url}/sdk/cleanse_response?source={self.source}",
            data={"text": prompt_text, "threadId": self.thread_id},
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        if resp.status_code == 200:
            # TODO - may not need whole json, just text
            return resp.json()
        else:
            # TODO Catch better errors.
            raise

    def rehydrate_prompt(self, prompt_text):
        if self.thread_id is None or self.llm_model is None:
            raise Exception("Thread ID and Model not set")

        resp = requests.post(
            f"{self.liminal_client_url}/sdk/hydrate_response?source={self.source}",
            # TODO - look at SDK Architecture docs to find if you need any of the context stuff
            # Or if you want to let the server handle it all internally.
            data={"text": prompt_text, "threadId": self.thread_id},
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        if resp.status_code == 200:
            # TODO - may not need whole json, just text
            return resp.json()
        else:
            # TODO Catch better errors.
            raise

    def process(self, prompt_text):
        if self.thread_id is None or self.llm_model is None:
            raise Exception("Thread ID and Model not set")

        resp = requests.post(
            f"{self.liminal_client_url}/sdk/process?source={self.source}",
            # TODO - look at SDK Architecture docs to find if you need any of the context stuff
            # Or if you want to let the server handle it all internally.
            data={"text": prompt_text, "threadId": self.thread_id},
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        if resp.status_code == 200:
            # TODO - may not need whole json, just text
            return resp.json()
        else:
            # TODO Catch better errors.
            raise

    def get_deid_context_history(self):
        # TODO - needed?
        if self.thread_id is None or self.llm_model is None:
            raise Exception("Thread ID and Model not set")

        resp = requests.post(
            f"{self.liminal_client_url}/sdk/get_context_history?source={self.source}",
            # TODO - look at SDK Architecture docs to find if you need any of the context stuff
            # Or if you want to let the server handle it all internally.
            data={"threadId": self.thread_id},
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        if resp.status_code == 200:
            # TODO - may not need whole json, just text
            return resp.json()
        else:
            # TODO Catch better errors.
            raise

    def analyze(self, prompt_text):
        # TODO - needed?
        if self.thread_id is None or self.llm_model is None:
            raise Exception("Thread ID and Model not set")

        resp = requests.post(
            f"{self.liminal_client_url}/sdk/analyze_response?source={self.source}",
            # TODO - look at SDK Architecture docs to find if you need any of the context stuff
            # Or if you want to let the server handle it all internally.
            data={"text": prompt_text, "threadId": self.thread_id},
            headers={"Authorization": f"Bearer {self.__auth_token}"},
        )
        if resp.status_code == 200:
            # TODO - may not need whole json, just text
            return resp.json()
        else:
            # TODO Catch better errors.
            raise
