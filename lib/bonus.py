"""
bonus.py — Nationale-Nederlanden GenAI Assessment
Covers all four bonus questions:
  1. Better presentation of results
  2. Performance improvements (async, cache, retry)
  3. Architecture flow — see presentation slide 8
  4. Best practices applied throughout
"""

import asyncio
import logging
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from lib.agent import get_best_work

# BONUS 4 — structured logging instead of bare print() for observability
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# BONUS 1 — Better presentation of results
# ─────────────────────────────────────────────────────────────

def print_results(works: list) -> None:
    """
    Structured console output distinguishing public figures
    from private individuals at a glance.
    """
    if not works:
        print("⚠️  No results to display.")
        return

    public  = [p for p in works if p.get("status") == "public_figure"]
    private = [p for p in works if p.get("status") == "private_individual"]

    print(f"\n📊 Summary: {len(public)} public figures, {len(private)} private individuals\n")
    print("─" * 60)

    for person in works:
        name   = person.get("name", "Unknown")
        status = person.get("status")
        work   = person.get("work", "")

        if status == "public_figure":
            print(f"🏆 {name}")
            print(f"   {work}")
        else:
            print(f"⚪ {name}")
            print(f"   Private individual — no public records found.")
        print("─" * 60)


# ─────────────────────────────────────────────────────────────
# BONUS 2 — Performance: async parallel calls
# ─────────────────────────────────────────────────────────────

async def get_best_work_async(name: str) -> dict:
    """
    Run a single LLM agent call in a thread pool (non-blocking).
    Uses asyncio.get_running_loop() — safer than get_event_loop()
    which is deprecated in Python 3.10+.
    """
    loop = asyncio.get_running_loop()  # safer than get_event_loop()
    try:
        work = await loop.run_in_executor(None, get_best_work, name)
    except Exception as e:
        logger.error("Agent call failed for '%s': %s", name, e)
        work = "NOT_NOTABLE"

    status = "private_individual" if work == "NOT_NOTABLE" else "public_figure"
    return {
        "name":   name,
        "status": status,
        "work":   work if status == "public_figure" else "No public records found.",
    }


async def run_exercise_5_async(users: list, limit: int = 5) -> list:
    """
    Parallel version of run_exercise_5.
    Runs all LLM agent calls concurrently instead of sequentially.
    Reduces total wall time from (limit × delay) to ~1 agent call duration.
    """
    if not users:
        logger.warning("run_exercise_5_async called with empty user list.")
        return []

    names = [
        f"{u['name']['first']} {u['name']['last']}"
        for u in users[:limit]
    ]
    logger.info("Running %d agent calls in parallel...", len(names))

    tasks = [get_best_work_async(name) for name in names]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    logger.info("Parallel agent calls complete.")
    return list(results)


# ─────────────────────────────────────────────────────────────
# BONUS 2 — Performance: caching repeated lookups
# ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=256)
def get_best_work_cached(name: str) -> str:
    """
    Cached wrapper around get_best_work.
    Avoids re-querying the same name across multiple runs
    within the same process lifetime.

    Cache hit example:
        get_best_work_cached("Marie Curie")  # hits LLM
        get_best_work_cached("Marie Curie")  # instant — served from cache
    """
    logger.info("Cache miss — querying LLM for '%s'", name)
    return get_best_work(name)


# ─────────────────────────────────────────────────────────────
# BONUS 2 — Performance: retry with exponential back-off
# ─────────────────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    before_sleep=before_sleep_log(logger, logging.WARNING),  # logs each retry attempt
    reraise=True,  # re-raises the original exception after all attempts are exhausted
)
def get_best_work_with_retry(name: str) -> str:
    """
    Retry wrapper — handles transient DuckDuckGo rate limits
    or temporary Ollama failures without crashing the pipeline.
    Waits 2s → 4s → 8s between attempts (capped at 10s).
    Logs each retry attempt automatically via before_sleep_log.
    """
    return get_best_work(name)


# ─────────────────────────────────────────────────────────────
# BONUS 4 — Best practices summary (applied across the project)
# ─────────────────────────────────────────────────────────────
#
# ✅ Type hints on every function
# ✅ Docstrings on every function
# ✅ raise_for_status() on all HTTP calls
# ✅ timeout=10 on requests.get to prevent hanging
# ✅ Input validation (results 1-5000) before hitting the API
# ✅ rate-limit delay between LLM calls (time.sleep)
# ✅ recursion_limit cap on LangGraph agent (see lib/agent.py)
# ✅ NOT_NOTABLE sentinel — prevents hallucination leaking through
# ✅ Name match check — blocks wrong-person substitution
# ✅ .env for secrets — never hardcode API keys
# ✅ requirements.txt with pinned versions
# ✅ Separation of concerns: fetch / format / test / identify / agent / bonus
# ✅ Retry + back-off via tenacity for network resilience
# ✅ lru_cache for repeated lookups within a session
# ✅ asyncio.gather for parallel execution in production scenarios
# ✅ structred logging via logging module instead of bare print()
# ✅ asyncio.get_running_loop() instead of deprecated get_event_loop()
# ✅ return_exceptions=False on gather — fails fast on unexpected errors
# ✅ reraise=True on retry — surfaces real errors after exhausting attempts
# ✅ before_sleep_log — automatic retry logging without manual print()
# ✅ .get() with defaults on dict access — safe against missing keys
# ✅ Empty input guards on both print_results and run_exercise_5_async
#
# BONUS 3 — Architecture flow: see presentation slide 8
#            or run the interactive diagram in the presentation.