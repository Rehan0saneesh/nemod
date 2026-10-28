import json
import time
from openai import OpenAI
from backend.config import settings

class HamiltonianAgent:
    def __init__(self, client: OpenAI):
        self.client = client

    def process(self, graph_dict: dict) -> tuple[dict, int]:
        start = time.perf_counter()
        prompt = (
            "You are a Quantum Operations Research Scientist specializing in QAOA formulations. "
            "Given this graph representing vehicle routing stops, construct the cost Hamiltonian parameters "
            "and suggest layer depth and angle priors to prevent barren plateaus.\n"
            "Output JSON with keys:\n"
            "  'p_layers': int (between 1 and 3)\n"
            "  'gamma_init': float (between 0.1 and 1.5)\n"
            "  'beta_init': float (between 0.1 and 1.5)\n"
            "  'penalty_weight': float\n\n"
            f"GRAPH:\n{json.dumps(graph_dict)}"
        )
        response = self.client.chat.completions.create(
            model=settings.MODEL_ULTRA,
            messages=[
                {"role": "system", "content": "Return valid JSON only. Do not wrap in markdown tags."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        data = json.loads(response.choices[0].message.content)
        return data, latency_ms