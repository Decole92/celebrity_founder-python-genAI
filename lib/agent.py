import time
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent


llm = ChatOllama(
    model="llama3.2",
    temperature=0.1,
    num_predict=150,
)

search_tool = DuckDuckGoSearchRun()

# SYSTEM = """You are a strict research assistant.
# Given a person's full name, search for them and summarise their single
# most acclaimed work or achievement in 2-3 sentences.

# STRICT RULES:
# - Only describe the EXACT person named, never a similar or related person.
# - If the search results are about a different person, respond with NOT_NOTABLE.
# - If no notable public figure exists with that exact name, respond with NOT_NOTABLE.
# - Never guess, infer, or substitute a different person.
# - Respond with NOT_NOTABLE when in doubt."""


SYSTEM_PROMPT = """You are a strict fact-checker. Rules you must never break:
1. Search for the EXACT name given to you.
2. If search results show a DIFFERENT person, return NOT_NOTABLE immediately.
3. If you are not 100% certain the result matches the exact name, return NOT_NOTABLE.
4. Never substitute, guess, or find a similar name.
5. Return NOT_NOTABLE when in doubt.
Only describe someone if search results confirm their exact name."""

AGENT_RECURSION_LIMIT = 5

agent_executor = create_react_agent(
    model=llm,
    tools=[search_tool],
    prompt=SYSTEM_PROMPT,
)


def names_match(query: str, response: str) -> bool:
    """Check if the queried name appears in the response."""
    first, last = query.lower().split()[0], query.lower().split()[-1]
    response_lower = response.lower()
    return first in response_lower and last in response_lower


def get_best_work(name: str) -> str:
    try:
        result = agent_executor.invoke(
            {
                "messages": [
                    ("human", f"Who is {name} and what is their most acclaimed work or achievement?")
                ]
            },
            config={"recursion_limit": AGENT_RECURSION_LIMIT},
        )
        output = result["messages"][-1].content

        if "NOT_NOTABLE" in output:
            return "NOT_NOTABLE"

        # reject if the response is about a different person
        if not names_match(name, output):
            return "NOT_NOTABLE"

        return output
    except Exception as e:
        return f"Error: {str(e)}"


def run_exercise_5(users: list, limit: int = 5, delay: float = 2.0) -> list:
    results = []
    for user in users[:limit]:
        name = f"{user['name']['first']} {user['name']['last']}"
        work = get_best_work(name)

        if work.strip() == "NOT_NOTABLE":
            results.append({
                "name":   name,
                "status": "private_individual",
                "work":   "No public records found."
            })
        else:
            results.append({
                "name":   name,
                "status": "public_figure",
                "work":   work
            })

        time.sleep(delay)
    return results