from dotenv import load_dotenv
load_dotenv()
import uuid

from src.backend.graph.supervisor import build_graph, run_graph


def test_graph_compiles():
    app = build_graph()
    assert app is not None
    nodes = list(app.nodes.keys())
    expected = ["interview", "chat_state", "triage", "emergency", "resource_finder", "appointment"]
    for node in expected:
        assert node in nodes, f"Missing node: {node}"
    print(f"✓ graph compiled — nodes: {nodes}")


def test_run_graph_returns_dict():
    result = run_graph(
        most_recent_user_input="I have chest pain in Carrollton TX no insurance",
        thread_id=str(uuid.uuid4())
    )
    assert result is not None
    assert isinstance(result, dict)
    assert "chat_output" in result
    print("✓ run_graph returned dict")
