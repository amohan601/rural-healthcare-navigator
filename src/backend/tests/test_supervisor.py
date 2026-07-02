from dotenv import load_dotenv
load_dotenv()


from src.backend.graph.supervisor import run_graph


from src.backend.graph.supervisor import build_graph, run_graph


def test_graph_compiles():
    app = build_graph()
    assert app is not None
    nodes = list(app.nodes.keys())
    expected = ["triage", "resource_finder", "insurance_checker",
                "appointment_prep", "reflection", "human_approver", "synthesizer"]
    for node in expected:
        assert node in nodes, f"Missing node: {node}"
    print(f"✓ graph compiled — nodes: {nodes}")


def test_run_graph_returns_dict():
    result = run_graph(
        user_query="I have chest pain in Carrollton TX no insurance",
        thread_id=str(uuid.uuid4())
    )
    assert result is not None
    assert isinstance(result, dict)
    print("✓ run_graph returned dict")


def test_triage_result_populated():
    result = run_graph(
        user_query="I have chest pain in Carrollton TX",
        thread_id=str(uuid.uuid4())
    )
    triage = result.get("triage_result")
    assert triage is not None,                    "triage_result missing"
    assert "urgency"        in triage,            "urgency missing"
    assert "conditions"     in triage,            "conditions missing"
    assert "recommendation" in triage,            "recommendation missing"
    assert triage["urgency"] in ("LOW", "MEDIUM", "HIGH")
    print(f"✓ triage_result: urgency={triage['urgency']} conditions={triage['conditions']}")


def test_resource_finder_result_populated():
    result = run_graph(
        user_query="I have chest pain in Carrollton TX no insurance",
        thread_id=str(uuid.uuid4())
    )
    rf = result.get("resource_finder_result")
    assert rf is not None,                   "resource_finder_result missing"
    assert "providers" in rf,               "providers key missing"
    assert "summary"   in rf,               "summary key missing"
    assert isinstance(rf["providers"], list)
    assert isinstance(rf["summary"],   str)
    print(f"✓ resource_finder_result: {len(rf['providers'])} providers")
    print(f"  summary: {rf['summary'][:100]}...")


def test_final_response_populated():
    result = run_graph(
        user_query="I have a fever in Austin TX",
        thread_id=str(uuid.uuid4())
    )
    assert result.get("final_response"), "final_response missing"
    print(f"✓ final_response: {result['final_response'][:100]}...")


def test_reflection_populated():
    result = run_graph(
        user_query="ankle sprain Dallas TX",
        thread_id=str(uuid.uuid4())
    )
    reflection = result.get("reflection")
    assert reflection is not None,          "reflection missing"
    assert "score" in reflection,           "score missing from reflection"
    assert reflection["score"] >= 1
    print(f"✓ reflection score={reflection['score']}")


def test_approved_populated():
    result = run_graph(
        user_query="headache in Phoenix AZ",
        thread_id=str(uuid.uuid4())
    )
    assert result.get("approved") is True, "approved should be True from stub"
    print("✓ approved=True")


def test_multi_turn_memory():
    thread_id = str(uuid.uuid4())
    first  = run_graph(user_query="chest pain in Carrollton TX", thread_id=thread_id)
    second = run_graph(user_query="I also have diabetes",         thread_id=thread_id)
    assert first.get("triage_result")  is not None
    assert second.get("triage_result") is not None
    print(f"✓ multi-turn: turn1={first['triage_result'].get('urgency')} turn2={second['triage_result'].get('urgency')}")


def test_different_queries():
    queries = [
        "severe headache in Phoenix AZ",
        "cough for 3 weeks in Austin TX",
        "ankle sprain no insurance Dallas TX",
    ]
    for q in queries:
        result = run_graph(user_query=q, thread_id=str(uuid.uuid4()))
        triage = result.get("triage_result", {})
        print(f"  {q[:40]:40} → {triage.get('urgency', 'N/A')}")
    print("✓ all queries handled")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("\n" + "="*60)
    print("DAY 3 — SUPERVISOR TESTS")
    print("="*60 + "\n")

    tests = [
        test_graph_compiles,
        test_run_graph_returns_dict,
        test_triage_result_populated,
        test_resource_finder_result_populated,
        test_final_response_populated,
        test_reflection_populated,
        test_approved_populated,
        test_multi_turn_memory,
        test_different_queries,
    ]

    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(tests)} passed  {failed} failed")
    print("✅ Day 3 complete — ready for Day 4" if not failed else "❌ Fix failures before Day 4")
    print("="*60)

