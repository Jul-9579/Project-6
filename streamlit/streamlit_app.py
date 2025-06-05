import streamlit as st
from dotenv import load_dotenv
import os
import psycopg
import pandas as pd

# Load environment variables
load_dotenv()

# Define the function to get data from your Supabase PostgreSQL table
def get_api_data():
    dbconn = st.secrets["DBCONN"]  # Make sure this is in your .env file
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()

    # Execute your SQL query
    cur.execute('SELECT * FROM api_data;')

    # Fetch all data
    data = cur.fetchall()

    # Optional: get column names dynamically
    colnames = [desc.name for desc in cur.description]

    cur.close()
    conn.close()

    # Return as pandas DataFrame
    return pd.DataFrame(data, columns=colnames)

# Streamlit interface starts here
st.title("📊 Bitcoin Stock Prices")

# Fetch data
try:
    api_data = get_api_data()
    st.success("✅ Data loaded successfully!")
    st.dataframe(api_data)

    # Optional: Plot something (if you have numeric columns)
    if "date" in api_data.columns and "close" in api_data.columns:
        api_data["date"] = pd.to_datetime(api_data["date"])
        st.line_chart(api_data.set_index("date")["close"])
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")



# Define a fonction to get data from article table
import pandas as pd
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()  # Make sure this is at the top of your script

def get_article_data():
    dbconn = dbconn = st.secrets["DBCONN"]  # Ensure your .env uses DBCONN, not DB_CONN (unless your code matches)
    if dbconn is None:
        raise ValueError("❌ Environment variable 'DBCONN' not found. Check your .env file.")

    # Connect to database
    try:
        conn = psycopg.connect(dbconn)
        cur = conn.cursor()

        # Execute SQL query
        cur.execute('SELECT * FROM article_data;')

        # Fetch all rows
        data = cur.fetchall()

        # Get column names from cursor description
        colnames = [desc.name for desc in cur.description]

        cur.close()
        conn.close()

        # Return data as a DataFrame
        return pd.DataFrame(data, columns=colnames)

    except Exception as e:
        raise RuntimeError(f"❌ Failed to fetch article data: {e}")
    

st.header("📰 Latest Bitcoin News")
try:
    article_data = get_article_data()
    st.dataframe(article_data)
except Exception as e:
    st.error(e)





