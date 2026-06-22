def print_puzzle(state: str, size: int):
    """Prints the puzzle string in a readable 2D grid format."""
    print(f"State String: '{state}'")
    for i in range(size):
        # Extract the row
        row = state[i*size:(i+1)*size]
        # Replace 0 with _ for readability
        row_str = " ".join(row).replace("0", "_")
        print(row_str)
    print("-" * (size * 2))
