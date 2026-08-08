import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.map_coloring.MapColoring import MapColoringCSP
from domains.n_queens.NQueensCSP import NQueensCSP
from csp.Backtracking import BacktrackingSolver
from csp.SymmetricBacktracking import SymmetricBacktrackingSolver
from csp.heuristics.MRV import mrv
from csp.inference.ForwardChecking import forward_checking


def main():
    print("=" * 65)
    print("         SYMMETRIC BACKTRACKING & SYMMETRY BREAKING DEMO")
    print("=" * 65)
    
    # -------------------------------------------------------------
    # 1. Value Symmetry Breaking on Map Coloring
    # -------------------------------------------------------------
    print("1. MAP COLORING (Value Permutation Symmetry)")
    print("   Permuting colors (e.g. Red <-> Green <-> Blue) produces isomorphic search trees.")
    print("   Value symmetry breaking guarantees that at any node with unassigned colors,")
    print("   at most ONE unused color is explored, pruning redundant isomorphic branches.\n")
    
    mc_standard = BacktrackingSolver(MapColoringCSP())
    mc_standard.solve()
    
    mc_symmetric = SymmetricBacktrackingSolver(MapColoringCSP(), value_symmetry=True)
    mc_symmetric.solve()
    
    print(f"   Standard Backtracking nodes:  {mc_standard.nodes_expanded}")
    print(f"   Symmetric Backtracking nodes: {mc_symmetric.nodes_expanded}")
    print(f"   Map Coloring Solution: {mc_symmetric.assignment}\n")
    
    # -------------------------------------------------------------
    # 2. Geometric / Variable Symmetry Breaking on 6-Queens CSP
    # -------------------------------------------------------------
    print("2. 6-QUEENS CSP (Geometric Reflection Symmetry)")
    print("   Chessboard has D4 dihedral symmetry. Restricting Queen 0 to the left half")
    print("   of the board (columns 0..N//2) eliminates half of the symmetric search space!\n")
    
    # 2a. Standard 6-Queens Backtracking
    nq_standard = BacktrackingSolver(
        NQueensCSP(n=6, break_symmetry=False),
        inference=forward_checking
    )
    nq_standard.solve()
    
    # 2b. Symmetry-Broken 6-Queens Backtracking
    nq_symmetric = SymmetricBacktrackingSolver(
        NQueensCSP(n=6, break_symmetry=True),
        inference=forward_checking
    )
    nq_symmetric.solve()
    
    print(f"   Standard 6-Queens FC nodes:  {nq_standard.nodes_expanded}")
    print(f"   Symmetric 6-Queens FC nodes: {nq_symmetric.nodes_expanded}")
    print(f"   Reduction in nodes explored: {((nq_standard.nodes_expanded - nq_symmetric.nodes_expanded) / nq_standard.nodes_expanded) * 100:.1f}%")
    print(f"   Solution Found: {nq_symmetric.assignment}")
    print("=" * 65)


if __name__ == "__main__":
    main()
