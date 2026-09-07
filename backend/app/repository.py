from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=None)
def load_data_file(filename: str) -> dict[str, Any]:
    with (DATA_DIRECTORY / filename).open(encoding="utf-8") as data_file:
        return json.load(data_file)
