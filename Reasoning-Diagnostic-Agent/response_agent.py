from langchain_ollama import ChatOllama

model = "llama3.2"

response_formatter_prompt = "You are a helpful assistant. Summarize the message into one sentence."

llm = ChatOllama(
    model=model,
    verbose=True
    )

async def query_agent(prompt: str) -> str:
    print("Formatting response")

    messages = [("system", response_formatter_prompt),
                ("human", prompt)
    ]

    response = llm.invoke(messages)

    return response.text()
