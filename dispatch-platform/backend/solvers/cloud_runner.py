import requests
import time
from backend.config import settings

def run_cloud_qaoa(graph_dict: dict, hamiltonian_spec: dict) -> tuple[dict, int]:
    start = time.perf_counter()
    payload = {
        "nodes": graph_dict["nodes"],
        "edges": graph_dict["edges"],
        "p_layers": hamiltonian_spec.get("p_layers", 1),
        "gamma_init": hamiltonian_spec.get("gamma_init", 0.5),
        "beta_init": hamiltonian_spec.get("beta_init", 0.5)
    }
    res = requests.post(f"{settings.CLOUD_WORKER_URL}/solve", json=payload, timeout=60)
    res.raise_for_status()
    latency_ms = int((time.perf_counter() - start) * 1000)
    return res.json(), latency_ms