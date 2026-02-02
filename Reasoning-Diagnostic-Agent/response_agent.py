from langchain_ollama import ChatOllama
from sentence_transformers import SentenceTransformer, util


def get_similarity_evaluator_prompt(generated: str, reference: str) -> str:
    return f"""
### LLM evaluator prompt

You are an automated **similarity evaluator**. Your job is to determine whether **every key detail listed in a reference string**
is present in a test string. The reference string will be a **list of key details to check** (not a free-form narrative). Treat
the reference list as the authoritative set of facts to verify. Do **not** judge, critique, or alter the reference list. Evaluate
**only** whether the test string contains the listed details and score based solely on those items. Produce a numeric score from
**0 to 100** and a concise list of any missing or partially present details. Follow the rules below exactly.

---

#### Task
1. Read the **reference string** (a list of key details) and the **test string**.
2. Parse the reference string into distinct **details** exactly as listed. Do **not** infer additional details beyond the items explicitly listed in the reference string.
3. For each listed detail, decide whether that detail is **present** in the test string (present = conveyed, possibly via paraphrase or equivalent form).
4. Compute a score between 0 and 100 where **100** means every listed detail is present in the test string, and **0** means none of the listed details are present.
5. Return a JSON object with three keys:
   - **score**: integer (0-100) — the final score rounded to the nearest integer.
   - **missing_details**: array of strings — each string is a concise description of a listed detail that is missing or only partially present in the test string. If none are missing, return an empty array.
   - **explanation**: short string (one or two sentences) summarizing how the score was computed.

---

#### Definitions and matching rules
- **Reference list**: the reference string is a list (comma-, semicolon-, or newline-separated) of the exact key details to check. Treat each list item as one detail unless the item itself contains multiple explicit sub-details separated by a clear delimiter; in that case, treat each explicit sub-detail as a separate detail only if the reference list itself separates them.
- **Detail**: any discrete fact, claim, or piece of information explicitly listed in the reference string (examples: named entities, dates, numeric values, relationships, actions, attributes, locations, categorical labels). Do **not** extract or invent additional details from the reference.
- **Present**: a listed detail is present if the test string **conveys the same fact**. Accept paraphrases, synonyms, and equivalent formats (e.g., "Jan 1, 2024" vs "2024-01-01", "ten" vs "10") as present when the meaning is the same.
- **Partial presence**: if the test string contains only part of a listed compound item (e.g., reference list item: "Alice, 35, from Seattle" and the test string has "Alice from Seattle"), treat the missing sub-detail ("35") as missing.
- **Ambiguity**: if the test string is ambiguous about a listed detail (could mean the same thing but not clearly), treat that detail as **missing**.
- **Named entities**: require the same referent. Different names that clearly refer to the same entity (aliases, widely known nicknames) count as present.
- **Numbers and units**: allow equivalent numeric formats and unit conversions only if equivalence is explicit or trivially derivable. If conversion is nontrivial or ambiguous, treat as missing.
- **Negation and polarity**: preserve polarity. If the reference list asserts X and the test denies X, the detail is missing.
- **Extra information** in the test string that is not in the reference list **must not** affect the score.
- **Zero-details case**: if the reference string contains no extractable list items (empty or whitespace only), return `score: 100`, `missing_details: []`, and an explanation stating no details to check.

---

#### Scoring method
- Start with **base = 100**.
- Let **N** be the number of distinct details parsed from the reference list.
  - If **N = 0**, return score 100.
  - Otherwise compute **deduction_per_detail = 100 / N**.
- For each listed detail:
  - If **present**, deduct **0**.
  - If **missing**, deduct **deduction_per_detail**.
  - If **partially present**, deduct **deduction_per_detail x 0.5**.
- Final score = `max(0, round(100 - sum(deductions)))`.
- Do not penalize for extra details in the test string.
- Round the final score to the nearest integer.

---

#### Output format (exact)
Return **only** a single JSON object (no surrounding text). Example structure:

```json
{{
  "score": 87,
  "missing_details": [
    "Reference date 2024-01-01 is missing",
    "Reference mentions 'paid in full' status which is not present"
  ],
  "explanation": "Reference had 6 details; 1 fully missing and 1 partially present produced deductions totaling 13 points."
}}
```

- **score** must be an integer between 0 and 100.
- **missing_details** must list each missing or partially missing listed detail as a short phrase.
- **explanation** must be one or two sentences describing N, how many missing/partial details, and the arithmetic that produced the score.

---

#### Examples with expected JSON responses

**Example 1**
Reference (list): `"order number: #123; shipped date: 2024-01-01; destination city: Seattle; item count: 3 items; payment status: paid"`
Extracted details (N=5): order number, shipped date, destination city, item count, payment status.
Test string lacks payment status and item count. Expected JSON response:

```json
{{
  "score": 60,
  "missing_details": [
    "item count (3 items) is missing",
    "payment status (paid) is missing"
  ],
  "explanation": "Reference had 5 details; 2 fully missing produced deductions of 20 points each, totaling 40 points, so score = 60."
}}
```

**Example 2**
Reference (list): `"name: Alice; age: 35; city: Seattle"`
Extracted details (N=3): name, age, city.
Test string: `"Alice from Seattle"` (age missing). Expected JSON response:

```json
{{
  "score": 67,
  "missing_details": [
    "age (35) is missing"
  ],
  "explanation": "Reference had 3 details; 1 fully missing produced a deduction of 33.33 points, rounded to 33, so score = 67."
}}
```

---

#### Tone and behavior
- Be objective and conservative: only mark a listed detail as present when the test string clearly conveys the same fact.
- Do not evaluate the truthfulness of the reference list; assume it is correct.
- Do not include any commentary beyond the required JSON output.

---

Use the instructions above to evaluate the two strings provided.

TEST string:
"{generated}"

REFERENCE string:
"{reference}"
    """


