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

## gpt-oss:20b (temperature 1)

| Iteration # | Diagnostic_elapsed_time (s) | LLM_similarity_score | ST_similarity_score | Total_tokens |
|------------:|----------------------------:|---------------------:|--------------------:|-------------:|
|           1 |                       198.5 |                  100 |                  64 |        14467 |
|           2 |                      163.88 |                  100 |                  59 |        14637 |
|           3 |                      173.01 |                  100 |                  60 |        14254 |
|           4 |                      184.77 |                  100 |                  53 |        14876 |
|           5 |                      176.07 |                  100 |                  52 |        14814 |
|           6 |                      191.68 |                  100 |                  63 |        14457 |
|           7 |                      155.96 |                  100 |                  62 |        14528 |
|           8 |                      168.38 |                  100 |                  56 |        14231 |
|           9 |                      170.49 |                  100 |                  68 |        14662 |
|          10 |                      170.24 |                   80 |                  62 |        14621 |
|          11 |                      202.79 |                  100 |                  62 |        15048 |
|          12 |                      196.41 |                  100 |                  58 |        15016 |
|          13 |                      175.19 |                  100 |                  53 |        14678 |
|          14 |                      169.39 |                  100 |                  66 |        14197 |
|          15 |                      170.16 |                  100 |                  66 |        14228 |
|          16 |                      211.19 |                  100 |                  71 |        14601 |
|          17 |                      230.37 |                  100 |                  59 |        14828 |
|          18 |                      210.27 |                  100 |                  64 |        14609 |
|          19 |                      162.21 |                   80 |                  56 |        14586 |
|          20 |                      146.41 |                  100 |                  71 |        14441 |

Diagnostic_elapsed_time (s) Mean: 181.37 ± 9.31

LLM_similarity_score Mean: 98.00 ± 2.70

ST_similarity_score Mean: 61.25 ± 2.46

Total_tokens Mean: 14588.95 ± 109.34

Total elapsed time: 90.1 minutes


## gemma4:e4b (temperature 1)

| Iteration # | Diagnostic_elapsed_time (s) | LLM_similarity_score | ST_similarity_score | Total_tokens |
|------------:|----------------------------:|---------------------:|--------------------:|-------------:|
|           1 |                      547.49 |                  100 |                  44 |        19455 |
|           2 |                       547.1 |                  100 |                  43 |        23626 |
|           3 |                      699.59 |                  100 |                  42 |        25067 |
|           4 |                       398.2 |                   20 |                  44 |        21465 |
|           5 |                      587.96 |                  100 |                  42 |        24065 |
|           6 |                      374.61 |                  100 |                  45 |        16068 |
|           7 |                      430.91 |                  100 |                  53 |        19676 |
|           8 |                      467.95 |                  100 |                  44 |        18619 |
|           9 |                      495.81 |                    0 |                   7 |        23340 |
|          10 |                      572.56 |                   80 |                  59 |        22375 |
|          11 |                      707.53 |                  100 |                  54 |        25487 |
|          12 |                       471.2 |                  100 |                  45 |        17182 |
|          13 |                      448.87 |                  100 |                  43 |        19989 |
|          14 |                      236.86 |                  100 |                  44 |        17479 |
|          15 |                       738.2 |                   60 |                  63 |        24283 |
|          16 |                      400.96 |                  100 |                  52 |        16346 |
|          17 |                      437.62 |                    0 |                   7 |        22015 |
|          18 |                       490.3 |                   20 |                  47 |        17051 |
|          19 |                      366.89 |                    0 |                  44 |        14792 |
|          20 |                      522.51 |                  100 |                  41 |        21562 |

Diagnostic_elapsed_time (s) Mean: 497.16 ± 54.48

LLM_similarity_score Mean: 74.00 ± 17.78

ST_similarity_score Mean: 43.15 ± 6.02

Total_tokens Mean: 20497.10 ± 1441.48

Total elapsed time: 203.1 minutes


## granite4:32b-a9b-h (temperature 0.8 (Ollama default))

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


## qwen3.5:4b (temperature 1)

| Iteration # | Diagnostic_elapsed_time (s) | LLM_similarity_score | ST_similarity_score |
|------------:|----------------------------:|---------------------:|--------------------:|
|           1 |                         551 |                  100 |                  56 |

Total elapsed time: 31.4 minutes