"""Document chunk models and clause-aware chunker for regulations."""

import re
from dataclasses import dataclass, field


@dataclass
class RegulationChunk:
    chunk_id: str
    document: str
    clause_id: str
    section_title: str
    text: str
    page: int = 1
    metadata: dict = field(default_factory=dict)


class ClauseAwareChunker:
    """Chunks structured regulatory texts while preserving clause numbers and hierarchy."""

    DOCUMENT_HEADER_PATTERN = re.compile(r"^\[DOCUMENT:\s*(.+?)\]", re.MULTILINE)
    CLAUSE_HEADER_PATTERN = re.compile(r"^\[CLAUSE:\s*([\d\.]+)\s*-\s*(.+?)\]", re.MULTILINE)

    def chunk_text(
        self, text: str, default_doc_name: str = "UNECE Regulation"
    ) -> list[RegulationChunk]:
        """Split text by clause headers and generate atomic regulation chunks."""
        doc_name = default_doc_name
        doc_match = self.DOCUMENT_HEADER_PATTERN.search(text)
        if doc_match:
            doc_name = doc_match.group(1).strip()

        # Split on clause headers
        clause_splits = list(self.CLAUSE_HEADER_PATTERN.finditer(text))
        if not clause_splits:
            # Fallback: paragraph-based chunking if no explicit clause headers
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
            chunks = []
            for idx, p in enumerate(paragraphs, start=1):
                clean_doc = re.sub(r"[^a-zA-Z0-9]", "_", doc_name)[:12]
                chunks.append(
                    RegulationChunk(
                        chunk_id=f"{clean_doc}-P{idx}",
                        document=doc_name,
                        clause_id=f"Para-{idx}",
                        section_title="General",
                        text=p,
                    )
                )
            return chunks

        chunks: list[RegulationChunk] = []
        for i, match in enumerate(clause_splits):
            clause_id = match.group(1).strip()
            section_title = match.group(2).strip()

            start_pos = match.end()
            end_pos = clause_splits[i + 1].start() if i + 1 < len(clause_splits) else len(text)
            clause_body = text[start_pos:end_pos].strip()

            # Create clean short chunk ID (e.g. R48-6.2.6)
            doc_prefix = "R48" if "48" in doc_name else ("R112" if "112" in doc_name else "REG")
            chunk_id = f"{doc_prefix}-{clause_id}"

            chunk = RegulationChunk(
                chunk_id=chunk_id,
                document=doc_name,
                clause_id=clause_id,
                section_title=section_title,
                text=clause_body,
                metadata={
                    "source_doc": doc_name,
                    "clause_id": clause_id,
                    "section_title": section_title,
                },
            )
            chunks.append(chunk)

        return chunks
