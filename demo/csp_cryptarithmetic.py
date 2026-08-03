import sys
import time
from domains.cryptarithmetic.Cryptarithmetic import CryptarithmeticCSP
from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.ForwardChecking import forward_checking


def solve_crypto(addends, result):
    print(f"\nSolving Cryptarithmetic: {' + '.join(addends)} = {result}")
    
    try:
        problem = CryptarithmeticCSP(addends, result)
    except ValueError as e:
        print(f"Error: {e}")
        return
        
    # We use Forward Checking (MAC requires purely binary constraints)
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=mrv_with_degree_heuristic,
        order_domain_values=order_domain_values_default,
        inference=forward_checking
    )
    
    start = time.time()
    solution = solver.solve()
    duration = time.time() - start
    
    if solver.status == "SUCCESS":
        print(f"Solution found in {duration:.4f} seconds! (Nodes expanded: {solver.nodes_expanded})")
        print("Assignment:")
        for char, digit in sorted(solution.items()):
            print(f"  {char} = {digit}")
            
        print("\nVerification:")
        for word in addends:
            val = "".join(str(solution[c]) for c in word)
            print(f"  {word:10} -> {val:10}")
        print("  " + "-"*20)
        res_val = "".join(str(solution[c]) for c in result)
        print(f"  {result:10} -> {res_val:10}")
        
    else:
        print(f"NO SOLUTION EXISTS. Searched in {duration:.4f} seconds. (Nodes expanded: {solver.nodes_expanded})")


def main():
    if len(sys.argv) > 2:
        # Expecting: python -m demo.csp_cryptarithmetic WORD1 WORD2 [WORD3...] RESULT
        args = sys.argv[1:]
        addends = [w.upper() for w in args[:-1]]
        result = args[-1].upper()
        solve_crypto(addends, result)
    else:
        print("No custom words provided. Defaulting to SEND + MORE = MONEY")
        print("Usage: python -m demo.csp_cryptarithmetic [ADDEND1] [ADDEND2] ... [RESULT]")
        solve_crypto(["SEND", "MORE"], "MONEY")
        
        print("\n--- Another built-in example ---")
        solve_crypto(["TWO", "TWO"], "FOUR")


if __name__ == "__main__":
    main()
