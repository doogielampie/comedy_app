import requests
import streamlit as st

# ---- Settings ----------------------------------------------------------
BUSINESS = "a stand-up comedy club"
LABELS = ["comedians", "show experience", "food & drinks", "tickets & price", "safety concern", "other"]
GUIDE = """Give each comment exactly one label from this list:

comedians: the performers or the material. Who was funny or not, the headliner, the host, jokes that offended or fell flat.
show experience: the room and how the show ran. Seating, sight lines, sound, start time, show length, crowd or heckler behavior that staff did not stop.
food & drinks: what they ate or drank and how it was served. Quality, slow servers, missing orders, the drink minimum.
tickets & price: paying and booking. Ticket price, fees, the booking site, refunds, cancellations, "not worth the money".
safety concern: someone was harmed or at risk. Harassment, threats, a fight, injury, getting sick from food, discrimination by staff.
other: does not fit above or is too vague to tell. "Fine.", questions, parking, unrelated topics.

Rules for hard cases:
- Praise and a complaint together: label by the complaint.
- More than one complaint: label by the one that hurt the night most.
- Sarcasm: label by the real meaning, not the literal words.
- Any hint of a safety problem wins over every other label, even if it is mentioned in passing.
- Pure praise: label by what they praised.

Answer with the label only, written exactly as in the list, and nothing else."""
MODEL = "openai/gpt-oss-20b"   # if you get a 404, the model was retired: see console.groq.com/docs/models
URL = "https://api.groq.com/openai/v1/chat/completions"
# ------------------------------------------------------------------------


def get_key():
    # The course notes use both spellings, so accept either one in Streamlit Secrets
    for name in ("GROQ_API_KEY", "GROQ-API-KEY"):
        if name in st.secrets:
            return st.secrets[name]
    raise KeyError("Add GROQ_API_KEY to the app's Secrets on Streamlit Cloud.")


def clean(answer):
    """Turn the model's answer into one of LABELS, or 'unclear'."""
    text = answer.strip().lower().strip(" .\"'*`:")
    text = text.replace(" and ", " & ")
    if text in LABELS:
        return text
    found = [label for label in LABELS if label in text]
    return found[0] if len(found) == 1 else "unclear"


def label_comment(text):
    prompt = f"You label customer comments for {BUSINESS}.\n\n{GUIDE}\n\nComment: {text}"
    response = requests.post(
        URL,
        headers={"Authorization": f"Bearer {get_key()}"},
        json={"model": MODEL, "temperature": 0,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    response.raise_for_status()
    return clean(response.json()["choices"][0]["message"]["content"])
