import pytest
from backend.agents.triage_agent import TriageAgent
from backend.agents.hamiltonian_agent import HamiltonianAgent

class MockChatChoice:
    def __init__(self, content):
        self.message = type('obj', (object,), {'content': content})

class MockChatResponse:
    def __init__(self, content):
        self.choices = [MockChatChoice(content)]

class MockOpenAIClient:
    def __init__(self, return_content):
        self.return_content = return_content
        self.chat = type('obj', (object,), {
            'completions': type('obj', (object,), {
                'create': lambda **kwargs: MockChatResponse(self.return_content)
            })
        })

def test_triage_agent():
    mock_payload = '{"nodes": [0, 1], "edges": [[0, 1, 4.5]]}'
    agent = TriageAgent(MockOpenAIClient(mock_payload))
    data, lat = agent.process("Route between stop 0 and 1 dist 4.5")
    assert "nodes" in data
    assert len(data["nodes"]) == 2

def test_hamiltonian_agent():
    mock_payload = '{"p_layers": 1, "gamma_init": 0.5, "beta_init": 0.5, "penalty_weight": 2.0}'
    agent = HamiltonianAgent(MockOpenAIClient(mock_payload))
    data, lat = agent.process({"nodes": [0, 1], "edges": [[0, 1, 1.0]]})
    assert data["p_layers"] == 1
    assert data["gamma_init"] == 0.5