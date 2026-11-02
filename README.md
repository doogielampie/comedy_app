# The Punchline Room: comedy club feedback app

**Business question:** What part of a night at our club most often ruins it for customers, so I know what to fix first?

## Labels (exactly one per comment)
- **comedians**: the performers or the material. Who was funny or not, the headliner, the host, jokes that offended or fell flat.
- **show experience**: the room and how the show ran. Seating, sight lines, sound, start time, show length, crowd or heckler behavior that staff did not stop.
- **food & drinks**: what they ate or drank and how it was served. Quality, slow servers, missing orders, the drink minimum.
- **tickets & price**: paying and booking. Ticket price, fees, the booking site, refunds, cancellations, "not worth the money."
- **safety concern**: someone was harmed or at risk. Harassment, threats, a fight, injury, getting sick from food, discrimination by staff. Always sent to manual review.
- **other**: does not fit above or is too vague to tell. "Fine.", questions, parking, unrelated topics.

Rules for hard cases: praise plus a complaint is labeled by the complaint; with several complaints, the one that hurt the night most; sarcasm by its real meaning; any hint of safety wins; pure praise by what was praised.

## How the app works
- **Customer tab:** a star rating, a comment, or both (at least one). Comments are labeled by an LLM (Groq, `openai/gpt-oss-20b`). A rating with no comment is saved as `no comment` without calling the LLM.
- **Owner tab:** feedback received, average stars, needs manual review; a chart of bad nights (1–2 stars) by label and a chart of average stars by label; every comment that needs manual review, shown in full.
- **Needs manual review:** `safety concern`, `unclear` (the model's answer was not a valid label, or the call failed), and 1–2 star comments labeled `other`.

## Deploy
1. Upload these files to a **public** GitHub repo (no `feedback.csv`, no key).
2. On share.streamlit.io, create an app from the repo with main file `app.py`.
3. Under Advanced settings → Secrets, add: `GROQ_API_KEY = "your-key"`
4. `demo_comments.csv` has 20 sample comments to type in for testing.
