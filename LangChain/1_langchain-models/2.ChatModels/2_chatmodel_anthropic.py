from langchain_anthropic import ChatAnthropic


#model = ChatAnthropic(model='claude-3-5-sonnet-20241022')
model = None
try:
    model = ChatAnthropic(
        model="claude-3-5-haiku@20241022",  #  Specify the Claude model you want to use.
        temperature=0,                  #  Set the sampling temperature (0.0 to 1.0).
        max_tokens=1024,                #  Maximum number of tokens to generate.
        api_key="dial-mqjekw9tuhcrugvqhko5yfju5t8",                #  Optionally pass your Anthropic API key here.
        base_url="https://ai-proxy.lab.epam.com",               #  Optional: Specify a custom base URL if using a proxy or service emulator.
        timeout=None,                 #  Optional: Timeout for requests.
        max_retries=2,                #  Optional: Max number of retries if a request fails.
        
    )
    print("✅ ChatAnthropic model initialized successfully.")

    result = model.invoke('What is the capital of India')
    print("--Answer")
    print(result.content)
except Exception as e:
    print(f"🔥 Error during model initialization or invocation: {e}") 