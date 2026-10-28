import json
import time
from openai import OpenAI
from backend.config import settings

class TriageAgent:
    def __init__(self, client: OpenAI):
        self.client = client

    def process(self, raw_manifest: str) -> tuple[dict, int]:
        start = time.perf_counter()
        prompt = (
            "You are a logistics network extraction parser. Convert the following unstructured "
            "delivery manifest, fleet coordinates, or stop list into a strict mathematical graph.\n"
            "Output JSON only with keys:\n"
            "  'nodes': list of integer IDs (0 to N-1)\n"
            "  'edges': list of [u, v, weight] lists (undirected, weight is distance/cost)\n\n"
            f"MANIFEST:\n{raw_manifest}"
        )
        response = self.client.chat.completions.create(
            model=settings.MODEL_NANO,
            messages=[
                {"role": "system", "content": "Return valid JSON only. Do not wrap in markdown tags."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        data = json.loads(response.choices[0].message.content)
        return data, latency_ms