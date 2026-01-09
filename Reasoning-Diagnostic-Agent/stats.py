import math
import statistics

def print_stats(labels: list[str], data):
    if not data or len(data) != len(labels):
        print("Error: data length does not match labels length")
        return

    iteration_label = "Iteration #"

    # Determine number of rows (assuming all data lists have the same length)
    num_rows = len(data[0]) if data else 0

    # Calculate column widths
    col_widths = []
    col_widths.append(len(iteration_label))
    for col in range(len(labels)):
        max_width = len(labels[col])
        for row in range(num_rows):
            if row < len(data[col]):
                max_width = max(max_width, len(str(data[col][row])))
            else:
                max_width = max(max_width, len("N/A"))
        col_widths.append(max_width)

    # Print header
    print("\nSTATS:")
    header = " | ".join([f"{iteration_label:>{col_widths[0]}}", *[f"{labels[i]:>{col_widths[i+1]}}" for i in range(len(labels))]])
    print(header)

    # Print separator
    separator = "-+-".join("-" * col_widths[i] for i in range(len(labels)+1))
    print(separator)

    # Print rows
    for row in range(num_rows):
        row_data = []
        row_data.append(f"{(row+1):>{col_widths[0]}}")
        for col in range(len(labels)):
            if row < len(data[col]):
                value = str(data[col][row])
            else:
                value = "N/A"
            row_data.append(f"{value:>{col_widths[col+1]}}")
        print(" | ".join(row_data))

    if num_rows > 1:
        for col in range(len(labels)):
            # Calculate mean and standard deviation for column
            mean_col = statistics.mean(data[col])
            stdev_col = statistics.stdev(data[col])
            n = len(data[col])

            # Standard error of the mean
            sem = stdev_col / math.sqrt(n)

            # Mean with 95% z-score confidence interval
            print(f"\n{labels[col]} Mean: {mean_col:.2f} ± {(1.96 * sem):.2f}")


if __name__ == "__main__":

    labels = ["Diagnostic_elapsed_time", "LLM_similarity_score", "ST_similarity_score"]
    elapsed_time = [0,1,2]
    scores_llm = [3,4,5]
    scores_st = [6,7,8]

    print_stats(labels=labels, data=[elapsed_time, scores_llm, scores_st])
