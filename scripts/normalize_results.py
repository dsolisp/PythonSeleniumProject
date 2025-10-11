"""
Backfill / normalize historical test result JSON files into a
pytest-json-report-like schema.
Creates `*_normalized.json` alongside original files to avoid overwriting.

Run with:
    venv-enhanced/bin/python scripts/normalize_results.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "data" / "results"


def normalize_custom_file(path: Path) -> Path:
    with Path.open(path) as f:
        try:
            data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            print(f"[SKIP] Unable to parse JSON: {path}")
            return None

    # Detect our custom format: top-level 'results' with 'tests'
    if (
        isinstance(data, dict)
        and "results" in data
        and isinstance(data["results"], dict)
        and "tests" in data["results"]
    ):
        norm = {}
        # created: try to use execution_time or timestamp fields if present, else now
        created = data.get("execution_time") or data.get("timestamp") or None
        if isinstance(created, str):
            # try parse iso or yyyymmdd
            try:
                # common ISO
                dt = datetime.fromisoformat(created)
                created_ts = dt.timestamp()
            except (ValueError, OSError):
                try:
                    created_ts = datetime.now(timezone.utc).timestamp()
                except OSError:
                    created_ts = None
        elif isinstance(created, (int, float)):
            created_ts = float(created)
        else:
            created_ts = datetime.now(timezone.utc).timestamp()

        norm["created"] = created_ts
        norm["duration"] = data.get("duration", 0)
        # environment: keep as-is (string or dict)
        norm["environment"] = data.get(
            "environment",
            data["results"].get("environment", "unknown"),
        )
        # metadata: map browser
        norm["metadata"] = {"Browser": data["results"].get("browser", "unknown")}

        norm_tests = []
        for t in data["results"].get("tests", []):
            outcome = t.get("status") or "unknown"
            duration = t.get("duration", 0)
            nodeid = t.get("name") or t.get("nodeid") or "unknown"
            entry = {
                "nodeid": nodeid,
                "outcome": outcome,
                "duration": duration,
                "call": {"duration": duration, "outcome": outcome},
            }
            norm_tests.append(entry)

        norm["tests"] = norm_tests

        # write normalized file
        dest = path.with_name(path.stem + "_normalized.json")
        with Path.open(dest, "w") as df:
            json.dump(norm, df, indent=2)
        return dest

    # If file already looks like pytest-json-report
    # (has 'tests' list of dicts with nodeid)
    if (
        isinstance(data, dict)
        and "tests" in data
        and isinstance(data["tests"], list)
        and any(isinstance(x, dict) and "nodeid" in x for x in data["tests"][:5])
    ):
        # Already ok — skip
        return None

    # Not a recognized format
    return None


def main():
    print(f"Scanning {RESULTS_DIR} for JSON result files...")
    if not RESULTS_DIR.exists():
        print("No results dir; nothing to do")
        return

    json_files = list(RESULTS_DIR.rglob("*.json"))
    if not json_files:
        print("No JSON files found")
        return

    converted = []
    for jf in json_files:
        # skip already normalized files
        if jf.name.endswith("_normalized.json"):
            continue
        dest = normalize_custom_file(jf)
        if dest:
            converted.append((jf, dest))
            print(f"Converted {jf} -> {dest}")

    print(f"Done. Converted {len(converted)} files.")


if __name__ == "__main__":
    main()