async def compare_agent_LLM(response: str, reference_response: str, model:str) -> str:
    print("🤖 Evaluating similarity with LLM")
    print("    Response")
    print("    --------")
    print(response)
    print("    Reference")
    print("    ---------")
    print(reference_response)

    messages = [("human", get_similarity_evaluator_prompt(response, reference_response))]

    llm = ChatOllama(
        model=model,
        verbose=True
        )

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


if __name__ == "__main__":
    import asyncio

    test = """
        **Root cause of the alert**

        The origin service **d3f1a8b2-7c4e-4f9e-9e2a-8b6c3a2d1f4e** is experiencing high latency on over 90 % of requests in the last hour because the deployment that hosts the service is overloaded with too many requests.

        * The deployment (`f3c9a7e2-8b4d-4f6a-9c2e-7d1b3a6e5c9f`) is running at an average CPU load of **98 %**.
        * It processes an average of **500 requests per second** across **2 role instances**, which equates to **250 req/s per instance**—well above the 100 req/s threshold that triggers a “system overloaded with too many requests” diagnosis.

        Thus, the high latency alert is caused by the deployment being saturated by a high request volume, leading to CPU contention and slower request handling.
    """
    reference = """
        The alert is triggered because the origin service is over-loaded with too many requests, which is causing CPU saturation and, in turn, high latency:

        * The origin service is running on a deployment where the average CPU load is 98% over the last hour.
        * This high CPU usage is due to the deployment receiving ≈500 requests/s while it has only 2 role instances, which results in ≈250 requests/s per instance—well above the 100 requests/s threshold.

        Because the CPU is saturated, the service cannot process requests quickly, leading to the observed high latency on more than 90% of requests.
    """

    # Run the LLM evaluator and print the JSON result
    result = asyncio.run(compare_agent_LLM(test, reference, "gpt-oss:20b"))
    print("---- Result ----")
    print(result)
