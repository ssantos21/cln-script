from collections import defaultdict
from datetime import datetime, timedelta
import json
import requests
import psycopg2

import utils

def save(settings_data, data_json, start_time, end_time):

    pg_host, pg_port, pg_db, pg_user, pg_password = \
        settings_data["pg_host"], \
        settings_data["pg_port"], \
        settings_data["pg_db"], \
        settings_data["pg_user"], \
        settings_data["pg_password"]
    
    conn_string = "host=%s port=%s dbname=%s user=%s password=%s" % (pg_host, pg_port, pg_db, pg_user, pg_password)

    conn = psycopg2.connect(conn_string)

    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS cln_event_earnings (id serial PRIMARY KEY, channel varchar, start_time TIMESTAMPTZ, end_time TIMESTAMPTZ, stats_data JSONB);")

    start_time = datetime.fromtimestamp(start_time)
    end_time = datetime.fromtimestamp(end_time)

    for event_data in data_json['events']:
        account = event_data['account']
        event_json = json.dumps(event_data)

        cur.execute("""
            INSERT INTO cln_event_earnings (channel, start_time, end_time, stats_data)
            VALUES (%s, %s, %s, %s);
            """, (account, start_time, end_time, event_json))
        
    conn.commit()

    cur.close()
    conn.close()

def execute(hours=24):
    print("Executing total-fee-income.py")

    settings_data = utils.get_settings_data()

    rpc_method = "v1/bkpr-listaccountevents"

    url = "%s/%s" % (settings_data["nodeRestUrl"], rpc_method)

    headers = {
        "content-type": "application/json",
        "Rune": settings_data["rune"]
    }

    response = requests.post(url, headers=headers)

    data = json.loads(response.text)

    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
    end_time = int(datetime.now().timestamp())

    # Filter the events to remove those older than 24 hours
    filtered_events = [event for event in data['events'] if event['timestamp'] >= start_time]

    # Update the data dictionary with the filtered events
    data['events'] = filtered_events

    save(settings_data, data, start_time, end_time)

    return data
