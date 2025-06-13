import streamlit as st
from dotenv import load_dotenv
import os
import psycopg
import pandas as pd
import altair as alt

# Load environment variables
load_dotenv()

# --- Database fetching functions ---

def get_api_data():
    dbconn = st.secrets["DBCONN"]
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()
    cur.execute('SELECT * FROM api_data;')
    data = cur.fetchall()
    colnames = [desc.name for desc in cur.description]
    cur.close()
    conn.close()
    return pd.DataFrame(data, columns=colnames)

def get_article_data():
    dbconn = st.secrets["DBCONN"]
    if dbconn is None:
        raise ValueError("❌ Environment variable 'DBCONN' not found.")
    try:
        conn = psycopg.connect(dbconn)
        cur = conn.cursor()
        cur.execute('SELECT * FROM article_data;')
        data = cur.fetchall()
        colnames = [desc.name for desc in cur.description]
        cur.close()
        conn.close()
        return pd.DataFrame(data, columns=colnames)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to fetch article data: {e}")

# --- Streamlit UI ---

st.title("📊 Bitcoin Dashboard")
st.markdown("This dashboard shows daily Bitcoin closing prices and the latest crypto-related articles from u.today.")

# --- Bitcoin Price Data Section ---

try:
    api_data = get_api_data()
    st.success("✅ Price data loaded successfully!")

    st.subheader("📈 Bitcoin Price Data")
    api_data["date"] = pd.to_datetime(api_data["date"])

    # Date filter
    min_date = api_data["date"].min().date()
    max_date = api_data["date"].max().date()
    start_date, end_date = st.date_input("Filter by date range:", [min_date, max_date])

    if start_date and end_date:
        mask = (api_data["date"].dt.date >= start_date) & (api_data["date"].dt.date <= end_date)
        filtered_data = api_data[mask]
    else:
        filtered_data = api_data

    st.dataframe(filtered_data, use_container_width=True)

    # Line chart
    line_chart = alt.Chart(filtered_data).mark_line(color='orange').encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('close:Q', title='Closing Price (€)'),
        tooltip=['date:T', 'close:Q']
    ).properties(
        title="Bitcoin Closing Prices Over Time",
        width=700,
        height=400
    ).interactive()

    st.altair_chart(line_chart)

except Exception as e:
    st.error(f"❌ Failed to load price data: {e}")

# --- Article Data Section ---

st.header("📰 Latest Bitcoin News")
try:
    article_data = get_article_data()

    if 'date' in article_data.columns:
        article_data['date'] = pd.to_datetime(article_data['date'])

    st.subheader("🧰 Filter Articles")

    # Author filter
    if 'author' in article_data.columns:
        authors = article_data['author'].dropna().unique()
        selected_author = st.selectbox("Filter by author", options=["All"] + sorted(authors.tolist()))
    else:
        selected_author = "All"

    # Date filter
    if 'date' in article_data.columns:
        min_date = article_data['date'].min().date()
        max_date = article_data['date'].max().date()
        start_date, end_date = st.date_input("Filter by publication date", [min_date, max_date])
    else:
        start_date = end_date = None

    # Search bar
    search_term = st.text_input("🔍 Search articles")

    # --- Filtering Logic ---
    filtered_articles = article_data.copy()

    if selected_author != "All":
        filtered_articles = filtered_articles[filtered_articles['author'] == selected_author]

    if start_date and end_date:
        filtered_articles = filtered_articles[
            (filtered_articles['date'].dt.date >= start_date) &
            (filtered_articles['date'].dt.date <= end_date)
        ]

    if search_term:
        filtered_articles = filtered_articles[
            filtered_articles.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        ]

    # --- Display articles with bookmark option ---
    st.markdown("### 📰 Filtered Articles")

    for i, row in filtered_articles.iterrows():
        st.markdown(f"""
        **{row['title']}**  
        *By {row['author']} on {row['date'].strftime('%d %b %Y')}*  
        [🔗 Read more]({row['link']})
        """)
        
        # Bookmark checkbox
        if st.checkbox("📌 Bookmark", key=f"bookmark_{i}"):
            if "saved_articles" not in st.session_state:
                st.session_state["saved_articles"] = []
            # Avoid duplicate saves
            if not any(row['title'] == a['title'] for a in st.session_state["saved_articles"]):
                st.session_state["saved_articles"].append(row)

        st.markdown("---")

except Exception as e:
    st.error(f"❌ Failed to load articles: {e}")

# --- Bookmarked Articles Section ---

if "saved_articles" in st.session_state and st.session_state["saved_articles"]:
    st.header("📚 Bookmarked Articles")
    for article in st.session_state["saved_articles"]:
        st.markdown(f"- [{article['title']}]({article['link']}) by {article['author']}")
