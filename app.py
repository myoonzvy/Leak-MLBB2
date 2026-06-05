import html
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import streamlit as st

BASE_URL = "https://survey.moontontech.net/t/5RVc"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RESULTS_FILE = Path("results.json")
WORKERS = 16

st.set_page_config(page_title="5RVc Survey Scanner", page_icon="🔎", layout="wide")

st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"]{background:#010001;color:#fff}.block-container{max-width:1100px;padding