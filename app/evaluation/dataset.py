"""Dataset loader and validator for benchmark evaluation sets."""

import json
from pathlib import Path

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger


class EvalItem(BaseModel):
    req_id: str
    text: str
    expected_issues: list[str] = Field(default_factory=list)
    expected_clause_ids: list[str] = Field(default_factory=list)
    expected_severities: list[str] = Field(default_factory=list)
    notes: str = ""


class EvalDatasetLoader:
    def __init__(self, file_path: Path | str | None = None):
        if file_path is None:
            self.file_path = settings.eval_data_dir / "eval_set.jsonl"
        else:
            self.file_path = Path(file_path)

    def load(self) -> list[EvalItem]:
        """Load and validate evaluation items from JSONL file."""
        items: list[EvalItem] = []
        if not self.file_path.exists():
            logger.warning("Eval dataset file not found at: %s", self.file_path)
            return items

        with open(self.file_path, encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    data = json.loads(clean_line)
                    item = EvalItem(**data)
                    items.append(item)
                except Exception as e:
                    logger.error("Error parsing line %d of %s: %s", line_no, self.file_path, e)

        logger.info("Loaded %d evaluation items from %s", len(items), self.file_path)
        return items
