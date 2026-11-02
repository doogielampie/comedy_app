import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from labeler import LABELS, label_comment

# ---- Settings ----------------------------------------------------------
TITLE = "The Punchline Room"
QUESTION = ("What part of a night at our club most often ruins it for customers, "
            "so I know what to fix first?")
LOW_RATING = 2                      # 2 stars or fewer is a bad night
CSV_FILE = "feedback.csv"
COLUMNS = ["time", "comment", "rating", "label"]
ORDER = LABELS + ["unclear"]        # chart order; "no comment" rows are left out of the charts
COLORS = {"comedians": "#7B3FA0", "show experience": "#2F6DB5", "food & drinks": "#D98A1E",
          "tickets & price": "#2BA37A", "safety concern": "#C0392B", "other": "#8C8C8C",
          "unclear": "#CFCFCF"}
# ------------------------------------------------------------------------

st.set_page_config(page_title=TITLE, page_icon="🎤", layout="wide")
st.title(f"🎤 {TITLE}")
st.caption("Customers leave feedback after the show. An LLM labels each comment. The owner sees what to fix.")

# Load the saved feedback, or start with an empty table
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=COLUMNS)


def escape(text):
    """Show a comment exactly as typed (no markdown, and $ signs don't turn into math)."""
    for ch in "\\`*_{}[]()#+-!|$<>~":
        text = text.replace(ch, "\\" + ch)
    return text


def needs_review(data):
    """Comments the owner should read: safety concerns, labels the model could not give,
    and bad nights (1-2 stars) that only fit 'other'."""
    return (data["label"].isin(["safety concern", "unclear"])
            | ((data["label"] == "other") & (data["rating"] <= LOW_RATING)))


tab_customer, tab_owner = st.tabs(["Customer: tell us about your night", "Owner: what should I fix?"])

# ---- Customer side ----------------------------------------------------------
with tab_customer:
    st.subheader("How was the show?")
    st.write("Leave a star rating, a comment, or both.")
    with st.form("feedback_form", clear_on_submit=True):
        stars = st.feedback("stars")          # None until clicked, then 0 to 4
        comment = st.text_area("Your comment (optional)")
        submitted = st.form_submit_button("Send feedback")

    if submitted:
        comment = comment.strip()
        if not comment and stars is None:
            st.error("Please choose a star rating or write a comment.")
        else:
            if comment:
                try:
                    label = label_comment(comment)
                except Exception as error:      # never lose the customer's feedback
                    label = "unclear"
                    st.caption(f"(Labeling failed, saved for manual review: {error})")
            else:
                label = "no comment"
            new_row = pd.DataFrame([{"time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                     "comment": comment,
                                     "rating": None if stars is None else stars + 1,
                                     "label": label}])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("Thanks for coming out, and for your feedback!")
            if comment:
                st.caption(f"Behind the scenes, the app labeled it: {label}")

# ---- Owner side -------------------------------------------------------------
with tab_owner:
    st.subheader("What should I fix first?")
    st.caption(f"Business question: {QUESTION}")

    if df.empty:
        st.info("No feedback yet. Switch to the customer tab and add the first one.")
    else:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        df["comment"] = df["comment"].fillna("")
        flag = needs_review(df)
        rated = df["rating"].dropna()

        m1, m2, m3 = st.columns(3)
        m1.metric("Feedback received", len(df))
        m2.metric("Average stars", f"{rated.mean():.1f}" if len(rated) else "–")
        m3.metric("Needs manual review", int(flag.sum()))

        comments = df[df["label"] != "no comment"]
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Bad nights (1–2 stars) by what went wrong**")
            bad = comments[comments["rating"] <= LOW_RATING]
            counts = (bad["label"].value_counts().reindex(ORDER, fill_value=0)
                      .rename_axis("label").reset_index(name="count"))
            counts = counts[counts["count"] > 0].sort_values("count", ascending=False)
            if counts.empty:
                st.caption("No 1–2 star comments yet.")
            else:
                fig = px.bar(counts, x="count", y="label", orientation="h", color="label",
                             text="count", color_discrete_map=COLORS)
                fig.update_layout(showlegend=False, xaxis_title="Comments", yaxis_title=None,
                                  yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, width="stretch")
                top = counts.iloc[0]["label"]
                st.caption(f"Most common reason for a bad night so far: **{top}**")

        with col2:
            st.markdown("**Average stars by label**")
            avg = (comments.dropna(subset=["rating"]).groupby("label")["rating"]
                   .agg(["mean", "count"]).reindex(ORDER).dropna().reset_index())
            if avg.empty:
                st.caption("No rated comments yet.")
            else:
                avg["mean"] = avg["mean"].round(1)
                fig = px.bar(avg, x="label", y="mean", color="label", text="mean",
                             color_discrete_map=COLORS, range_y=[0, 5],
                             hover_data={"count": True})
                fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Average stars")
                st.plotly_chart(fig, width="stretch")

        st.subheader(f"Needs manual review ({int(flag.sum())})")
        st.caption("Safety concerns, comments the model could not label, "
                   "and 1–2 star comments that only fit 'other'.")
        review = df[flag].iloc[::-1]          # newest first
        if review.empty:
            st.success("Nothing to review right now.")
        for _, row in review.iterrows():
            with st.container(border=True):
                stars_text = "no rating" if pd.isna(row["rating"]) else "★" * int(row["rating"])
                st.markdown(f"**{row['label']}** · {stars_text} · {row['time']}")
                st.markdown(escape(row["comment"]))

        with st.expander("All feedback"):
            st.dataframe(df, hide_index=True, width="stretch")
        st.download_button("Download CSV", df.to_csv(index=False), file_name="feedback.csv")
        st.caption("On free Streamlit Cloud, saved feedback can disappear when the app restarts. "
                   "Download the CSV to keep it.")
