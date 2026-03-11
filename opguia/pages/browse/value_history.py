"""Value history — ring buffer of timestamped values for watched variables.

Accumulates numeric readings over time, shared between the watch panel
polling loop and the graph panel for rendering.
"""

import time
from collections import deque


# Max data points per variable
MAX_POINTS = 500


class ValueHistory:
    """Stores time-series data for watched variables."""

    def __init__(self, max_points: int = MAX_POINTS):
        self._max = max_points
        # {node_id: deque of [timestamp_ms, value]}
        self._data: dict[str, deque] = {}

    def record(self, node_id: str, value) -> bool:
        """Record a value reading. Returns True if numeric (graphable)."""
        if not isinstance(value, (int, float, bool)):
            return False
        now = time.time() * 1000  # ECharts expects ms
        if node_id not in self._data:
            self._data[node_id] = deque(maxlen=self._max)
        self._data[node_id].append([now, float(value)])
        return True

    def get(self, node_id: str) -> list:
        """Get all recorded points for a node as a list."""
        if node_id in self._data:
            return list(self._data[node_id])
        return []

    def remove(self, node_id: str):
        """Remove history for a node."""
        self._data.pop(node_id, None)

    def clear(self):
        """Clear all history."""
        self._data.clear()

    @property
    def node_ids(self) -> set[str]:
        return set(self._data.keys())
