import sys
import json
import time
import networkx as nx
import cudaq

def run_solver(graph_data: dict, p_layers: int, gamma_init: float, beta_init: float):
    start_time = time.perf_counter()

    try:
        cudaq.set_target("nvidia")
    except Exception:
        cudaq.set_target("default")

    G = nx.Graph()
    for u, v, w in graph_data["edges"]:
        G.add_edge(int(u), int(v), weight=float(w))

    num_qubits = len(graph_data["nodes"])
    p = p_layers

    hamiltonian = 0
    for u, v, data in G.edges(data=True):
        w = data.get("weight", 1.0)
        hamiltonian += 0.5 * w * (cudaq.spin.i - cudaq.spin.z(u) * cudaq.spin.z(v))

    @cudaq.kernel
    def qaoa_kernel(qubit_count: int, layers: int, thetas: list[float]):
        qreg = cudaq.qvector(qubit_count)
        h(qreg)
        for l in range(layers):
            gamma = thetas[l]
            beta = thetas[l + layers]
            for edge_idx, (u, v) in enumerate(G.edges()):
                cx(qreg[u], qreg[v])
                rz(2.0 * gamma, qreg[v])
                cx(qreg[u], qreg[v])
            for q in range(qubit_count):
                rx(2.0 * beta, qreg[q])

    optimizer = cudaq.optimizers.NelderMead()
    initial_thetas = [gamma_init] * p + [beta_init] * p

    def objective(params):
        return -cudaq.observe(qaoa_kernel, hamiltonian, num_qubits, p, params).expectation()

    _, opt_thetas = optimizer.optimize(dimensions=2 * p, function=objective)
    counts = cudaq.sample(qaoa_kernel, num_qubits, p, opt_thetas, shots_count=1000)

    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return {
        "status": "success",
        "best_bitstring": counts.most_probable(),
        "energy": float(objective(opt_thetas)),
        "solver_latency_ms": latency_ms,
        "target": cudaq.get_target().name
    }

if __name__ == "__main__":
    raw_in = sys.stdin.read()
    payload = json.loads(raw_in)
    res = run_solver(
        payload["graph_data"],
        payload.get("p_layers", 1),
        payload.get("gamma_init", 0.5),
        payload.get("beta_init", 0.5)
    )
    print(json.dumps(res))