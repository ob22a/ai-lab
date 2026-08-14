from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict, deque
import itertools

from csp.CSPSolver import CSPSolver
from csp.CSPProblem import CSPProblem, Constraint
from csp.TreeCSP import TreeCSPSolver, get_constraint_graph, is_tree_graph


class ClusterAgreementConstraint(Constraint):
    """
    Constraint between two clusters (megavariables) ensuring they agree
    on all shared original variables (the separator).
    """
    def __init__(self, cluster1_id: Any, cluster2_id: Any, cluster1_vars: List[Any], cluster2_vars: List[Any]):
        super().__init__([cluster1_id, cluster2_id])
        self.c1_id = cluster1_id
        self.c2_id = cluster2_id
        self.c1_vars = cluster1_vars
        self.c2_vars = cluster2_vars
        self.shared_vars = [v for v in cluster1_vars if v in cluster2_vars]

    def is_satisfied(self, assignment: Dict[Any, Any]) -> bool:
        if self.c1_id not in assignment or self.c2_id not in assignment:
            return True
            
        tuple1 = assignment[self.c1_id]
        tuple2 = assignment[self.c2_id]
        
        # map var -> val for cluster 1
        map1 = dict(zip(self.c1_vars, tuple1))
        # map var -> val for cluster 2
        map2 = dict(zip(self.c2_vars, tuple2))
        
        for var in self.shared_vars:
            if map1[var] != map2[var]:
                return False
        return True


class TreeDecomposition:
    """
    Represents a tree decomposition of a CSP.
    - clusters: Dict mapping cluster_id -> List[original_variables]
    - edges: List of tuples (cluster_id_1, cluster_id_2) defining the tree structure
    """
    def __init__(self, clusters: Dict[str, List[Any]], edges: List[Tuple[str, str]]):
        self.clusters = clusters
        self.edges = edges

    def validate(self, csp: CSPProblem) -> Tuple[bool, str]:
        """
        Validates the 3 fundamental properties of Tree Decomposition:
        1. Variable Coverage: Every variable in csp must be in at least one cluster.
        2. Constraint Coverage: Every constraint's scope must be contained in at least one cluster.
        3. Running Intersection Property: For every variable X, the sub-graph of clusters 
           containing X must form a connected tree.
        """
        # Check that cluster edges form a tree
        cluster_ids = list(self.clusters.keys())
        cluster_adj = defaultdict(set)
        for u, v in self.edges:
            cluster_adj[u].add(v)
            cluster_adj[v].add(u)
            
        if not is_tree_graph(cluster_ids, cluster_adj):
            return False, "Cluster adjacency graph contains cycles or is disconnected."

        # 1. Variable Coverage
        all_cluster_vars = set()
        for cvars in self.clusters.values():
            all_cluster_vars.update(cvars)
        for var in csp.variables:
            if var not in all_cluster_vars:
                return False, f"Variable {var} not covered by any cluster."

        # 2. Constraint Coverage
        for var in csp.variables:
            for constraint in csp.constraints[var]:
                c_vars = set(constraint.variables)
                covered = any(c_vars.issubset(set(cvars)) for cvars in self.clusters.values())
                if not covered:
                    return False, f"Constraint on {constraint.variables} not contained within any single cluster."

        # 3. Running Intersection Property
        for var in csp.variables:
            var_clusters = [cid for cid, cvars in self.clusters.items() if var in cvars]
            if len(var_clusters) > 1:
                # Check connectedness in tree
                visited = set()
                queue = deque([var_clusters[0]])
                visited.add(var_clusters[0])
                var_clusters_set = set(var_clusters)
                
                while queue:
                    curr = queue.popleft()
                    for neighbor in cluster_adj[curr]:
                        if neighbor in var_clusters_set and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                            
                if visited != var_clusters_set:
                    return False, f"Clusters containing variable '{var}' do not form a connected subtree."

        return True, "Valid Tree Decomposition"


