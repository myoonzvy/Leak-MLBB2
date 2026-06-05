import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import streamlit as st

BASE_URL = "https://survey.moontontech.net/t/5RVc"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RESULTS_FILE = Path("results.json")
WORKERS = 12

st.set_page_config(page_title="5RVc Survey Scanner", page_icon="🔎", layout="wide")

st.title("5RVc Survey Scanner")
st.caption("Simple working