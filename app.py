import html
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

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/125.0 Mobile Safari/537.36",
    "Accept": "text/html,application