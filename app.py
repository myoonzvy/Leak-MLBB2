import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import streamlit as st

BASE_URL = "https://survey.moontontech.net/t/5RVc"
TITLE_CODE = "5RVc"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RESULTS_FILE = Path("results.json")
WORKERS = 16

st.set_page_config(page_title=f"{TITLE_CODE} Survey Scanner", page_icon="🔎", layout="wide")

st.markdown("""
<style>
.stApp { background: #010001; color: white; }
a { text-decoration: none !important; }
.code-grid { display