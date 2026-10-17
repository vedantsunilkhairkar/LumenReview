"""Document loader for regulation files (txt, md, pdf)."""

from pathlib import Path

from app.core.logging import logger
from app.rag.chunker import ClauseAwareChunker, RegulationChunk


class RegulationLoader:
    def __init__(self, regulations_dir: Path | str | None = None):
        if regulations_dir is None:
            from app.core.config import settings

            self.regulations_dir = settings.regulations_dir
        else:
            self.regulations_dir = Path(regulations_dir)
        self.chunker = ClauseAwareChunker()

    def load_all(self) -> list[RegulationChunk]:
        """Load and chunk all regulation files in the regulations directory."""
        all_chunks: list[RegulationChunk] = []
        if not self.regulations_dir.exists():
            logger.warning("Regulations directory does not exist: %s", self.regulations_dir)
            return all_chunks

        for file_path in self.regulations_dir.glob("*.*"):
            if file_path.suffix.lower() in [".txt", ".md"]:
                chunks = self.load_text_file(file_path)
                all_chunks.extend(chunks)
            elif file_path.suffix.lower() == ".pdf":
                chunks = self.load_pdf_file(file_path)
                all_chunks.extend(chunks)

        logger.info("Loaded %d regulation chunks from %s", len(all_chunks), self.regulations_dir)
        return all_chunks

    def load_text_file(self, file_path: Path) -> list[RegulationChunk]:
        """Load and chunk a single text or markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            doc_name = file_path.stem.replace("_", " ").title()
            return self.chunker.chunk_text(content, default_doc_name=doc_name)
        except Exception as e:
            logger.error("Failed to load text file %s: %s", file_path, e)
            return []

    def load_pdf_file(self, file_path: Path) -> list[RegulationChunk]:
        """Load and chunk a PDF file using pypdf if installed, or fallback."""
        try:
            import pypdf

            reader = pypdf.PdfReader(str(file_path))
            full_text = []
            for page_num, page in enumerate(reader.pages, start=1):
                extracted = page.extract_text() or ""
                full_text.append(f"\n[PAGE: {page_num}]\n{extracted}")
            text_content = "\n".join(full_text)
            return self.chunker.chunk_text(text_content, default_doc_name=file_path.stem)
        except ImportError:
            logger.warning("pypdf not installed. Skipping PDF %s", file_path)
            return []
        except Exception as e:
            logger.error("Failed to parse PDF %s: %s", file_path, e)
            return []
