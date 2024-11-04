from dataclasses import dataclass
from typing import List, Dict


@dataclass
class DuplicateInfo:
    name: str
    count: int
    items: List[Dict]