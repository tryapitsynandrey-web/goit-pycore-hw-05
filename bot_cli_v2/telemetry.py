from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def _telemetry_path(base_dir: Path) -> Path:
    return base_dir / "telemetry.json"


def record_command(base_dir: Path, command: str) -> None:
    p = _telemetry_path(base_dir)
    data: Dict[str, int] = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    data[command] = data.get(command, 0) + 1

    try:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # телеметрія не повинна ламати додаток
        pass
