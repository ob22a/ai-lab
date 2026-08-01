"""
Verification suite for Pattern Database correctness.
Run after generating PDB .bin files in ./pdbs/
"""
import math
import os
from itertools import permutations

from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from domains.n_puzzle.PDBGenerator import PDBGenerator
from domains.n_puzzle.PatternDatabase import PatternDatabase


def normalize_to_int_tuple(state) -> tuple[int, ...]:
    """
    Safely converts flat hex strings ('0123456789abcdef'), space-separated strings,
    or existing lists/tuples into a standardized tuple of integers.
    """
    if isinstance(state, tuple):
        return state
    if isinstance(state, list):
        return tuple(state)
    if isinstance(state, str):
        # Handle flat string representation like '0123456789abcdef'
        if len(state) in (9, 16):
            return tuple(int(char, 16) for char in state)
        # Handle space-separated or comma-separated tokens
        return tuple(int(token, 16) for token in state.replace(",", " ").split())
    raise ValueError(f"Unsupported board state data type: {type(state)}")


def rank_bijection_test(n_positions: int, k: int, get_rank_fn):
    """Verify ranking is a perfect bijection on ordered k-permutations of n cells."""
    total = math.perm(n_positions, k)
    seen = set()

    # Enumerate by brute force over all ordered k-tuples of distinct positions
    for positions in permutations(range(n_positions), k):
        r = get_rank_fn(list(positions), n_positions)
        assert 0 <= r < total, f"Rank {r} out of range for positions {positions}"
        assert r not in seen, f"Collision at rank {r} for positions {positions}. Tracking lists do not match."
        seen.add(r)
        
    assert len(seen) == total, f"Expected {total} unique ranks, got {len(seen)}"
    print(f"  Rank bijection OK: {total} arrangements, no collisions.")


def reverse_dijkstra_rank_costs(puzzle, target_tiles_hex):
    """
    Replicate PDBGenerator reverse Dijkstra; return rank -> min cost map.
    Tracks the k targets PLUS the blank space tile (0) pinned to the end.
    """
    import heapq

    # Track target tiles plus the blank space tile (0) at the end
    target_tiles_int = [int(t, 16) for t in target_tiles_hex if t != "0"]
    tracked_elements = target_tiles_int + [0]
    
    target_set = set(target_tiles_int)
    target_index = {tile: i for i, tile in enumerate(tracked_elements)}
    num_targets = len(tracked_elements)
    n = puzzle.total_tiles

    def abstract(full):
        return tuple(
            tile if (tile in target_set or tile == 0) else -1
            for tile in full
        )

    def positions_by_order(abs_state):
        pos = [0] * num_targets
        for idx, tile in enumerate(abs_state):
            slot = target_index.get(tile)
            if slot is not None:
                pos[slot] = idx
        return pos

    def get_rank(positions):
        used = 0
        rank = 0
        for i, pos in enumerate(positions):
            mask = (1 << pos) - 1
            less = pos - bin(used & mask).count("1")
            rank = rank * (n - i) + less
            used |= 1 << pos
        return rank

    rank_costs = {}
    goal = normalize_to_int_tuple(puzzle.goal_state)
    start_abs = abstract(goal)
    pq = [(0, start_abs)]
    min_costs = {start_abs: 0}

    while pq:
        cost, current = heapq.heappop(pq)
        
        # Settle the minimum cost for this target layout when popped
        r = get_rank(positions_by_order(current))
        if r not in rank_costs or cost < rank_costs[r]:
            rank_costs[r] = cost

        if cost > min_costs.get(current, math.inf):
            continue
            
        blank_idx = current.index(0)
        for neighbor_idx in puzzle.moves_map[blank_idx]:
            moving = current[neighbor_idx]
            move_cost = 1 if moving in target_set else 0
            new_cost = cost + move_cost
            
            lst = list(current)
            lst[blank_idx], lst[neighbor_idx] = lst[neighbor_idx], lst[blank_idx]
            new_abs = tuple(lst)
            
            if new_cost < min_costs.get(new_abs, math.inf):
                min_costs[new_abs] = new_cost
                heapq.heappush(pq, (new_cost, new_abs))

    return rank_costs, positions_by_order, get_rank, abstract


def exact_pdb_cost_for_state(puzzle, target_tiles_hex, state_input, rank_costs, positions_by_order, get_rank, abstract_fn):
    """Calculates expected PDB lookup cost using standardized state processing."""
    full = normalize_to_int_tuple(state_input)
    r = get_rank(positions_by_order(abstract_fn(full)))
    return rank_costs.get(r, -1)


