import os
import psycopg2


def update_utoday_table (event, context=None):
    articles = event.get("articles")
    if not articles or not isinstance(articles, list):
        raise ValueError("Invalid or missing articles data")

    dbconn = os.getenv("DBCONN")
    if not dbconn:
        raise EnvironmentError("DBCONN not found in environment variables.")

    insert_query = """
        INSERT INTO article_data (date, title, author, link)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (link) DO NOTHING;
    """

    try:
        with psycopg.connect(dbconn) as conn:
            with conn.cursor() as cur:
                for article in articles:
                    cur.execute(insert_query, (
                        article["date"],
                        article["title"],
                        article["author"],
                        article["link"]
                    ))
                conn.commit()

        print(f"✅ Inserted {len(articles)} articles")
        return {"message": f"Inserted {len(articles)} articles"}
    except Exception as e:
        print(f"❌ Failed to insert data: {e}")
        raise e


