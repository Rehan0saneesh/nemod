from fastapi import FastAPI
from pydantic import BaseModel
import networkx as nx
import cudaq
import time

app = FastAPI(title="Nebius CUDA-Q Cloud Worker")

try:
    cudaq.set_target("nvidia")
except Exception:
    cudaq.set_target("default")

class SolveRequest(BaseModel):
    nodes: list[int]
    edges: list[list[float]]
    p_layers: int = 1
    gamma_init: float = 0.5
    beta_init: float = 0.5

@app.post("/solve")
def solve(req: SolveRequest):
    start = time.perf_counter()
    G = nx.Graph()
    for u, v, w in req.edges:
        G.add_edge(int(u), int(v), weight=float(w))

    num_qubits = len(req.nodes)
    p = req.p_layers

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
    initial_thetas = [req.gamma_init] * p + [req.beta_init] * p

    def objective(params):
        return -cudaq.observe(qaoa_kernel, hamiltonian, num_qubits, p, params).expectation()

    _, opt_thetas = optimizer.optimize(dimensions=2 * p, function=objective)
    counts = cudaq.sample(qaoa_kernel, num_qubits, p, opt_thetas, shots_count=1000)
    latency_ms = int((time.perf_counter() - start) * 1000)

    return {
        "status": "success",
        "best_bitstring": counts.most_probable(),
        "energy": float(objective(opt_thetas)),
        "solver_latency_ms": latency_ms,
        "target": cudaq.get_target().name
    }