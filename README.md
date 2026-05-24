# Nationale-Nederlanden — GenAI Engineer Assessment

A Python project that fetches random user data, filters it, identifies public figures with a local LLM, and finds their best-known work using a LangChain agentic workflow.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| pip3 | latest |
| [Ollama](https://ollama.com) | latest |
| llama3.2 model | pulled via Ollama |

---

## Project Structure

```
.
├── main.py                  # Entry point — runs all 5 exercises
├── test_main.py             # Exercise 3: pytest test suite
├── requirements.txt         # Pinned dependencies
├── README.md
├── .env.local               # Local environment variables (not committed)
├── .gitignore
├── code/presentation/feedback/
│   ├── GenAI Engineer Assessment v2.html
│   └── GenAI Engineer Assessment v2.pdf   # export from HTML (Print → Save as PDF)
└── lib/
    ├── helperFunction.py    # Exercise 1 & 2: get_users, format_users, make_user
    ├── llm.py               # Exercise 4: identify_person, identify_batch (Ollama)
    ├── agent.py             # Exercise 5: LangChain/LangGraph agent, run_exercise_5
    └── bonus.py             # Bonus: print_results, run_exercise_5_async, caching, retry
```

---

## Setup

### 1. Clone / unzip the project

```bash
unzip nn-genai-assessment.zip
cd nn-genai-assessment
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Pull the LLM model via Ollama

```bash
ollama pull llama3.2
```

Make sure the Ollama server is running before executing the project:

```bash
ollama serve
```

> On macOS / Linux, Ollama typically auto-starts after installation. Run `ollama list` to confirm the model is available.

---

## Running the Project

```bash
python3 main.py
```

The script will:

1. **Exercise 1** — Fetch 20 random users from `randomuser.me`
2. **Exercise 2** — Format and filter names (born ≤ 2000)
3. **Exercise 4** — Identify 5 people (born ≤ 2000) using the local LLM (~1.3 s delay between calls)
4. **Exercise 5** — Run the LangChain agent on the same 5 filtered users (parallel async calls)
5. **Bonus 1** — Structured console output distinguishing public figures from private individuals

---

## Running Tests

```bash
python3 -m pytest test_main.py -v
```

All 10 tests pass:

| Test | What it covers |
|---|---|
| `test_returns_list` | `format_users` always returns a list |
| `test_correct_count` | Correct number of users filtered |
| `test_name_format` | Names are in `"First Last"` format |
| `test_filters_post_2000` | Users born after 2000 are excluded |
| `test_includes_year_2000_edge_case` | Year 2000 is included (boundary check) |
| `test_empty_response` | Empty input returns empty list |
| `test_all_post_2000` | All post-2000 users yields empty result |
| `test_names_are_strings` | All returned names are non-empty strings |
| `test_missing_results_key` | `get_users` raises `KeyError` when API response is malformed |
| `test_full_pipeline` | End-to-end: mocked HTTP → `get_users` → `format_users` |

> ⚠️ Two deprecation warnings appear at test time — these are from upstream libraries, not from this project:
> - `langchain-community` is being sunset; `DuckDuckGoSearchRun` will need to migrate to a standalone package in a future version.
> - `create_react_agent` has moved from `langgraph.prebuilt` in LangGraph v1.0 — however the import in `langchain.agents` does **not** exist in the currently installed version, so keep using `from langgraph.prebuilt import create_react_agent` until the standalone package is available.

---

## Bonus Features

### Bonus 1 — Better result presentation

Replace the loop in `main.py` with:

```python
from lib.bonus import print_results
print_results(works)
```

Public figures get a trophy emoji and full description; private individuals get a clear "no public records" line.

### Bonus 2 — Performance improvements

Three strategies are available in `lib/bonus.py`:

| Strategy | Function | Benefit |
|---|---|---|
| Async parallel | `run_exercise_5_async` | Cuts total time from `n × delay` to ~1 call duration |
| LRU cache | `get_best_work_cached` | Skips repeated LLM calls for the same name within a session |
| Retry + back-off | `get_best_work_with_retry` | Retries up to 3× (2s → 4s → 8s) on DuckDuckGo/Ollama failures |

Additional improvements applied in `lib/bonus.py`:

- `asyncio.get_running_loop()` replaces the deprecated `get_event_loop()` (Python 3.10+)
- Each async agent call is wrapped in try/except — one failure no longer kills the whole batch
- `before_sleep_log` on the retry decorator logs every retry attempt automatically
- `reraise=True` surfaces the real exception after all attempts are exhausted
- Structured `logging` replaces bare `print()` — timestamps and log levels included
- Empty input guards on `print_results` and `run_exercise_5_async`
- Safe `.get()` with defaults on dict access in `print_results`

To run the async version:

```python
import asyncio
from lib.bonus import run_exercise_5_async

works = asyncio.run(run_exercise_5_async(users, limit=5))
```

### Bonus 3 — Architecture flow

See slide 8 of the accompanying presentation:
[`code/presentation/feedback/GenAI Engineer Assessment v2.html`](code/presentation/feedback/GenAI%20Engineer%20Assessment%20v2.html)
(or the exported PDF in the same folder).

High-level flow:

```
randomuser.me API
      │
      ▼
get_users()  ──►  format_users()  ──►  identify_batch()  ──►  run_exercise_5()
(Exercise 1)      (Exercise 2)         (Exercise 4)           (Exercise 5)
                                       Ollama / llama3.2      LangChain + DuckDuckGo
                                                                    │
                                                                    ▼
                                                             print_results()
                                                             (Bonus 1)
```

### Bonus 4 — Best practices applied

- Type hints on every function
- Docstrings on every public function
- `raise_for_status()` on all HTTP calls
- `timeout=10` on `requests.get` to prevent hanging
- Input validation (`results` 1–5000) before hitting the API
- Rate-limit delay (`time.sleep`) between LLM calls
- `recursion_limit` cap on LangGraph agent (5 steps max)
- `NOT_NOTABLE` sentinel to prevent hallucination leaking through
- Name-match check to block wrong-person substitution
- `.env`-ready structure — never hardcode API keys
- `requirements.txt` with pinned versions
- Separation of concerns across modules: `helperFunction`, `llm`, `agent`, `bonus`
- Retry + exponential back-off via `tenacity` with `reraise=True` and `before_sleep_log`
- `lru_cache` for repeated lookups within a session
- `asyncio.gather` for parallel execution
- `asyncio.get_running_loop()` instead of deprecated `get_event_loop()`
- Structured `logging` instead of bare `print()` for observability
- Empty input guards and safe `.get()` dict access throughout

---

## Notes

- The `randomuser.me` API returns different users on each run, so Exercise 4/5 results will vary.
- Ollama must be running locally. The model is `llama3.2` — swap the model name in `lib/llm.py` and `lib/agent.py` if you use a different one.
- DuckDuckGo search (used in the LangChain agent) has rate limits. The `delay` parameter and the retry wrapper in `lib/bonus.py` mitigate this.
- The `NOT_NOTABLE` sentinel and name-match check in `lib/agent.py` prevent the LLM from substituting a similarly named celebrity for an unknown private individual.

### ⚠️ A note on hallucination with llama3.2

Through hands-on experience building this project, `llama3.2` showed a **notable tendency to hallucinate** — particularly in Exercise 4 and 5, where it would confidently substitute a well-known person for an unknown private individual with a similar name (e.g. inventing a biography for a random "James Wilson" by confusing them with a public figure).

Mitigations were applied (`NOT_NOTABLE` sentinel, name-match check, `temperature=0.1`), but they do not fully eliminate the problem with a local 3B model.

**For a production environment, `gpt-4o-mini` or `gpt-4o` via the OpenAI API is strongly recommended.** These models have significantly better instruction-following, are far less likely to confabulate identities, and handle the "unknown person → return not found" case much more reliably. The LangChain agent in `lib/agent.py` is already compatible — swapping the model is a one-line change:

```python
# Current (local, hallucination-prone)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2", temperature=0.1)

# Recommended (production-grade)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
```

Add your key to a `.env` file:

```
OPENAI_API_KEY=sk-...
```

---

## Assessment Reflection

**Difficulty:** Medium

**Time:** ~90 minutes is sufficient for exercises 1–5. The bonus section (especially async and retry) adds another 20–30 minutes if you implement all parts.

**What went well:**
- The `randomuser.me` API is simple and well-documented.
- LangChain's `create_react_agent` makes the agentic loop very concise.
- `tenacity` and `lru_cache` are drop-in improvements with minimal code.

**What required extra care:**
- Preventing LLM hallucination (substituting a famous person for an unknown name) needed both the `NOT_NOTABLE` sentinel in the system prompt and a post-hoc name-match check.
- DuckDuckGo rate limits make the agent brittle without the retry wrapper.