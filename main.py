from lib.helperFunction import get_users, format_users
from lib.llm import identify_batch
from lib.agent import run_exercise_5
from lib.bonus import (
    print_results,           # BONUS 1 — better output formatting
    run_exercise_5_async,    # BONUS 2 — async parallel calls
    get_best_work_cached,    # BONUS 2 — caching
    get_best_work_with_retry # BONUS 2 — retry with back-off
)
import json
import asyncio


def main():
    try:
        print("🚀 Nationale-Nederlanden GenAI Engineer Assessment\n")

        # ── Exercise 1 ────────────────────────────────────────────
        users = get_users()
        print(f"✅ Exercise 1 - Fetched {len(users)} users")

        # ── Exercise 2 ────────────────────────────────────────────
        names = format_users(users)
        filtered_out = len(users) - len(names)
        print(f"✅ Exercise 2 - Formatted names")
        print(f"📌 {len(names)} of {len(users)} users born in or before 2000 ({filtered_out} filtered out)\n")
        print(json.dumps(names, indent=2, ensure_ascii=False))

        # ── Exercise 4 ────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("🧠 EXERCISE 4 - LLM Identification Results")
        print("=" * 60 + "\n")

        enriched = identify_batch(users, limit=5, delay=1.3)

        for person in enriched:
            print(f"👤 {person['name']} ({person['nationality']}, b. {person['birth_year']})")
            print(f"   {person['info']}\n")

        # ── Exercise 5 ────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("🤖 EXERCISE 5 - LangChain Agent: Best Work")
        print("=" * 60 + "\n")

        # BONUS 2a — async parallel execution (faster than sequential)
        # Runs all agent calls concurrently instead of one by one.
        # Swap this for run_exercise_5(users, limit=5) to go back to sequential.
        works = asyncio.run(run_exercise_5_async(users, limit=5))

        # BONUS 2b — cached lookup example
        # If the same name appears again later in the session,
        # get_best_work_cached returns instantly without hitting the LLM.
        # Example: get_best_work_cached("Marie Curie")

        # BONUS 2c — retry with exponential back-off example
        # Use get_best_work_with_retry("name") anywhere instead of get_best_work("name")
        # to automatically retry up to 3 times on DuckDuckGo or Ollama failures.
        # Example: get_best_work_with_retry("Alan Turing")

        # BONUS 1 — structured output (public figures vs private individuals)
        print_results(works)

    except Exception as e:
        print(f"❌ Failed: {e}")


if __name__ == "__main__":
    main()