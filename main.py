from lib.helperFunction import get_users, format_users, filter_users_born_on_or_before
from lib.llm import identify_batch
from lib.bonus import print_results, run_exercise_5_async
import asyncio


def print_name_list(names: list[str]) -> None:
    """Print names in the assessment example format (single-quoted list)."""
    if not names:
        print("[]")
        return
    print("[")
    for i, name in enumerate(names):
        suffix = "," if i < len(names) - 1 else ""
        print(f"  '{name}'{suffix}")
    print("]")


def main():
    try:
        print("🚀 Nationale-Nederlanden GenAI Engineer Assessment\n")

        # ── Exercise 1 ────────────────────────────────────────────
        users = get_users()
        print(f"✅ Exercise 1 - Fetched {len(users)} users")

        # ── Exercise 2 ────────────────────────────────────────────
        names = format_users(users)
        filtered_users = filter_users_born_on_or_before(users)
        filtered_out = len(users) - len(filtered_users)
        print(f"✅ Exercise 2 - Formatted names")
        print(
            f"📌 {len(names)} of {len(users)} users born in or before 2000 "
            f"({filtered_out} filtered out)\n"
        )
        print_name_list(names)

        # ── Exercise 4 ────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("🧠 EXERCISE 4 - LLM Identification Results")
        print("=" * 60 + "\n")

        enriched = identify_batch(filtered_users, limit=5, delay=1.3)

        for person in enriched:
            print(f"👤 {person['name']} ({person['nationality']}, b. {person['birth_year']})")
            print(f"   {person['info']}\n")

        # ── Exercise 5 ────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("🤖 EXERCISE 5 - LangChain Agent: Best Work")
        print("=" * 60 + "\n")

        works = asyncio.run(run_exercise_5_async(filtered_users, limit=5))

        # ── Bonus 1 ───────────────────────────────────────────────
        print_results(works)

    except Exception as e:
        print(f"❌ Failed: {e}")


if __name__ == "__main__":
    main()
