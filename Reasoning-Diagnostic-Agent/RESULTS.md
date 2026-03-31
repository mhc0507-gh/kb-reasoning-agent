# Results from Test Executions

## Evaluation Methodology

### LLM Similarity Score

The **LLM similarity score** (0–100) evaluates how well the diagnostic agent's response covers key details from a reference response. An LLM evaluator uses a structured prompt to:

1. Extract key details and facts from the reference response
2. Check whether each key detail is present or partially present in the generated response
3. Calculate a coverage percentage based on the number of matched details
4. Return a JSON result with:
   - **Score**: 0–100 integer (percentage of key details found)
   - **Missing details**: List of details absent or only partially covered
   - **Explanation**: Brief summary of coverage analysis

**Use case**: Validates whether the diagnostic output contains all essential findings and root cause information from the reference.

### Sentence-Transformer (ST) Similarity Score

The **Sentence-Transformer similarity score** (0–100) uses semantic embeddings to measure response similarity:

1. Generates vector embeddings for both the generated and reference responses using the `all-MiniLM-L6-v2` model
2. Computes cosine similarity between the two embeddings (range: -1 to 1)
3. Scales the result to 0–100 (0 = completely dissimilar, 100 = identical)

**Use case**: Fast, embedding-based similarity check that captures semantic meaning without requiring detailed key-point extraction.

---

## gpt-oss:20b

| Iteration # | Diagnostic_elapsed_time (s) | LLM_similarity_score | ST_similarity_score |
|------------:|----------------------------:|---------------------:|--------------------:|
|           1 |                         228 |                  100 |                  61 |
|           2 |                         217 |                  100 |                  56 |
|           3 |                         234 |                  100 |                  56 |
|           4 |                         222 |                  100 |                  67 |
|           5 |                         175 |                  100 |                  63 |
|           6 |                         207 |                  100 |                  68 |
|           7 |                         245 |                  100 |                  63 |
|           8 |                         195 |                  100 |                  65 |
|           9 |                         203 |                  100 |                  49 |
|          10 |                         184 |                  100 |                  57 |
|          11 |                         196 |                  100 |                  60 |
|          12 |                         196 |                  100 |                  65 |
|          13 |                         223 |                  100 |                  56 |
|          14 |                         236 |                  100 |                  58 |
|          15 |                         224 |                  100 |                  62 |
|          16 |                         175 |                  100 |                  60 |
|          17 |                         366 |                  100 |                  68 |
|          18 |                         186 |                  100 |                  59 |
|          19 |                         226 |                  100 |                  49 |
|          20 |                         306 |                   80 |                  69 |

Diagnostic_elapsed_time (s) Mean: 222.20 ± 19.75

LLM_similarity_score Mean: 99.00 ± 1.96

ST_similarity_score Mean: 60.55 ± 2.52

Total elapsed time: 111.7 minutes


## granite4:32b-a9b-h

| Iteration # | Diagnostic_elapsed_time (s) | LLM_similarity_score | ST_similarity_score |
|------------:|----------------------------:|---------------------:|--------------------:|
|           1 |                         289 |                   20 |                  50 |
|           2 |                         227 |                   80 |                  58 |
|           3 |                         244 |                   60 |                  62 |
|           4 |                         214 |                   80 |                  61 |
|           5 |                         283 |                  100 |                  62 |
|           6 |                         321 |                   60 |                  49 |
|           7 |                         203 |                   60 |                  54 |
|           8 |                         331 |                   80 |                  47 |
|           9 |                         231 |                   80 |                  63 |
|          10 |                         220 |                   20 |                  64 |
|          11 |                         214 |                   80 |                  65 |
|          12 |                         263 |                   40 |                  60 |
|          13 |                         346 |                   80 |                  55 |
|          14 |                         262 |                   80 |                  56 |
|          15 |                         270 |                   80 |                  49 |
|          16 |                         279 |                   60 |                  57 |
|          17 |                         249 |                   80 |                  50 |
|          18 |                         214 |                   60 |                  59 |
|          19 |                         283 |                   80 |                  54 |
|          20 |                         247 |                   80 |                  48 |

Diagnostic_elapsed_time (s) Mean: 259.50 ± 18.04

LLM_similarity_score Mean: 68.00 ± 9.17

ST_similarity_score Mean: 56.15 ± 2.55

Total elapsed time: 112.5 minutes


## qwen3.5:4b

| Iteration # | Diagnostic_elapsed_time (s) | LLM_similarity_score | ST_similarity_score |
|------------:|----------------------------:|---------------------:|--------------------:|
|           1 |                         551 |                  100 |                  56 |

Total elapsed time: 31.4 minutes