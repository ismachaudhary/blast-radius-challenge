"""Safe baseline optimizer for the RWX Blast Radius challenge.

Runs every test to avoid missed-test penalties, then chooses the number
of workers (1..8) with the lowest estimated cost:
busiest worker runtime + 2 seconds per worker.
"""

import json
import sys
from pathlib import Path

DATA = Path("/data")
MAX_WORKERS = 8


def split(tests, worker_count):
    workers = [[] for _ in range(worker_count)]
    loads = [0.0] * worker_count

    for test in sorted(tests, key=lambda item: item["seconds"], reverse=True):
        worker_index = min(range(worker_count), key=lambda index: loads[index])
        workers[worker_index].append(test["number"])
        loads[worker_index] += test["seconds"]

    return workers, max(loads, default=0.0)


def best_split(tests):
    best_workers = [[]]
    best_cost = float("inf")

    for count in range(1, MAX_WORKERS + 1):
        workers, busiest_time = split(tests, count)
        estimated_cost = busiest_time + 2.0 * count
        if estimated_cost < best_cost:
            best_cost = estimated_cost
            best_workers = workers

    return best_workers, best_cost


def main():
    tests = json.loads((DATA / "tests.json").read_text())["tests"]
    workers, estimated_cost = best_split(tests)

    for patch in sorted((DATA / "commits").glob("*.patch")):
        print(json.dumps({"commit": patch.stem, "workers": workers}))

    print(
        f"selected all {len(tests)} tests using {len(workers)} workers; "
        f"estimated per-commit cost {estimated_cost:.3f}s",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
