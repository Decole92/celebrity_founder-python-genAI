import time
import ollama

# SYSTEM_PROMPT = """You are a researcher with access only to your training data.
# Given a name, nationality, and birth year:
# - If you have CERTAIN knowledge this is a real notable public figure, describe them in 1-2 sentences.
# - If you are not 100% certain, you MUST respond exactly with:
#   'No notable public figure found for this name.'
# Do NOT guess. Do NOT invent details. When in doubt, say not found."""

SYSTEM_PROMPT = """You are a strict fact-checker. Rules you must never break:
1. Search for the EXACT name given to you.
2. If search results show a DIFFERENT person, return NOT_NOTABLE immediately.
3. If you are not 100% certain the result matches the exact name, return NOT_NOTABLE.
4. Never substitute, guess, or find a similar name.
5. Return NOT_NOTABLE when in doubt.
Only describe someone if search results confirm their exact name."""

def identify_person(name: str, nationality: str, year: int) -> str:
    prompt = (
        f"Name: {name}\n"
        f"Nationality: {nationality}\n"
        f"Birth year: {year}"   
    )
  

    response = ollama.chat(
    model="llama3.2",         # ← swap this
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ],
    options={"temperature": 0.1, "num_predict": 150}
 
    )
    content = response['message']['content'].strip() 
    if content == "NOT_NOTABLE" or "notable" not in content.lower():
        return "NOT_NOTABLE — private individual, no public records found."
    return content



def identify_batch(users: list, limit: int = 5, delay: float = 1.5) -> list:
    results = []
    for user in users[:limit]:
        name  = f"{user['name']['first']} {user['name']['last']}"
        nat   = user["nat"]
        year  = user["dob"]["date"][:4]  # ← extract year from "1973-11-08T..." 
        info  = identify_person(name, nat, int(year))
        results.append({
            "name":        name,
            "nationality": nat,    # ← add this
            "birth_year":  year,   # ← add this
            "info":        info
        })
        time.sleep(delay)
    return results