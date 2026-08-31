import numpy as np

from app.embeddings import generate_embeddings


def test_generate_embeddings_returns_expected_shape():
    texts = [
        "Blockchain is a distributed ledger.",
        "Artificial intelligence can analyze research papers.",
    ]

    embeddings = generate_embeddings(texts)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] > 0


def test_generate_embeddings_returns_normalized_vectors():
    texts = [
        "Blockchain is a distributed ledger.",
        "Research papers contain useful information.",
    ]

    embeddings = generate_embeddings(texts)

    norms = np.linalg.norm(embeddings, axis=1)

    assert np.allclose(norms, 1.0, atol=1e-5)