def auto_tree_decomposition(csp: CSPProblem) -> TreeDecomposition:
    """
    Heuristically constructs a tree decomposition for small/medium CSPs using 
    maximal cliques along an elimination ordering (e.g. Min-Fill heuristic).
    """
    adj = get_constraint_graph(csp)
    graph = {v: set(adj[v]) for v in csp.variables}
    remaining = set(csp.variables)
    clusters: Dict[str, List[Any]] = {}
    cluster_nodes: List[Set[Any]] = []
    
    # Elimination ordering using min-fill
    elim_order = []
    while remaining:
        # Pick vertex that adds minimum fill edges to its neighbors
        def fill_count(v):
            nbrs = list(graph[v] & remaining)
            fills = 0
            for i in range(len(nbrs)):
                for j in range(i + 1, len(nbrs)):
                    if nbrs[j] not in graph[nbrs[i]]:
                        fills += 1
            return fills
            
        best_v = min(remaining, key=lambda v: (fill_count(v), len(graph[v] & remaining)))
        elim_order.append(best_v)
        remaining.remove(best_v)
        
        # Connect all neighbors (create clique)
        nbrs = list(graph[best_v] & remaining)
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                graph[nbrs[i]].add(nbrs[j])
                graph[nbrs[j]].add(nbrs[i])
                
        clique = set(nbrs) | {best_v}
        # Check if subset of any existing cluster
        if not any(clique.issubset(c) for c in cluster_nodes):
            cluster_nodes.append(clique)

    for i, c in enumerate(cluster_nodes):
        clusters[f"C_{i+1}"] = sorted(list(c), key=lambda x: str(x))

    # Build maximum spanning tree of cluster intersections (Junction Tree)
    c_ids = list(clusters.keys())
    candidate_edges = []
    for i in range(len(c_ids)):
        for j in range(i + 1, len(c_ids)):
            u, v = c_ids[i], c_ids[j]
            weight = len(set(clusters[u]) & set(clusters[v]))
            if weight > 0:
                candidate_edges.append((weight, u, v))
                
    candidate_edges.sort(key=lambda x: x[0], reverse=True)
    
    # Kruskal's algorithm on clusters
    parent_map = {cid: cid for cid in c_ids}
    def find(x):
        if parent_map[x] != x:
            parent_map[x] = find(parent_map[x])
        return parent_map[x]
        
    tree_edges = []
    for w, u, v in candidate_edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent_map[ru] = rv
            tree_edges.append((u, v))
            
    # Connect any isolated clusters to the first component
    for cid in c_ids[1:]:
        if find(cid) != find(c_ids[0]):
            parent_map[find(cid)] = find(c_ids[0])
            tree_edges.append((c_ids[0], cid))

    return TreeDecomposition(clusters, tree_edges)


class TreeDecompositionSolver(CSPSolver):
    """
    Solves a general CSP by transforming it into a meta Tree-CSP using Tree Decomposition:
    1. Formulates clusters C_i of original variables as megavariables.
    2. Builds the domain of C_i as all valid combinations satisfying internal constraints.
    3. Adds ClusterAgreementConstraints along tree edges.
    4. Solves the meta tree CSP in linear time via TreeCSPSolver with 0 backtracks.
    5. Reconstructs original variable assignments.
    """
    def __init__(self, problem: CSPProblem, decomposition: Optional[TreeDecomposition] = None):
        super().__init__(problem)
        if decomposition is not None:
            self.decomposition = decomposition
            is_valid, msg = self.decomposition.validate(self.problem)
            if not is_valid:
                raise ValueError(f"Invalid Tree Decomposition: {msg}")
        else:
            self.decomposition = auto_tree_decomposition(self.problem)

    def _generate_cluster_domains(self) -> Optional[Dict[str, List[Tuple[Any, ...]]]]:
        """
        Finds all valid tuple assignments for each cluster that satisfy all 
        internal constraints within that cluster.
        """
        cluster_domains: Dict[str, List[Tuple[Any, ...]]] = {}
        
        for cid, cvars in self.decomposition.clusters.items():
            if not cvars:
                cluster_domains[cid] = [()]
                continue
                
            # Cartesian product of domain values for cvars
            var_domain_lists = [self.problem.domains[v] for v in cvars]
            valid_tuples = []
            
            # Find all internal constraints whose variables are entirely inside this cluster
            internal_constraints = []
            for v in cvars:
                for constr in self.problem.constraints[v]:
                    if all(cv in cvars for cv in constr.variables):
                        if constr not in internal_constraints:
                            internal_constraints.append(constr)
                            
            for combo in itertools.product(*var_domain_lists):
                self.nodes_expanded += 1
                assignment = dict(zip(cvars, combo))
                satisfied = True
                for constr in internal_constraints:
                    if not constr.is_satisfied(assignment):
                        satisfied = False
                        break
                if satisfied:
                    valid_tuples.append(combo)
                    
            if not valid_tuples:
                # One cluster has no valid internal assignment -> CSP unsolvable
                return None
                
            cluster_domains[cid] = valid_tuples
            
        return cluster_domains

    def _solve_impl(self) -> Optional[Dict[Any, Any]]:
        """
        Executes tree decomposition solving.
        """
        self.reset()
        cluster_domains = self._generate_cluster_domains()
        if cluster_domains is None:
            self.status = "FAILURE"
            return None

        # Build meta CSP
        meta_variables = list(self.decomposition.clusters.keys())
        meta_csp = CSPProblem(meta_variables, cluster_domains)
        
        # Add separator agreement constraints along tree edges
        for u, v in self.decomposition.edges:
            u_vars = self.decomposition.clusters[u]
            v_vars = self.decomposition.clusters[v]
            meta_csp.add_constraint(ClusterAgreementConstraint(u, v, u_vars, v_vars))
            
        # Solve meta-CSP with TreeCSPSolver
        tree_solver = TreeCSPSolver(meta_csp)
        meta_solution = tree_solver.solve()
        self.nodes_expanded += tree_solver.nodes_expanded
        
        if meta_solution is None:
            self.status = "FAILURE"
            return None
            
        # Reconstruct original variable assignment
        full_assignment = {}
        for cid, combo in meta_solution.items():
            cvars = self.decomposition.clusters[cid]
            for var, val in zip(cvars, combo):
                full_assignment[var] = val
                
        self.assignment = full_assignment
        self.status = "SUCCESS"
        return full_assignment
