"""Intentionally flaky concurrent test — material for ci_watchdog triage.

The test races against a ThreadPoolExecutor and a `time.sleep`. Under CI
load (shared runners, noisy neighbours) the assertion order breaks roughly
10-30% of the time. This is NOT a real bug in production code; it's a bug
in the test itself.

Expected ci_watchdog behaviour:
  1. Observe a failed run of this test.
  2. Re-run with `gh run rerun --failed`; notice the second run passes.
  3. Pull runs across the last ~20 attempts; compute fail-rate.
  4. Post [CI-DIAG] tagged 'flaky' with repro signature + recommended fix
     (use a synchronization primitive, not sleep).
"""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest


def _append_after_delay(output: list[int], value: int, delay: float) -> None:
    time.sleep(delay)
    output.append(value)


@pytest.mark.flaky
def test_append_order_race():
    """Supposed to verify 1 lands before 2 — races ~20% on shared runners."""
    out: list[int] = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        # Intended: value 1 (delay 0.01s) should append before value 2 (delay 0.03s).
        # Reality: on busy CPUs the 0.01s thread gets preempted and the order flips.
        f2 = ex.submit(_append_after_delay, out, 2, 0.03)
        f1 = ex.submit(_append_after_delay, out, 1, 0.01)
        f1.result()
        f2.result()
    assert out == [1, 2]


def test_sleep_budget_reasonable():
    """Non-flaky guard so the suite isn't 100% flaky."""
    start = time.time()
    time.sleep(0.01)
    assert time.time() - start < 0.5
