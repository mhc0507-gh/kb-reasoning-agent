from langchain_ollama import ChatOllama
from sentence_transformers import SentenceTransformer, util

model = "llama3.2"

response_formatter_prompt = "You are a helpful assistant. Summarize the message into one sentence."

def get_similarity_evaluator_prompt(generated: str, reference: str) -> str:
    return f"""
    You are a semantic similarity evaluator.

    Compare the generated text with the reference text and score their semantic similarity
    on a scale from 0 to 100, where:

    - 100 = identical meaning
    - 80-99 = very similar meaning (generated text has all information present in reference text)
    - 50-79 = somewhat similar meaning (generated text is missing information present in reference text)
    - 1-49 = weak similarity
    - 0 = completely unrelated

    GENERATED:
    "{generated}"

    REFERENCE:
    "{reference}"

    Return ONLY valid JSON in this format:
    {{
        "score": <number>,
        "explanation": "<short explanation>"
    }}
    """

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


async def compare_agent_LLM(response: str, reference_response: str) -> str:
    print("🤖 Evaluating similarity with LLM")
    print(f"    Response:  {response}")
    print(f"    Reference: {reference_response}")

    messages = [("human", get_similarity_evaluator_prompt(response, reference_response))]

    similarity_response = llm.invoke(messages)

    return similarity_response.text()


async def compare_agent_ST(response: str, reference_response: str) -> int:
    print("🤖 Evaluating similarity with ST")
    # print(f"    Response:  {response}")
    # print(f"    Reference: {reference_response}")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    emb1 = model.encode(response)
    emb2 = model.encode(reference_response)

    score = util.cos_sim(emb1, emb2)

    # Convert to int on scale 0-100
    return int(score.item() * 100)
