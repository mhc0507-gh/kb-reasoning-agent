def print_stats(labels: list[str], data):
    if not data or len(data) != len(labels):
        print("Error: data length does not match labels length")
        return

    # Determine number of rows (assuming all data lists have the same length)
    num_rows = len(data[0]) if data else 0

    # Calculate column widths
    col_widths = []
    for col in range(len(labels)):
        max_width = len(labels[col])
        for row in range(num_rows):
            if row < len(data[col]):
                max_width = max(max_width, len(str(data[col][row])))
            else:
                max_width = max(max_width, len("N/A"))
        col_widths.append(max_width)

    # Print header
    header = " | ".join(f"{labels[i]:>{col_widths[i]}}" for i in range(len(labels)))
    print(header)

    # Print separator
    separator = "-+-".join("-" * col_widths[i] for i in range(len(labels)))
    print(separator)

    # Print rows
    for row in range(num_rows):
        row_data = []
        for col in range(len(labels)):
            if row < len(data[col]):
                value = str(data[col][row])
            else:
                value = "N/A"
            row_data.append(f"{value:>{col_widths[col]}}")
        print(" | ".join(row_data))

if __name__ == "__main__":

    labels = ["Diagnostic_elapsed_time", "LLM_similarity_score", "ST_similarity_score"]
    elapsed_time = [0,1,2]
    scores_llm = [3,4,5]
    scores_st = [6,7,8]

    print_stats(labels=labels, data=[elapsed_time, scores_llm, scores_st])
