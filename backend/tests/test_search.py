from app.search import ResearchSearchEngine


def test_search_returns_results_for_known_topic():
    engine = ResearchSearchEngine()

    results = engine.search(
        "What is blockchain?",
        top_k=5,
    )

    assert isinstance(results, list)
    assert len(results) > 0

    for result in results:
        assert "score" in result
        assert "paper_id" in result
        assert "paper_name" in result
        assert "page_number" in result
        assert "text" in result
        assert result["text"].strip()


def test_search_returns_at_most_requested_top_k():
    engine = ResearchSearchEngine()

    results = engine.search(
        "blockchain architecture",
        top_k=3,
    )

    assert len(results) <= 3


def test_search_result_scores_are_sorted():
    engine = ResearchSearchEngine()

    results = engine.search(
        "What is blockchain?",
        top_k=5,
    )

    scores = [result["score"] for result in results]

    assert scores == sorted(scores, reverse=True)
