import os
import psycopg

def update_api_table(event, context=None):
    # Expecting: event = {"btc_data": ["BTC", "2025-06-11", 56000.0, 58000.0, 55000.0, 57000.0, 2100.5]}
    record = event.get("btc_data")
    if not isinstance(record, list) or len(record) != 7:
        raise ValueError("Invalid or missing BTC data. Expected 7 elements.")

    dbconn = os.getenv("DBCONN")
    if not dbconn:
        raise EnvironmentError("DBCONN not found in environment variables.")

    query = """
        INSERT INTO api_data (date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date) DO NOTHING;
    """

    try:
        with psycopg.connect(dbconn) as conn:
            with conn.cursor() as cur:
                _, date, open_, high, low, close, volume = record
                cur.execute(query, (date, open_, high, low, close, volume))
                conn.commit()
        return {"message": f"Inserted BTC data for {date}"}
    except Exception as e:
        raise RuntimeError(f"Database insert failed: {e}")
