import os
import time

import altair as alt
import numpy as np
import pandas as pd
import pymongo
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Set the page title
st.title("REPORT")

if st.button("Reset"):
    st.session_state.value = "Reset"
    st.rerun()


def get_data():
    mongo_uri = os.getenv("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri)
    db = client["account"]
    collection = db["referral"]
    data = collection.find()

    print(data)

    return data


def get_leaderboard(id: str):
    if not id:
        return None
    url = "https://w3gg.io/api/v1/leaderboards"

    querystring = {"offset": "0", "limit": "3", "filter": "user_id:eq:{}".format(id)}

    payload = ""
    headers = {"User-Agent": "insomnia/2023.5.8"}

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    if response.status_code == 200:
        j = response.json()
        r = j.get("results", [])
        if len(r) > 0:
            return r[0]
        else:
            return None
    else:
        return None


data = get_data()

filtered_data = []
for d in data:
    e = {
        "name": d.get("name", None),
        "email": d.get("email", None),
        # "password": d.get("password", None),
        "active": d.get("active", None),
        "referral_code": d.get("referral_code", None),
        "id": d.get("id", None),
        "exp": None,
        "wxp": None,
    }
    # check leaderboards
    l = get_leaderboard(e.get("id"))
    if l:
        exp = l.get("exp", None)
        wxp = l.get("wxp", None)

        if exp:
            e["exp"] = str(int(exp))
        if wxp:
            e["wxp"] = str(int(wxp))

    filtered_data.append(e)

df = pd.DataFrame(filtered_data)
st.table(df)


progress_text = "count down.."
my_bar = st.progress(0, text=progress_text)

for percent_complete in range(30):
    time.sleep(1)
    my_bar.progress(percent_complete + 1, text=progress_text)

st.write("refetching data")
time.sleep(1)
my_bar.empty()
st.rerun()
