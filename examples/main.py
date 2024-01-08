from liminalsdk import LiminalSDK

liminal = LiminalSDK(
  <liminal_client_url>,
  <authentication_service_type>,
  <client_id>,
  <client_secret>,
  <username> # Email address
)

liminal.get_threads() # returns available threadIds to the user (done through Auth) if none, we tell the user to create a new thread.
liminal.get_available_llms() # MIGHT be necessary for the below:
liminal.create_thread(name, llmKey) # creates a thread with a name and llmKey from getAvailableLLMs(), which lets the user know which llms the admin has enabled. I believe we already have this functionality? Likewise, this function should also set it to said thread, and return the threadId.
liminal.set_thread(threadId) # sets the thread to the threadId Errors out if threadId not available to user internally.

liminal_clean_data = liminal.cleanse_prompt(prompt_text)
liminal_rehydrated_data = liminal.rehydrate_rompt(prompt_text)
llm_response_data = liminal.process(prompt_text)
