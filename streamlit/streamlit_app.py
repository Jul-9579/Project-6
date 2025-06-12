import streamlit as st
from dotenv import load_dotenv
import os
import psycopg
import pandas as pd
import altair as alt  # Only import once, globally

# Set page config FIRST
st.set_page_config(page_title="Bitcoin Dashboard", layout="centered")

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

# if st.button("🔄 Refresh Data"):
#     st.rerun()

# --- Price Data Section ---

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

    # Line chart (cleaned up, no legend)
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

    # Search functionality
    search_term = st.text_input("🔍 Search articles")
    if search_term:
        filtered_articles = article_data[article_data.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    else:
        filtered_articles = article_data

    # Format links if 'link' column exists
    if 'link' in filtered_articles.columns:
        filtered_articles['link'] = filtered_articles['link'].apply(
            lambda url: f"[Read more]({url})" if pd.notnull(url) else "")
    
    # Display markdown table if link column exists
    if 'link' in filtered_articles.columns:
        st.markdown(filtered_articles.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.dataframe(filtered_articles, use_container_width=True)

except Exception as e:
    st.error(f"❌ Failed to load articles: {e}")
