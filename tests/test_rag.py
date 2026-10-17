"""Tests for RAG ingestion, chunking, vector store, and hybrid retrieval."""

from app.rag.chunker import ClauseAwareChunker
from app.rag.embeddings import DeterministicEmbedding
from app.rag.loader import RegulationLoader
from app.rag.retriever import HybridRetriever, tokenize_for_bm25
from app.rag.vector_store import VectorStore

SAMPLE_REGULATION_TEXT = """[DOCUMENT: UNECE Regulation No. 48 - Installation]

[CLAUSE: 6.2.6 - Dipped-Beam Initial Aim]
Clause 6.2.6.1.2: Depending on the mounting height in metres (h) of the dipped-beam headlamp,
the vertical inclination of the cut-off must remain between:
- For h < 0.8 m: between -0.5% and -2.5% (initial aim between -1.0% and -1.5%).
- For h > 1.0 m: between -1.0% and -3.0% (initial aim between -1.5% and -2.0%).

[CLAUSE: 6.5.9 - Direction-Indicator Flashing Frequency]
Clause 6.5.9: The frequency of the light flash must be 90 +/- 30 periods per minute (1.5 +/- 0.5 Hz).
The time interval between the first flash and activation must not exceed one second.
"""


def test_clause_aware_chunking():
    chunker = ClauseAwareChunker()
    chunks = chunker.chunk_text(SAMPLE_REGULATION_TEXT, default_doc_name="Test UNECE R48")

    assert len(chunks) == 2
    assert chunks[0].clause_id == "6.2.6"
    assert chunks[0].section_title == "Dipped-Beam Initial Aim"
    assert "vertical inclination" in chunks[0].text
    assert chunks[0].chunk_id == "R48-6.2.6"

    assert chunks[1].clause_id == "6.5.9"
    assert "90 +/- 30 periods per minute" in chunks[1].text
    assert chunks[1].chunk_id == "R48-6.5.9"


def test_tokenization_preserves_numbers_and_symbols():
    text = "Clause 6.2.6.1.2: inclination -0.5% to -2.5% at 1.5 Hz"
    tokens = tokenize_for_bm25(text)
    assert "6.2.6.1.2" in tokens
    assert "-0.5%" in tokens
    assert "1.5" in tokens
    assert "hz" in tokens


def test_vector_store_and_hybrid_retrieval(tmp_path):
    temp_chroma = str(tmp_path / "test_chroma")
    embedding_engine = DeterministicEmbedding()
    store = VectorStore(persist_dir=temp_chroma, embedding_engine=embedding_engine)

    chunker = ClauseAwareChunker()
    chunks = chunker.chunk_text(SAMPLE_REGULATION_TEXT)
    indexed = store.add_chunks(chunks)
    assert indexed == 2
    assert store.count() == 2

    # Test retrieval by ID for citation verifier
    chunk = store.get_chunk_by_id("R48-6.2.6")
    assert chunk is not None
    assert "vertical inclination" in chunk["text"]

    # Test Hybrid Retrieval
    retriever = HybridRetriever(vector_store=store)
    hits = retriever.retrieve(
        "What is the flashing frequency of direction indicators in Hz?", top_k=2
    )

    assert len(hits) > 0
    top_hit = hits[0]
    assert top_hit["chunk_id"] == "R48-6.5.9"
    assert "90 +/- 30" in top_hit["text"]


def test_regulation_loader_real_files():
    loader = RegulationLoader()
    chunks = loader.load_all()
    # We created unece_r48_excerpt.txt and unece_r112_excerpt.txt
    assert len(chunks) >= 10
    clause_ids = [c.clause_id for c in chunks]
    assert any("6.2.6" in cid for cid in clause_ids)
    assert any("6.5.7" in cid or "6.5.9" in cid for cid in clause_ids)
