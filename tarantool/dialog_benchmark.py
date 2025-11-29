"""Compare a dialog module before/after moving logic into Tarantool UDFs."""
from __future__ import annotations

import argparse
import sqlite3
import statistics
import time
from dataclasses import dataclass
from typing import Iterable, List

import tarantool

DB_PATH = "/tmp/dialogs.sqlite3"


class SQLiteDialogStore:
    """Simple baseline using a local SQL database."""

    def __init__(self) -> None:
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dialogs (
                dialog_id INTEGER NOT NULL,
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_message(self, dialog_id: int, author: str, body: str) -> None:
        self.conn.execute(
            "INSERT INTO dialogs(dialog_id, author, body, created_at) VALUES (?, ?, ?, ?)",
            (dialog_id, author, body, time.time()),
        )

    def get_dialog(self, dialog_id: int, limit: int) -> List[tuple]:
        cur = self.conn.execute(
            "SELECT dialog_id, message_id, author, body, created_at FROM dialogs "
            "WHERE dialog_id = ? ORDER BY message_id LIMIT ?",
            (dialog_id, limit),
        )
        return cur.fetchall()

    def cleanup(self) -> None:
        self.conn.commit()
        self.conn.close()


class TarantoolDialogStore:
    """Uses stored procedures defined in dialog_app.lua."""

    def __init__(self, host: str, port: int, user: str, password: str) -> None:
        self.conn = tarantool.Connection(host, port, user=user, password=password)

    def add_message(self, dialog_id: int, author: str, body: str) -> None:
        self.conn.call("add_message", [dialog_id, author, body])

    def get_dialog(self, dialog_id: int, limit: int) -> Iterable:
        return self.conn.call("get_dialog", [dialog_id, limit]).data[0]

    def cleanup(self) -> None:
        self.conn.close()


@dataclass
class BenchmarkResult:
    name: str
    write_qps: float
    read_qps: float
    p50_latency_ms: float


def run_benchmark(store, messages: int, reads: int, dialog_id: int = 1) -> BenchmarkResult:
    latencies: List[float] = []

    start = time.perf_counter()
    for i in range(messages):
        t0 = time.perf_counter()
        store.add_message(dialog_id, f"user-{i % 4}", f"hello #{i}")
        latencies.append((time.perf_counter() - t0) * 1000)
    write_elapsed = time.perf_counter() - start

    read_start = time.perf_counter()
    for _ in range(reads):
        store.get_dialog(dialog_id, 50)
    read_elapsed = time.perf_counter() - read_start

    store.cleanup()

    write_qps = messages / write_elapsed
    read_qps = reads / read_elapsed if read_elapsed else 0
    p50 = statistics.median(latencies)

    return BenchmarkResult(
        name=store.__class__.__name__,
        write_qps=write_qps,
        read_qps=read_qps,
        p50_latency_ms=p50,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Tarantool host")
    parser.add_argument("--port", type=int, default=3301, help="Tarantool port")
    parser.add_argument("--messages", type=int, default=2000, help="Messages to write")
    parser.add_argument("--reads", type=int, default=200, help="Dialog fetches to measure")
    parser.add_argument("--user", default="app", help="Tarantool user")
    parser.add_argument("--password", default="pass", help="Tarantool password")
    args = parser.parse_args()

    baseline = run_benchmark(SQLiteDialogStore(), messages=args.messages, reads=args.reads)
    migrated = run_benchmark(
        TarantoolDialogStore(args.host, args.port, args.user, args.password),
        messages=args.messages,
        reads=args.reads,
    )

    print("\nDialog module benchmark")
    print("=======================")
    for result in (baseline, migrated):
        print(
            f"{result.name:24} write_qps={result.write_qps:8.1f} "
            f"read_qps={result.read_qps:8.1f} p50={result.p50_latency_ms:.3f}ms"
        )

    gain = migrated.write_qps / baseline.write_qps if baseline.write_qps else 0
    print(f"\nMigration speed-up (writes): ×{gain:.2f}")


if __name__ == "__main__":
    main()
