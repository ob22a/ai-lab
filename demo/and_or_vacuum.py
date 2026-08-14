"""
demo/and_or_vacuum.py
AND-OR Search in Vacuum World Demo.

Demonstrates AND-OR graph search for contingency planning in both
deterministic and stochastic (slippery) vacuum world environments.

Usage:
    python -m demo.and_or_vacuum [--vis]

Note: Vacuum World runs in console mode only (no visualizer).
"""

import argparse
from domains.vacuum.VacuumWorld import VacuumWorld
from search.online.ANDORSearch import ANDORSearch


def print_plan(plan, indent=""):
    if plan is None:
        print(f"{indent}Failure")
        return
    if len(plan) == 0:
        print(f"{indent}[Goal Reached]")
        return
        
    print(f"{indent}Do: {plan['action']}")
    for outcome_state, subplan in plan['outcomes'].items():
        pos, dirt = outcome_state
        print(f"{indent}  If Agent at {pos}, Dirt at {set(dirt)}:")
        print_plan(subplan, indent + "    ")


def main():
    parser = argparse.ArgumentParser(description="AND-OR Search in Vacuum World")
    parser.add_argument("--vis", action="store_true", help="Launch visualizer (not available for Vacuum World)")
    args = parser.parse_args()

    if args.vis:
        print("Note: Vacuum World runs in console mode only (no visualizer).")
        print("Continuing with console output...\n")

    print("--- AND-OR Search in Vacuum World ---")
    
    width, height = 2, 1
    start_pos = (0, 0)
    dirt = {(0, 0), (1, 0)}
    
    print("\nEnvironment: 2x1 grid.")
    print("Agent starts at (0, 0). Dirt at (0, 0) and (1, 0).")
    
    # 1. Deterministic Vacuum World
    print("\n1. Deterministic (Non-slippery):")
    problem1 = VacuumWorld(width, height, start_pos, dirt, slippery=False)
    search1 = ANDORSearch(problem1)
    plan1 = search1.run()
    print_plan(plan1)

    # 2. Slippery Vacuum World
    print("\n2. Slippery (Movement actions might fail and leave agent in same spot):")
    print("Standard AND-OR search fails when cycles are possible (Try-Try-Again).")
    problem2 = VacuumWorld(width, height, start_pos, dirt, slippery=True)
    search2 = ANDORSearch(problem2)
    plan2 = search2.run()
    print_plan(plan2)
    
if __name__ == "__main__":
    main()
