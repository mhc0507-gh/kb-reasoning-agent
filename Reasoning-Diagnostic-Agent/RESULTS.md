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
|           1 |                         215 |                  100 |                  59 |
|           2 |                         115 |                    0 |                  47 |
|           3 |                         191 |                   20 |                  49 |
|           4 |                         136 |                  100 |                  58 |
|           5 |                         143 |                  100 |                  58 |
|           6 |                         175 |                  100 |                  61 |
|           7 |                         200 |                  100 |                  59 |
|           8 |                         146 |                  100 |                  62 |
|           9 |                         191 |                  100 |                  55 |
|          10 |                         125 |                    0 |                  56 |
|          11 |                         186 |                  100 |                  53 |
|          12 |                         159 |                  100 |                  50 |
|          13 |                         151 |                   80 |                  61 |
|          14 |                         138 |                    0 |                  13 |
|          15 |                         270 |                  100 |                  67 |
|          16 |                         141 |                   20 |                  55 |
|          17 |                         158 |                  100 |                  61 |
|          18 |                         191 |                  100 |                  60 |
|          19 |                         177 |                  100 |                  64 |
|          20 |                         134 |                  100 |                  59 |

Diagnostic_elapsed_time (s) Mean: 167.10 ± 16.12

LLM_similarity_score Mean: 76.00 ± 17.90

ST_similarity_score Mean: 55.35 ± 4.89

Total elapsed time: 88.3 minutes


## granite4:32b-a9b-h

| Iteration # | Diagnostic_elapsed_time (s) | LLM_similarity_score | ST_similarity_score |
|------------:|----------------------------:|---------------------:|--------------------:|
|           1 |                         282 |                    0 |                  51 |
|           2 |                         268 |                   80 |                  57 |
|           3 |                         266 |                   80 |                  52 |
|           4 |                         200 |                   80 |                  66 |
|           5 |                         185 |                    0 |                  49 |
|           6 |                         214 |                    0 |                  44 |
|           7 |                         238 |                  100 |                  51 |
|           8 |                         219 |                   80 |                  68 |
|           9 |                         203 |                   40 |                  68 |
|          10 |                         169 |                    0 |                  58 |
|          11 |                         187 |                    0 |                  42 |
|          12 |                         177 |                    0 |                  56 |
|          13 |                         182 |                    0 |                  61 |
|          14 |                         180 |                    0 |                  43 |
|          15 |                         305 |                   60 |                  53 |
|          16 |                         236 |                   60 |                  61 |
|          17 |                         255 |                   40 |                  48 |
|          18 |                         284 |                    0 |                  57 |
|          19 |                         165 |                    0 |                  52 |
|          20 |                         147 |                    0 |                  46 |

Diagnostic_elapsed_time (s) Mean: 218.10 ± 20.16

LLM_similarity_score Mean: 31.00 ± 16.45

ST_similarity_score Mean: 54.15 ± 3.47

Total elapsed time: 99.4 minutes