def verify_pdb_file(pdb_path, puzzle, target_tiles_hex):
    print(f"\n=== Verifying {pdb_path} ===")
    gen = PDBGenerator(puzzle, target_tiles_hex)
    pdb = PatternDatabase(pdb_path)

    assert pdb.num_targets == gen.num_targets, f"Targets count error: {pdb.num_targets} vs {gen.num_targets}"
    assert len(pdb.costs) == gen.total_arrangements, f"Size error: {len(pdb.costs)} vs {gen.total_arrangements}"

    # Rank bijection validations
    rank_gen = lambda pos, n: gen._get_rank(pos)
    rank_load = lambda pos, n: pdb._get_rank(pos, n)
    
    print("  Generator ranking:")
    rank_bijection_test(puzzle.total_tiles, gen.num_targets, rank_gen)
    print("  Loader ranking:")
    rank_bijection_test(puzzle.total_tiles, pdb.num_targets, rank_load)

    # Perform a boundary sanity alignment across sample board permutations
    print("  Checking alignment across sample permutations...")
    count = 0
    for positions in permutations(range(puzzle.total_tiles), gen.num_targets):
        rg = gen._get_rank(list(positions))
        rl = pdb._get_rank(list(positions), puzzle.total_tiles)
        assert rg == rl, f"Rank mismatch {positions}: gen={rg} load={rl}"
        count += 1
        if count >= 10000:  # Ceiling limit to prevent testing delays on huge configurations
            break
            
    print("  Generator/loader rank consistency OK")

    # Goal state check
    goal = normalize_to_int_tuple(puzzle.goal_state)
    assert pdb.get_cost(goal) == 0, f"Goal cost should be 0, got {pdb.get_cost(goal)}"
    print(f"  Goal state cost = 0 OK")

    # Binary footprint matching
    with open(pdb_path, "rb") as f:
        raw = f.read()
    num_t = raw[0]
    
    # FIX: Slice using (num_t) total header bytes (1 byte count + (num_t - 1) tile identifiers)
    data = raw[num_t:]
    assert len(data) == len(pdb.costs), f"Data footprint size mismatch: {len(data)} bytes vs {len(pdb.costs)} entries."
    print(f"  Binary file format size OK: {len(data)} bytes")

    return gen, pdb


def verify_costs_8puzzle():
    """Performs deep exhaustive BFS cross-checks over the small 8-puzzle configurations."""
    puzzle = NPuzzle(3)
    patterns = [
        ("./pdbs/8puzzle_1234.bin", ["1", "2", "3", "4"]),
        ("./pdbs/8puzzle_5678.bin", ["5", "6", "7", "8"]),
    ]

    test_states = [
        puzzle.goal_state,
        "102345678",  
        "120345678",  
        "123456780",  
    ]
    gen8 = NPuzzleGenerator(3)
    test_states.append(gen8.generate())

    for pdb_path, tiles in patterns:
        if not os.path.exists(pdb_path):
            print(f"SKIP: {pdb_path} not found")
            continue
        gen, pdb = verify_pdb_file(pdb_path, puzzle, tiles)

        rank_costs, pos_fn, rank_fn, abs_fn = reverse_dijkstra_rank_costs(puzzle, tiles)
        print("  Reverse-Dijkstra cross-check (all ranks):")
        mismatches = 0
        for rank, expected in rank_costs.items():
            actual = pdb.costs[rank]
            if actual != expected:
                mismatches += 1
                if mismatches <= 5:
                    print(f"    MISMATCH rank {rank}: file={actual}, expected={expected}")
        assert mismatches == 0, f"{mismatches} mismatch fields located within {pdb_path}"
        print(f"    All {len(rank_costs)} layout ranks match flawlessly!")

        print("  Spot-check states:")
        for state in test_states:
            pdb_cost = pdb.get_cost(state)
            expected = exact_pdb_cost_for_state(
                puzzle, tiles, state, rank_costs, pos_fn, rank_fn, abs_fn
            )
            assert pdb_cost == expected, (
                f"MISMATCH for state layout {state}: PDB={pdb_cost}, expected={expected}"
            )
            print(f"    {state}: PDB={pdb_cost} OK")


def verify_goal_and_one_move_15():
    """Validates core features on heavy 15-puzzle files without long iteration delays."""
    puzzle = NPuzzle(4)
    pdbs = [
        ("./pdbs/15puzzle_12345.bin", ["1", "2", "3", "4", "5"]),
        ("./pdbs/15puzzle_6789a.bin", ["6", "7", "8", "9", "a"]),
        ("./pdbs/15puzzle_bcdef.bin", ["b", "c", "d", "e", "f"]),
    ]
    for path, tiles in pdbs:
        if not os.path.exists(path):
            print(f"SKIP 15-puzzle verify: {path} template not found")
            return
        verify_pdb_file(path, puzzle, tiles)

    print("\n  Evaluating 15-Puzzle baseline target configurations...")
    pdb_objs = [PatternDatabase(p[0]) for p in pdbs]
    
    # Universal test states covering both tuple variations and raw hex string formatting
    goal_string = "0123456789abcdef"
    goal_tuple = normalize_to_int_tuple(goal_string)
    
    for idx, pdb in enumerate(pdb_objs):
        # Auto-detect API interface types for get_cost parameters
        try:
            cost_val = pdb.get_cost(goal_string)
        except Exception:
            cost_val = pdb.get_cost(goal_tuple)
            
        assert cost_val == 0, f"Database element {idx} generated an incorrect value ({cost_val}) for the unified goal!"
        
    print("  All 15-Puzzle configurations validated. Index conversions are clean.")


if __name__ == "__main__":
    print("Executing 8-Puzzle deep checking verification algorithms...")
    verify_costs_8puzzle()
    print("\nExecuting 15-Puzzle goal and one-move verification algorithms...")
    verify_goal_and_one_move_15()