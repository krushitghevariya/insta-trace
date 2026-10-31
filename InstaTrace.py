#!/usr/bin/env python3
"""
InstaTrace – Instagram Private & Collab Media Extractor (2025/2026 POC)
Streamlit Web Interface supporting Images, Videos, and Reels
Fully responsive across desktop, laptop, tablet, and mobile screens.
Includes Cloud Anti-429 Rate-Limit Mitigation & Cookie/Proxy Authentication.
FOR SECURITY RESEARCH / EDUCATIONAL USE ONLY
"""

import streamlit as st
import requests
import json
import time
import re
import random
from urllib.parse import unquote
from bs4 import BeautifulSoup
from io import StringIO, BytesIO
import csv
from PIL import Image
from typing import Dict, List, Optional, Sequence, Set, Tuple, Any

# Page configuration - responsive layout
st.set_page_config(
    page_title="InstaTrace – Reels, Videos & Images",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="auto"  # Automatically adapts: expanded on desktop, collapsed on mobile/tablet
)

# Comprehensive responsive styling across Desktop, Tablet, and Mobile
st.markdown("""
    <style>
    /* =========================================================
       1. GLOBAL & CONTAINER RESPONSIVENESS
       ========================================================= */
    *, *::before, *::after {
        box-sizing: border-box;
    }

    /* Fluid root layout padding */
    .block-container {
        padding-top: clamp(1rem, 2.5vw, 2.2rem) !important;
        padding-bottom: clamp(2rem, 3.5vw, 3.5rem) !important;
        padding-left: clamp(0.75rem, 3vw, 2rem) !important;
        padding-right: clamp(0.75rem, 3vw, 2rem) !important;
        max-width: 1400px !important;
    }

    /* =========================================================
       2. TYPOGRAPHY & HEADERS (Fluid clamp)
       ========================================================= */
    .main-header {
        text-align: center;
        background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(1.8rem, 4.5vw, 2.8rem) !important;
        font-weight: 800;
        margin-bottom: 6px;
        line-height: 1.2;
        word-break: break-word;
    }

    .sub-header {
        text-align: center;
        color: #555;
        font-size: clamp(0.9rem, 2vw, 1.15rem) !important;
        margin-bottom: clamp(14px, 2.5vw, 22px);
        line-height: 1.4;
        padding: 0 4px;
        word-break: break-word;
    }

    /* =========================================================
       3. RESPONSIVE NOTIFICATION BOXES & CARDS
       ========================================================= */
    .warning-box, .success-box, .error-box, .info-box {
        padding: clamp(10px, 2.2vw, 16px) clamp(12px, 2.5vw, 18px) !important;
        border-radius: 8px;
        margin-bottom: clamp(12px, 2vw, 18px);
        font-size: clamp(0.85rem, 1.8vw, 0.95rem);
        line-height: 1.45;
        word-break: break-word;
        overflow-wrap: anywhere;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }

    .card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: clamp(14px, 2.5vw, 22px);
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        word-break: break-word;
    }

    .post-card {
        background-color: #fafbfc;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: clamp(12px, 2.2vw, 18px);
        margin-bottom: clamp(12px, 2.2vw, 18px);
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        word-break: break-word;
    }

    .post-header-flex {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }

    /* =========================================================
       4. MEDIA BADGES & CAPTIONS
       ========================================================= */
    .badge-video, .badge-image, .badge-cover {
        display: inline-flex;
        align-items: center;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: clamp(0.72rem, 1.6vw, 0.82rem);
        font-weight: 700;
        white-space: nowrap;
        margin-right: 4px;
        vertical-align: middle;
    }
    .badge-video {
        background-color: #6f42c1;
        color: white;
    }
    .badge-image {
        background-color: #0366d6;
        color: white;
    }
    .badge-cover {
        background-color: #d73a49;
        color: white;
    }

    .caption-box {
        background: #f1f3f5;
        border-radius: 8px;
        padding: clamp(8px, 1.8vw, 12px);
        font-size: clamp(0.82rem, 1.8vw, 0.9rem);
        color: #333;
        margin-top: 8px;
        margin-bottom: 14px;
        word-break: break-word;
        overflow-wrap: anywhere;
    }

    /* =========================================================
       5. RESPONSIVE COLUMNS & FLEX WRAPPING
       ========================================================= */
    @media (max-width: 992px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.75rem 0.5rem !important;
        }
    }

    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
        }
        [data-testid="stSidebar"] {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }

    @media (max-width: 540px) {
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 0.35rem) !important;
            min-width: calc(50% - 0.35rem) !important;
        }
    }

    /* =========================================================
       6. RESPONSIVE METRIC CARDS
       ========================================================= */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #eef0f2;
        border-radius: 10px;
        padding: clamp(8px, 1.8vw, 14px);
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        overflow: hidden;
    }
    [data-testid="stMetricLabel"] {
        font-size: clamp(0.75rem, 1.8vw, 0.88rem) !important;
        white-space: normal !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.2rem, 3.2vw, 1.8rem) !important;
        line-height: 1.2 !important;
    }

    /* =========================================================
       7. TOUCH-FRIENDLY TABS & NAVIGATION
       ========================================================= */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 4px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        flex-wrap: nowrap;
        padding-bottom: 2px;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        padding: clamp(6px, 1.6vw, 10px) clamp(10px, 2vw, 16px) !important;
        font-size: clamp(0.8rem, 1.8vw, 0.95rem) !important;
        white-space: nowrap !important;
    }

    /* =========================================================
       8. BUTTONS & INTERACTIVE ELEMENTS (Touch friendly >= 44px)
       ========================================================= */
    .stButton > button,
    .stDownloadButton > button {
        min-height: 44px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: clamp(0.85rem, 1.8vw, 0.95rem) !important;
        padding: 8px 14px !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        word-break: break-word !important;
        transition: background-color 0.15s ease, transform 0.1s ease;
    }
    .stButton > button:active,
    .stDownloadButton > button:active {
        transform: scale(0.98);
    }

    /* Inputs & Selects touch size */
    [data-baseweb="input"], [data-baseweb="select"] {
        min-height: 42px !important;
        font-size: clamp(0.88rem, 1.8vw, 0.95rem) !important;
        border-radius: 8px !important;
    }

    /* =========================================================
       9. RESPONSIVE MEDIA (Images, Videos & Embeds)
       ========================================================= */
    [data-testid="stVideo"], [data-testid="stImage"] {
        width: 100% !important;
        max-width: 100% !important;
        border-radius: 8px;
        overflow: hidden;
    }
    video {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        border-radius: 8px;
        background: #000;
    }
    img {
        max-width: 100% !important;
        height: auto !important;
        object-fit: cover;
        border-radius: 8px;
    }

    /* =========================================================
       10. PREVENT HORIZONTAL OVERFLOW
       ========================================================= */
    code, pre {
        white-space: pre-wrap !important;
        word-break: break-all !important;
        overflow-wrap: anywhere !important;
    }
    [data-testid="stCodeBlock"] {
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    /* Responsive Dataframe */
    [data-testid="stDataFrame"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }
    </style>
""", unsafe_allow_html=True)

APP_NAME = "InstaTrace"
APP_SUBTITLE = "Instagram Private & Collab Media Extractor (Reels, Videos & Images POC)"
DISCLAIMER_HTML = """
<div class='warning-box'>
  <strong>⚠️ SECURITY RESEARCH & EDUCATIONAL NOTICE:</strong><br>
  This tool analyzes Instagram client behavior, timeline connections, and collaborative posts (co-authored content).<br>
  Only use on accounts or content you own or have explicit authorization to test.
</div>
"""


def id_to_shortcode(media_id: int) -> str:
    """Convert numerical Instagram media PK to shortcode."""
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    shortcode = ''
    while media_id > 0:
        media_id, remainder = divmod(media_id, 64)
        shortcode = alphabet[remainder] + shortcode
    return shortcode


def decode_url(escaped: str) -> str:
    """Decode URL from escaped format."""
    try:
        return unquote(escaped.encode('utf-8').decode('unicode_escape'))
    except Exception:
        return escaped


def shortcode_to_id(shortcode: str) -> int:
    """Convert Instagram alphanumeric shortcode to numerical media ID."""
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    media_id = 0
    for char in shortcode:
        if char in alphabet:
            media_id = media_id * 64 + alphabet.index(char)
    return media_id


def parse_cookie_input(raw: str) -> Tuple[Dict[str, str], str]:
    """Parse raw sessionid, cookie header, or exported JSON into cookies dict and header string."""
    raw = (raw or "").strip()
    if not raw:
        return {}, ""

    cookies: Dict[str, str] = {}

    # Strip leading 'Cookie:' or 'cookie:' if copied from DevTools headers
    if raw.lower().startswith("cookie:"):
        raw = raw[7:].strip()

    # Try parsing as JSON (e.g. from Cookie-Editor / EditThisCookie)
    if (raw.startswith("[") and raw.endswith("]")) or (raw.startswith("{") and raw.endswith("}")):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and "name" in item and "value" in item:
                        k = str(item["name"]).strip()
                        v = str(item["value"]).strip().strip('"')
                        if k:
                            cookies[k] = v
            elif isinstance(parsed, dict):
                for k, v in parsed.items():
                    k_str = str(k).strip()
                    v_str = str(v).strip().strip('"')
                    if k_str:
                        cookies[k_str] = v_str
            if cookies:
                cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
                return cookies, cookie_header
        except Exception:
            pass

    # Standard key-value format (sessionid=xxx; csrftoken=yyy)
    if "=" in raw:
        for pair in raw.split(";"):
            pair = pair.strip()
            if "=" in pair:
                k, v = pair.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"')
                if k:
                    cookies[k] = v
    else:
        # Raw session ID entered by user
        clean_sid = raw.strip().strip('"').strip("'")
        cookies["sessionid"] = clean_sid

    cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
    return cookies, cookie_header


def parse_cookie_string(cookie_input: str) -> Dict[str, str]:
    """Compatibility wrapper for parse_cookie_input."""
    cookies, _ = parse_cookie_input(cookie_input)
    return cookies


def parse_target_input(raw: str) -> Dict[str, Any]:
    """Parse user input into either profile username or direct reel/post URL."""
    raw = (raw or "").strip()

    # Check if direct reel URL
    m_reel = re.search(r"instagram\.com/(?:reel|reels)/([A-Za-z0-9_-]+)", raw)
    if m_reel:
        return {"mode": "direct_reel", "shortcode": m_reel.group(1), "target": m_reel.group(1)}

    # Check if direct post URL
    m_post = re.search(r"instagram\.com/p/([A-Za-z0-9_-]+)", raw)
    if m_post:
        return {"mode": "direct_post", "shortcode": m_post.group(1), "target": m_post.group(1)}

    # Check if profile URL with optional tab
    m_profile = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", raw)
    if m_profile:
        u = m_profile.group(1).strip()
        if u not in ("p", "reel", "reels", "stories", "explore"):
            return {"mode": "profile", "username": u, "target": u}

    # Plain username
    clean = raw.lstrip("@").strip().strip("/")
    return {"mode": "profile", "username": clean, "target": clean}


def create_session(cookie_str: str = "", proxy_url: str = "") -> requests.Session:
    """Create an anti-rate-limit session with rotating browser headers, cookies, and proxies."""
    session = requests.Session()

    ua_pool = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
    ]
    chosen_ua = random.choice(ua_pool)

    headers = {
        'user-agent': chosen_ua,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?1' if 'Mobile' in chosen_ua else '?0',
        'sec-ch-ua-platform': '"Android"' if 'Android' in chosen_ua else ('"macOS"' if 'Macintosh' in chosen_ua else '"Windows"'),
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'x-ig-app-id': '936619743392459',
        'x-asbd-id': '129477',
    }
    session.headers.update(headers)

    # Attach proxy if provided
    if proxy_url and proxy_url.strip():
        p = proxy_url.strip()
        session.proxies = {'http': p, 'https': p}

    # Attach session cookies if provided (from UI or Streamlit Secrets)
    effective_cookie = cookie_str.strip() if cookie_str else ""
    if not effective_cookie:
        try:
            effective_cookie = getattr(st, "secrets", {}).get("IG_COOKIE", "") or getattr(st, "secrets", {}).get("SESSION_ID", "")
        except Exception:
            effective_cookie = ""

    if effective_cookie:
        cookies_dict, cookie_hdr = parse_cookie_input(effective_cookie)
        if cookies_dict:
            session.cookies.update(cookies_dict)
            for k, v in cookies_dict.items():
                session.cookies.set(k, v, domain=".instagram.com", path="/")
            if cookie_hdr:
                session.headers['Cookie'] = cookie_hdr
            if "csrftoken" in cookies_dict:
                session.headers['x-csrftoken'] = cookies_dict["csrftoken"]

    return session


def validate_instagram_session(session: requests.Session) -> Tuple[bool, str]:
    """Test if current session cookies are authenticated and valid."""
    test_url = "https://www.instagram.com/api/v1/users/web_profile_info/?username=instagram"
    headers = {
        'x-ig-app-id': '936619743392459',
        'x-asbd-id': '129477',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.instagram.com/instagram/',
        'accept': '*/*',
    }
    try:
        r = session.get(test_url, headers=headers, timeout=12)
        if r.status_code == 200:
            return True, "Active (Session Authenticated & Verified)"
        elif r.status_code in (401, 403):
            return False, "Expired or Invalid (Instagram returned HTTP 401 Login Required)"
        elif r.status_code == 429:
            return False, "Rate Limited (HTTP 429 - Instagram is throttling requests from this IP)"
        else:
            return False, f"Unexpected response (HTTP {r.status_code})"
    except Exception as e:
        return False, f"Connection test failed: {e}"


def fetch_web_profile_info(session: requests.Session, username: str) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch profile data from Instagram's web_profile_info API."""
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        'x-ig-app-id': '936619743392459',
        'x-asbd-id': '129477',
        'x-requested-with': 'XMLHttpRequest',
        'referer': f'https://www.instagram.com/{username}/',
        'accept': '*/*',
    }
    max_retries = 2
    for attempt in range(max_retries):
        try:
            r = session.get(url, headers=headers, timeout=18)
            if r.status_code == 200:
                try:
                    return r.json(), None
                except Exception as e:
                    return None, f"JSON parse error: {e}"
            if r.status_code in (401, 403):
                return None, "HTTP 401/403: Instagram session expired or requires login."
            if r.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(2.0 + random.random() * 1.5)
                    continue
                return None, "HTTP 429 (Rate Limited by Instagram)"
            return None, f"HTTP {r.status_code}"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2.0)
                continue
            return None, f"Connection error: {e}"
    return None, "Request failed"


def fetch_user_tags(session: requests.Session, user_id: str) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch user's tagged and collaborated posts from Instagram API."""
    url = f"https://www.instagram.com/api/v1/usertags/{user_id}/feed/"
    headers = {
        'x-ig-app-id': '936619743392459',
        'x-asbd-id': '129477',
        'x-requested-with': 'XMLHttpRequest',
        'accept': '*/*',
    }
    try:
        r = session.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json(), None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def fetch_media_info_api(session: requests.Session, shortcode: str) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch media info via media PK or GraphQL query."""
    mid = shortcode_to_id(shortcode)
    if mid > 0:
        url = f"https://www.instagram.com/api/v1/media/{mid}/info/"
        headers = {
            'x-ig-app-id': '936619743392459',
            'x-asbd-id': '129477',
            'x-requested-with': 'XMLHttpRequest',
            'accept': '*/*',
        }
        try:
            r = session.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                try:
                    return r.json(), None
                except Exception:
                    pass
        except Exception:
            pass

    # Try GraphQL doc_id
    try:
        gql_url = f"https://www.instagram.com/graphql/query/?doc_id=10015901848480474&variables={json.dumps({'shortcode': shortcode})}"
        r = session.get(gql_url, timeout=15)
        if r.status_code == 200:
            return r.json(), None
    except Exception:
        pass

    return None, "Media API lookup failed"


def fetch_tab_html(session: requests.Session, username: str, tab_path: str = "") -> Tuple[Optional[str], Optional[str]]:
    """Fetch profile tab HTML with automatic backoff retry on 429."""
    url = f"https://www.instagram.com/{username}/{tab_path}"
    max_retries = 2
    for attempt in range(max_retries):
        try:
            r = session.get(url, timeout=18)
            if r.status_code == 200:
                return r.text, None
            if r.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(2.0 + random.random() * 1.5)
                    continue
                return None, "HTTP 429 (Rate Limited by Instagram)"
            return None, f"HTTP {r.status_code}"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2.0)
                continue
            return None, f"Connection error: {e}"
    return None, "Request failed"


def fetch_direct_url(session: requests.Session, url: str) -> Tuple[Optional[str], Optional[str]]:
    """Fetch direct post or reel page with retry."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            r = session.get(url, timeout=18)
            if r.status_code == 200:
                return r.text, None
            if r.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(2.0 + random.random() * 1.5)
                    continue
                return None, "HTTP 429 (Rate Limited by Instagram)"
            return None, f"HTTP {r.status_code}"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2.0)
                continue
            return None, f"Connection error: {e}"
    return None, "Request failed"


def extract_media_from_node(node: dict, acc: List[Dict[str, Any]], current_pid: Optional[str] = None, source: str = "") -> None:
    """Extract photos, videos, reels, and collab posts from any JSON node."""
    if not isinstance(node, dict):
        return

    pid = node.get("pk") or node.get("id") or current_pid or "unknown"
    pid = str(pid).replace("POLARIS_", "")

    shortcode = node.get("code") or node.get("shortcode")
    if not shortcode and str(pid).isdigit():
        try:
            shortcode = id_to_shortcode(int(pid))
        except Exception:
            shortcode = None

    media_type = node.get("media_type")  # 1=image, 2=video, 8=carousel
    product_type = str(node.get("product_type", "")).lower()  # "clips", "feed", etc.
    typename = str(node.get("__typename", "")).lower()
    is_video_node = (
        bool(node.get("is_video")) or
        media_type == 2 or
        product_type == "clips" or
        "video" in typename or
        "video" in str(node.get("__isXIGPolarisMedia", "")).lower()
    )

    # Caption extraction (standard, GraphQL, or string)
    caption = ""
    cap_obj = node.get("caption")
    if isinstance(cap_obj, dict):
        caption = cap_obj.get("text", "") or ""
    elif isinstance(cap_obj, str):
        caption = cap_obj
    elif "edge_media_to_caption" in node and isinstance(node["edge_media_to_caption"], dict):
        edges = node["edge_media_to_caption"].get("edges", [])
        if edges and isinstance(edges[0], dict):
            caption = edges[0].get("node", {}).get("text", "") or ""

    # Dimensions
    dim = node.get("dimensions") or {}
    w = dim.get("width") or node.get("original_width") or node.get("video_width") or "?"
    h = dim.get("height") or node.get("original_height") or node.get("video_height") or "?"
    res = f"{w}×{h}" if w != "?" and h != "?" else "Original"

    # Collab info
    collab_users = []
    coauthors = node.get("coauthor_producers")
    if isinstance(coauthors, list):
        for co in coauthors:
            if isinstance(co, dict) and co.get("username"):
                collab_users.append(co["username"])

    label_prefix = f"Collab with @{', @'.join(collab_users)} - " if collab_users else ""

    # 1. Video versions (Direct MP4 streams from IG CDN)
    if "video_versions" in node and isinstance(node["video_versions"], list) and node["video_versions"]:
        best_v = None
        best_v_score = -1
        for v in node["video_versions"]:
            if not isinstance(v, dict) or not v.get("url"):
                continue
            vw = v.get("width")
            vh = v.get("height")
            score = (vw * vh) if isinstance(vw, int) and isinstance(vh, int) else 0
            if score > best_v_score:
                best_v_score = score
                best_v = v

        if best_v and best_v.get("url"):
            vw = best_v.get("width", "?")
            vh = best_v.get("height", "?")
            label = f"{label_prefix}Reel (Video)" if (product_type == "clips" or "clips" in source.lower()) else f"{label_prefix}Video"
            acc.append({
                "post_id": pid,
                "shortcode": shortcode,
                "kind": "video",
                "type_label": label,
                "resolution": f"{vw}×{vh}",
                "url": decode_url(best_v["url"]),
                "caption": caption,
                "source": source,
                "collabs": collab_users,
            })

    # 2. Direct video_url (GraphQL)
    if "video_url" in node and isinstance(node["video_url"], str) and node["video_url"]:
        label = f"{label_prefix}Reel (Video)" if (product_type == "clips" or "felix" in source.lower() or "clips" in source.lower()) else f"{label_prefix}Video"
        acc.append({
            "post_id": pid,
            "shortcode": shortcode,
            "kind": "video",
            "type_label": label,
            "resolution": res,
            "url": decode_url(node["video_url"]),
            "caption": caption,
            "source": source,
            "collabs": collab_users,
        })

    # 3. Video resources list (GraphQL)
    if "video_resources" in node and isinstance(node["video_resources"], list):
        for vr in node["video_resources"]:
            if isinstance(vr, dict) and vr.get("src"):
                vw = vr.get("config_width", "?")
                vh = vr.get("config_height", "?")
                label = f"{label_prefix}Reel (Video)" if (product_type == "clips" or "clips" in source.lower()) else f"{label_prefix}Video"
                acc.append({
                    "post_id": pid,
                    "shortcode": shortcode,
                    "kind": "video",
                    "type_label": label,
                    "resolution": f"{vw}×{vh}",
                    "url": decode_url(vr["src"]),
                    "caption": caption,
                    "source": source,
                    "collabs": collab_users,
                })

    # 4. Image candidates / Cover Frame
    if "image_versions2" in node and isinstance(node["image_versions2"], dict):
        cands = node["image_versions2"].get("candidates", [])
        if isinstance(cands, list) and cands:
            best_cand = None
            best_cand_score = -1
            for cand in cands:
                if not isinstance(cand, dict) or not cand.get("url"):
                    continue
                cw = cand.get("width")
                ch = cand.get("height")
                score = (cw * ch) if isinstance(cw, int) and isinstance(ch, int) else 0
                if score > best_cand_score:
                    best_cand_score = score
                    best_cand = cand

            if best_cand and best_cand.get("url"):
                cw = best_cand.get("width", "?")
                ch = best_cand.get("height", "?")
                if is_video_node:
                    kind = "reel_cover" if product_type == "clips" else "video_cover"
                    label = f"{label_prefix}Reel Cover Frame" if product_type == "clips" else f"{label_prefix}Video Thumbnail"
                else:
                    kind = "image"
                    label = f"{label_prefix}Image"

                acc.append({
                    "post_id": pid,
                    "shortcode": shortcode,
                    "kind": kind,
                    "type_label": label,
                    "resolution": f"{cw}×{ch}",
                    "url": decode_url(best_cand["url"]),
                    "caption": caption,
                    "source": source,
                    "collabs": collab_users,
                })

    # 5. Direct display_uri / display_url (GraphQL)
    elif node.get("display_uri") or node.get("display_url"):
        d_url = node.get("display_uri") or node.get("display_url")
        if is_video_node:
            kind = "reel_cover" if product_type == "clips" else "video_cover"
            label = f"{label_prefix}Reel Cover Frame" if product_type == "clips" else f"{label_prefix}Video Thumbnail"
        else:
            kind = "image"
            label = f"{label_prefix}Image"

        acc.append({
            "post_id": pid,
            "shortcode": shortcode,
            "kind": kind,
            "type_label": label,
            "resolution": res,
            "url": decode_url(d_url),
            "caption": caption,
            "source": source,
            "collabs": collab_users,
        })

    # 6. Carousel sidecar children (Multi-item posts)
    if "edge_sidecar_to_children" in node and isinstance(node["edge_sidecar_to_children"], dict):
        edges = node["edge_sidecar_to_children"].get("edges", [])
        for edge in edges:
            if isinstance(edge, dict) and "node" in edge:
                extract_media_from_node(edge["node"], acc, current_pid=pid, source=f"{source} (Carousel Slide)")

    if "carousel_media" in node and isinstance(node["carousel_media"], list):
        for cnode in node["carousel_media"]:
            if isinstance(cnode, dict):
                extract_media_from_node(cnode, acc, current_pid=pid, source=f"{source} (Carousel Slide)")


def walk_json(data: Any, acc: List[Dict[str, Any]], current_pid: Optional[str] = None, source: str = "") -> None:
    """Recursively search JSON for media objects."""
    if isinstance(data, dict):
        pid = data.get("pk") or data.get("id") or current_pid
        extract_media_from_node(data, acc, pid, source)
        for v in data.values():
            walk_json(v, acc, pid, source)
    elif isinstance(data, list):
        for item in data:
            walk_json(item, acc, current_pid, source)


def extract_media_from_html(html: str, source: str = "") -> List[Dict[str, Any]]:
    """Extract media from all embedded scripts, ServerJS objects, and regex patterns in the HTML page."""
    if not html:
        return []

    acc: List[Dict[str, Any]] = []
    soup = BeautifulSoup(html, "html.parser")

    # 1. Inspect all script tags
    for script in soup.find_all("script"):
        text = script.string or script.text or ""
        if not text:
            continue

        # Try direct JSON parsing
        if any(term in text for term in ["image_versions2", "video_versions", "video_url", "polaris", "clips", "timeline", "shortcode"]):
            try:
                data = json.loads(text)
                walk_json(data, acc, source=source)
                continue
            except Exception:
                pass

        # Try extracting JSON inside s.handle(...)
        if "s.handle(" in text:
            for m in re.finditer(r's\.handle\((\{.*?\})\);', text):
                try:
                    data = json.loads(m.group(1))
                    walk_json(data, acc, source=source)
                except Exception:
                    pass

        # Try window.__additionalDataLoaded
        if "__additionalDataLoaded" in text:
            for m in re.finditer(r'__additionalDataLoaded\s*\([^,]+,\s*(\{.*?\})\s*\);', text):
                try:
                    data = json.loads(m.group(1))
                    walk_json(data, acc, source=source)
                except Exception:
                    pass

        # Try window._sharedData
        if "_sharedData" in text:
            m = re.search(r'_sharedData\s*=\s*(\{.*?\});', text)
            if m:
                try:
                    data = json.loads(m.group(1))
                    walk_json(data, acc, source=source)
                except Exception:
                    pass

    # 2. Safety Regex Extraction for direct .mp4 CDN video streams
    mp4_pattern = re.findall(r'https?:\\?/\\?/[^"\'<>\s]+?(?:fbcdn|cdninstagram)\.[a-z]+[^"\'<>\s]+?\.mp4[^"\'<>\s]*', html)
    existing_urls = {item["url"] for item in acc}
    for raw_mp4 in mp4_pattern:
        clean_mp4 = decode_url(raw_mp4.replace(r'\/', '/').replace(r'\u0026', '&'))
        if clean_mp4 not in existing_urls:
            acc.append({
                "post_id": "stream_media",
                "shortcode": None,
                "kind": "video",
                "type_label": "Direct Video Stream",
                "resolution": "Stream",
                "url": clean_mp4,
                "caption": "",
                "source": source,
                "collabs": [],
            })
            existing_urls.add(clean_mp4)

    return acc


def scan_target(
    target_info: Dict[str, Any],
    scan_reels: bool = True,
    scan_tagged: bool = True,
    scan_feed: bool = True,
    cookie_str: str = "",
    proxy_url: str = "",
    delay: float = 1.5
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Scan target with session anti-429 features, authenticated API support, and pacing delay."""
    session = create_session(cookie_str=cookie_str, proxy_url=proxy_url)

    all_media: List[Dict[str, Any]] = []
    errors: List[str] = []

    if target_info["mode"] in ("direct_reel", "direct_post"):
        code = target_info["shortcode"]
        path_type = "reel" if target_info["mode"] == "direct_reel" else "p"

        # 1. Try Direct API / GraphQL if cookies are set
        api_data, api_err = fetch_media_info_api(session, code)
        if api_data:
            walk_json(api_data, all_media, source="Media Info API")

        # 2. Try Embed captioned URL (high success rate)
        embed_url = f"https://www.instagram.com/p/{code}/embed/captioned/"
        emb_html, emb_err = fetch_direct_url(session, embed_url)
        if emb_html:
            items = extract_media_from_html(emb_html, source="Instagram Embed")
            all_media.extend(items)

        # 3. Direct URL HTML
        direct_url = f"https://www.instagram.com/{path_type}/{code}/"
        html, err = fetch_direct_url(session, direct_url)
        if html:
            items = extract_media_from_html(html, source="Direct Page")
            all_media.extend(items)
        if err and not all_media:
            errors.append(f"Direct fetch: {err}")

    elif target_info["mode"] == "profile":
        username = target_info["username"]
        profile_api_success = False

        # --- Tier 1: Authenticated Web Profile Info API ---
        api_data, api_err = fetch_web_profile_info(session, username)
        if api_data and "data" in api_data and "user" in api_data["data"]:
            user_obj = api_data["data"]["user"]
            if user_obj:
                profile_api_success = True
                user_id = user_obj.get("id")
                is_private = user_obj.get("is_private", False)

                # Feed / Timeline Media
                if scan_feed:
                    timeline = user_obj.get("edge_owner_to_timeline_media", {})
                    walk_json(timeline, all_media, source="Profile Timeline API")

                # Reels / Felix Video Timeline
                if scan_reels:
                    reels_timeline = user_obj.get("edge_felix_video_timeline", {})
                    walk_json(reels_timeline, all_media, source="Reels Timeline API")

                # Tagged & Collabs API (if user ID is present)
                if scan_tagged and user_id:
                    if delay > 0:
                        time.sleep(delay)
                    tags_data, tags_err = fetch_user_tags(session, user_id)
                    if tags_data:
                        walk_json(tags_data, all_media, source="Tagged & Collabs API")

                if is_private and not all_media:
                    errors.append(f"Account @{username} is private and the authenticated session is not following them.")

        if api_err:
            errors.append(f"Profile API: {api_err}")

        # --- Tier 2: Fallback to HTML Tab scraping if API returned 0 media or failed ---
        if not all_media or not profile_api_success:
            scan_jobs = []
            if scan_feed:
                scan_jobs.append(("Feed / Timeline", ""))
            if scan_reels:
                scan_jobs.append(("Reels / Clips Tab", "reels/"))
            if scan_tagged:
                scan_jobs.append(("Tagged / Collabs Tab", "tagged/"))

            for idx, (label, tab_path) in enumerate(scan_jobs):
                if idx > 0 and delay > 0:
                    time.sleep(delay + random.uniform(0.1, 0.4))

                html, err = fetch_tab_html(session, username, tab_path)
                if html:
                    items = extract_media_from_html(html, source=label)
                    all_media.extend(items)
                if err:
                    errors.append(f"{label}: {err}")

    # Deduplicate media by URL
    unique_items: Dict[str, Dict[str, Any]] = {}
    for item in all_media:
        url = item.get("url")
        if url and url not in unique_items:
            unique_items[url] = item

    deduped = list(unique_items.values())
    error_msg = "; ".join(errors) if errors and not deduped else None
    return deduped, error_msg


@st.cache_data(show_spinner=False, ttl=60 * 30)
def load_image(url: str):
    """Load image from URL."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception:
        pass
    return None


@st.cache_data(show_spinner=False, ttl=60 * 30)
def fetch_media_bytes(url: str) -> Optional[bytes]:
    """Download raw bytes for media download button."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None


def infer_download_meta(url: str, kind: str, res: str) -> Tuple[str, str]:
    """Infer file extension and MIME type for downloads."""
    path = url.split("?", 1)[0].lower()
    if kind == "video" or "video" in res.lower() or path.endswith(".mp4"):
        return "mp4", "video/mp4"
    if path.endswith(".png"):
        return "png", "image/png"
    if path.endswith(".webp"):
        return "webp", "image/webp"
    return "jpg", "image/jpeg"


def format_results_txt(media_items: List[Dict[str, Any]], target_name: str) -> str:
    """Format results as detailed text report."""
    if not media_items:
        return ""

    videos = [m for m in media_items if m.get("kind") == "video"]
    images = [m for m in media_items if m.get("kind") != "video"]

    by_post: Dict[str, List[Dict[str, Any]]] = {}
    for m in media_items:
        pid = m.get("post_id", "unknown")
        by_post.setdefault(pid, []).append(m)

    output = StringIO()
    output.write(f"InstaTrace – Target: @{target_name}\n")
    output.write("=" * 75 + "\n\n")
    output.write(f"Total Media: {len(media_items)} | Videos/Reels: {len(videos)} | Images/Covers: {len(images)} | Posts: {len(by_post)}\n\n")

    for pid in sorted(by_post.keys()):
        items = by_post[pid]
        shortcode = items[0].get("shortcode")
        ig_link = f"https://www.instagram.com/p/{shortcode}/" if shortcode else "N/A"
        cap = items[0].get("caption", "").strip()

        output.write(f"📌 Post ID: {pid} (Shortcode: {shortcode or 'N/A'})\n")
        output.write(f"   Instagram URL: {ig_link}\n")
        if cap:
            output.write(f"   Caption: {cap[:100]}\n")
        output.write(f"   Assets ({len(items)} variants):\n")
        output.write("-" * 75 + "\n")
        for i, it in enumerate(items, 1):
            type_tag = f"[{it.get('type_label', 'MEDIA')}]"
            res = it.get('resolution', '?')
            src = it.get('source', '')
            output.write(f"  {i:2}. {type_tag:<20} {res:>12} ({src})  ->  {it.get('url')}\n")
        output.write("\n")

    return output.getvalue()


def format_results_txt(media_items: List[Dict[str, Any]], target_name: str) -> str:
    """Format results as detailed text report."""
    if not media_items:
        return ""

    videos = [m for m in media_items if m.get("kind") == "video"]
    images = [m for m in media_items if m.get("kind") != "video"]

    by_post: Dict[str, List[Dict[str, Any]]] = {}
    for m in media_items:
        pid = m.get("post_id", "unknown")
        by_post.setdefault(pid, []).append(m)

    output = StringIO()
    output.write(f"InstaTrace – Target: @{target_name}\n")
    output.write("=" * 75 + "\n\n")
    output.write(f"Total Media: {len(media_items)} | Videos/Reels: {len(videos)} | Images/Covers: {len(images)} | Posts: {len(by_post)}\n\n")

    for pid in sorted(by_post.keys()):
        items = by_post[pid]
        shortcode = items[0].get("shortcode")
        ig_link = f"https://www.instagram.com/p/{shortcode}/" if shortcode else "N/A"
        cap = items[0].get("caption", "").strip()
        collabs = items[0].get("collabs", [])

        output.write(f"📌 Post ID: {pid} (Shortcode: {shortcode or 'N/A'})\n")
        output.write(f"   Instagram URL: {ig_link}\n")
        if collabs:
            output.write(f"   Collaborators: @{', @'.join(collabs)}\n")
        if cap:
            output.write(f"   Caption: {cap[:100]}\n")
        output.write(f"   Assets ({len(items)} variants):\n")
        output.write("-" * 75 + "\n")
        for i, it in enumerate(items, 1):
            type_tag = f"[{it.get('type_label', 'MEDIA')}]"
            res = it.get('resolution', '?')
            src = it.get('source', '')
            output.write(f"  {i:2}. {type_tag:<24} {res:>12} ({src})  ->  {it.get('url')}\n")
        output.write("\n")

    return output.getvalue()


def format_results_csv(media_items: List[Dict[str, Any]], target_name: str) -> str:
    """Format results as CSV with columns."""
    if not media_items:
        return ""

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Post ID", "Shortcode", "Media Type", "Resolution", "Collaborators", "Source", "Caption", "URL"])

    for it in media_items:
        collabs_str = ", ".join(it.get("collabs", []))
        writer.writerow([
            it.get("post_id", ""),
            it.get("shortcode", ""),
            it.get("type_label", ""),
            it.get("resolution", ""),
            collabs_str,
            it.get("source", ""),
            it.get("caption", "").replace("\n", " "),
            it.get("url", ""),
        ])

    return output.getvalue()


def format_results_json(media_items: List[Dict[str, Any]], target_name: str) -> str:
    """Format results as JSON."""
    if not media_items:
        return ""

    videos = [m for m in media_items if m.get("kind") == "video"]
    images = [m for m in media_items if m.get("kind") != "video"]

    by_post: Dict[str, List[Dict[str, Any]]] = {}
    for m in media_items:
        pid = m.get("post_id", "unknown")
        by_post.setdefault(pid, []).append(m)

    data = {
        "target": target_name,
        "total_media": len(media_items),
        "total_videos_and_reels": len(videos),
        "total_images_and_covers": len(images),
        "total_posts": len(by_post),
        "posts": by_post
    }

    return json.dumps(data, indent=2)


def _init_state() -> None:
    st.session_state.setdefault("target_input", "")
    st.session_state.setdefault("last_run_target", "")
    st.session_state.setdefault("run_error", None)
    st.session_state.setdefault("media_found", None)
    st.session_state.setdefault("media_items", None)
    st.session_state.setdefault("last_run_ts", None)
    st.session_state.setdefault("cookie_input", "")
    st.session_state.setdefault("proxy_input", "")


def render_header() -> None:
    st.markdown(f"<div class='main-header'>📸 {APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)

    with st.expander("ℹ️ Research & Ethical Disclaimer", expanded=False):
        st.markdown(DISCLAIMER_HTML, unsafe_allow_html=True)


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        st.markdown("## 🔍 Target & Scan")
        with st.form("run_form", border=False):
            target_input = st.text_input(
                "Instagram Target",
                value=st.session_state.get("target_input", ""),
                placeholder="username OR reel/post link",
                help="Enter a username (e.g. digraj_sinh) or a direct Reel / Post URL.",
            )

            st.markdown("#### Scan Sources")
            scan_feed = st.checkbox("Profile Timeline / Feed", value=True)
            scan_reels = st.checkbox("Reels Tab (/reels/)", value=True, help="Scan the Reels tab for public and shared reels")
            scan_tagged = st.checkbox("Tagged & Collabs (/tagged/)", value=True, help="Scan tagged content and collaborated posts")

            run_clicked = st.form_submit_button("🚀 Start Scan", use_container_width=True)

        # Anti-429 Rate-Limit Settings
        with st.expander("🔑 Cloud Bypass & Rate Limits (Fix 429)", expanded=False):
            st.caption("Shared cloud servers (AWS / Streamlit Cloud) get HTTP 429 rate-limited by Instagram. Adding your session cookie bypasses this instantly.")

            cookie_default = ""
            try:
                cookie_default = getattr(st, "secrets", {}).get("IG_COOKIE", "") or getattr(st, "secrets", {}).get("SESSION_ID", "")
            except Exception:
                pass

            cookie_input = st.text_input(
                "Instagram sessionid / Cookie",
                value=st.session_state.get("cookie_input", "") or cookie_default,
                type="password",
                help="Paste your sessionid from browser (F12 -> Application -> Cookies -> sessionid). Or set IG_COOKIE in Streamlit Secrets.",
                placeholder="Paste sessionid or full cookie string"
            )

            if cookie_input.strip():
                if st.button("🔍 Verify Cookie Session", use_container_width=True, key="btn_verify_cookie"):
                    with st.spinner("Testing session with Instagram API..."):
                        test_sess = create_session(cookie_str=cookie_input, proxy_url=st.session_state.get("proxy_input", ""))
                        is_ok, msg = validate_instagram_session(test_sess)
                        if is_ok:
                            st.success(f"🟢 **Session Verified:** {msg}")
                        else:
                            st.error(f"🔴 **Session Check:** {msg}")

            with st.expander("❓ How to get sessionid (15 seconds)", expanded=False):
                st.markdown(
                    """
                    1. Open [instagram.com](https://www.instagram.com) in your browser & log in.
                    2. Press **F12** (Developer Tools).
                    3. Click **Application** (Chrome/Edge) or **Storage** (Firefox) tab.
                    4. Under **Cookies** → select `https://www.instagram.com`.
                    5. Find **`sessionid`**, double click its value, copy and paste it above!
                    """
                )

            proxy_default = ""
            try:
                proxy_default = getattr(st, "secrets", {}).get("PROXY", "")
            except Exception:
                pass

            proxy_input = st.text_input(
                "Proxy URL (Optional)",
                value=st.session_state.get("proxy_input", "") or proxy_default,
                help="Optional HTTP/HTTPS/SOCKS5 proxy (e.g. http://user:pass@host:port).",
                placeholder="http://user:pass@host:port"
            )

            scan_delay = st.slider(
                "Pacing delay (seconds)",
                min_value=0.5,
                max_value=4.0,
                value=1.5,
                step=0.5,
                help="Adds a delay between tab scans to avoid triggering rate limits."
            )

        st.divider()
        st.markdown("## 🎨 Display & Playback")
        show_previews = st.toggle("Enable Media Previews", value=True, help="Renders embedded video players and image previews.")
        gallery_cols = st.slider("Gallery columns (Desktop)", min_value=1, max_value=4, value=2, help="On mobile devices, this adapts to 1 column automatically.")
        max_posts = st.slider("Max posts to render", min_value=5, max_value=50, value=15, step=1)

        st.divider()
        st.markdown("## ℹ️ Capabilities")
        st.info(
            """
            - **🎬 Reels & Clips:** Supports Reels tab and direct Reel links.
            - **🎥 Direct MP4 Streams:** Embedded video playback and direct MP4 downloads.
            - **🤝 Collab Posts:** Extracts co-authored posts & cover frames.
            - **🛡️ Rate-Limit Bypass:** Supports session cookies, proxies, and adaptive pacing.
            - **📱 Fully Responsive:** Optimized for desktop, tablet, and mobile screens.
            """
        )

        col_a, col_b = st.columns(2)
        reset_clicked = col_a.button("Reset", use_container_width=True)
        clear_cache_clicked = col_b.button("Clear Cache", use_container_width=True)

    return {
        "target_input": target_input,
        "run_clicked": run_clicked,
        "reset_clicked": reset_clicked,
        "clear_cache_clicked": clear_cache_clicked,
        "scan_feed": scan_feed,
        "scan_reels": scan_reels,
        "scan_tagged": scan_tagged,
        "show_previews": show_previews,
        "gallery_cols": int(gallery_cols),
        "max_posts": int(max_posts),
        "cookie_input": cookie_input,
        "proxy_input": proxy_input,
        "scan_delay": float(scan_delay),
    }


def render_empty_state() -> None:
    st.markdown(
        """
        <div class='card'>
          <h3 style='margin-top:0; font-size: clamp(1.15rem, 2.5vw, 1.4rem);'>Ready to Scan</h3>
          <p style='color: #666; font-size: clamp(0.85rem, 1.8vw, 0.95rem);'>
            Enter an Instagram username or a direct Reel/Post link in the sidebar to extract exposed media assets,
            including <strong>Reels, Videos, Thumbnails, and Collab Images</strong>.
          </p>
          <ul style='font-size: clamp(0.85rem, 1.8vw, 0.95rem); line-height: 1.6; padding-left: 20px;'>
            <li><strong>Reels & Video Streams:</strong> Direct MP4 playback & downloads.</li>
            <li><strong>Collab Posts:</strong> Co-authored media exposed via timeline or tagged connections.</li>
            <li><strong>Multi-Device Ready:</strong> Full responsive layout across desktop, tablet, and mobile.</li>
            <li><strong>Cloud Rate-Limit Protection:</strong> Built-in cookie and proxy support to bypass HTTP 429.</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_run_status() -> None:
    if st.session_state.get("run_error"):
        err = str(st.session_state['run_error'])
        if "429" in err:
            st.markdown(
                """
                <div class='error-box' style='border-left-color: #e0245e;'>
                  <h4 style='margin:0 0 8px 0; color: #dc3545;'>🚫 Instagram Rate Limit (HTTP 429) on Cloud Server</h4>
                  <p style='margin:0 0 10px 0;'>
                    Streamlit Community Cloud runs on shared AWS servers whose public IP addresses are restricted by Instagram for anonymous browsing requests.
                  </p>
                  <strong>💡 How to bypass this immediately:</strong>
                  <ol style='margin: 6px 0 0 0; padding-left: 22px; line-height: 1.7;'>
                    <li>Open the sidebar → expand <strong>🔑 Cloud Bypass & Rate Limits (Fix 429)</strong>.</li>
                    <li>Paste your Instagram <strong><code>sessionid</code></strong> cookie (from your browser DevTools → Application → Cookies → sessionid).</li>
                    <li>Click <strong>🔍 Verify Cookie Session</strong> to confirm it works.</li>
                    <li><em>(Permanent fix)</em> In Streamlit Cloud: Click <strong>App Settings</strong> → <strong>Secrets</strong> and add:
                      <br><code>IG_COOKIE = "sessionid=YOUR_SESSION_ID"</code>
                    </li>
                  </ol>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif "401" in err or "403" in err or "expired" in err.lower() or "login" in err.lower():
            st.markdown(
                f"""
                <div class='error-box' style='border-left-color: #dc3545;'>
                  <h4 style='margin:0 0 8px 0; color: #dc3545;'>🔴 Instagram Cookie Expired or Invalid</h4>
                  <p style='margin:0 0 10px 0;'>
                    {err}
                  </p>
                  <strong>💡 How to refresh your cookie:</strong>
                  <ol style='margin: 6px 0 0 0; padding-left: 22px; line-height: 1.7;'>
                    <li>Log into your account at <a href='https://www.instagram.com' target='_blank'>instagram.com</a> in your browser.</li>
                    <li>Press <strong>F12</strong> → <strong>Application</strong> → <strong>Cookies</strong> → <code>https://www.instagram.com</code>.</li>
                    <li>Copy the fresh <strong><code>sessionid</code></strong> value and update it in the sidebar.</li>
                  </ol>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class='error-box'>
                  <strong>⚠️ Notice:</strong> {err}
                </div>
                """,
                unsafe_allow_html=True,
            )

    media_found = st.session_state.get("media_found", None)
    if media_found is False and not st.session_state.get("run_error"):
        st.markdown(
            """
            <div class='info-box'>
              <strong>ℹ️ NO MEDIA FOUND:</strong> No exposed media assets were detected for this target.<br>
              Account may be strictly private (and not followed by your session), empty, or rate-limited.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_results(target_name: str, media_items: List[Dict[str, Any]], ui: Dict[str, Any]) -> None:
    videos = [m for m in media_items if m.get("kind") == "video"]
    images = [m for m in media_items if m.get("kind") != "video"]

    by_post: Dict[str, List[Dict[str, Any]]] = {}
    for m in media_items:
        pid = m.get("post_id", "unknown")
        by_post.setdefault(pid, []).append(m)

    post_ids = sorted(by_post.keys())
    post_count = len(post_ids)
    total_count = len(media_items)

    st.markdown(
        f"""
        <div class='success-box'>
          <strong>✅ Extracted {total_count} media assets across {post_count} posts</strong>
          ({len(videos)} Videos/Reels, {len(images)} Images & Covers)
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_overview, tab_gallery, tab_table, tab_downloads = st.tabs(
        ["📊 Overview", "🎬 Gallery & Players", "📋 Table View", "📥 Downloads"]
    )

    with tab_overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Media", total_count)
        c2.metric("🎬 Videos / Reels", len(videos))
        c3.metric("📷 Images & Covers", len(images))
        c4.metric("📌 Unique Posts", post_count)

        st.divider()
        if bool(ui.get("show_previews")):
            st.subheader("Featured Highlights")
            preview_items = (videos[:3] + images[:3])[:6]
            cols = st.columns(min(3, len(preview_items)) or 1)
            for i, it in enumerate(preview_items):
                with cols[i % len(cols)]:
                    st.caption(f"{it.get('type_label')} • Post {it.get('post_id')} • {it.get('resolution')}")
                    if it.get("kind") == "video":
                        st.video(it.get("url"))
                    else:
                        img = load_image(it.get("url"))
                        if img:
                            st.image(img, use_container_width=True)
                        else:
                            st.info("Preview loading...")
        else:
            st.info("Previews are currently disabled in the sidebar for maximum speed.")

    with tab_gallery:
        st.subheader("Media Gallery & Players")
        f1, f2, f3 = st.columns([2, 2, 2])
        with f1:
            media_type_filter = st.selectbox("Filter Media Type", ["All Media", "🎬 Videos & Reels Only", "📷 Images Only"])
        with f2:
            post_filter = st.selectbox("Filter by Post", ["All Posts"] + post_ids)
        with f3:
            show_url_box = st.toggle("Show Direct CDN URLs", value=False)

        # Filter items
        filtered_items = media_items
        if media_type_filter == "🎬 Videos & Reels Only":
            filtered_items = [m for m in filtered_items if m.get("kind") == "video"]
        elif media_type_filter == "📷 Images Only":
            filtered_items = [m for m in filtered_items if m.get("kind") != "video"]

        if post_filter != "All Posts":
            filtered_items = [m for m in filtered_items if m.get("post_id") == post_filter]

        # Group by post
        render_posts: Dict[str, List[Dict[str, Any]]] = {}
        for m in filtered_items:
            render_posts.setdefault(m.get("post_id", "unknown"), []).append(m)

        max_posts = int(ui.get("max_posts", 15))
        gallery_cols = int(ui.get("gallery_cols", 2))
        show_previews = bool(ui.get("show_previews"))

        sorted_post_keys = sorted(render_posts.keys())[:max_posts]

        for p_idx, pid in enumerate(sorted_post_keys, 1):
            items_for_p = render_posts[pid]
            first_it = items_for_p[0]
            shortcode = first_it.get("shortcode")
            caption = first_it.get("caption", "").strip()
            source = first_it.get("source", "")

            collabs_list = first_it.get("collabs", [])
            collab_badge_html = f" • <strong>Collab:</strong> <span style='color:#28a745; font-weight:700;'>@{', @'.join(collabs_list)}</span>" if collabs_list else ""

            st.markdown(
                f"""
                <div class='post-card'>
                  <div class='post-header-flex'>
                    <h3 style='margin:0; font-size: clamp(1.05rem, 2.2vw, 1.25rem);'>📌 Post #{p_idx} — ID: {pid}</h3>
                    {f"<a href='https://www.instagram.com/p/{shortcode}/' target='_blank' style='font-size: 0.85rem; font-weight: 600; text-decoration: none;'>🔗 View on Instagram ({shortcode})</a>" if shortcode else ""}
                  </div>
                  <p style='margin:4px 0 0 0; color:#666; font-size: clamp(0.8rem, 1.8vw, 0.9rem);'>
                    <strong>Source:</strong> {source} • <strong>Assets:</strong> {len(items_for_p)}{collab_badge_html}
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if caption:
                st.markdown(f"<div class='caption-box'><strong>Caption:</strong> {caption}</div>", unsafe_allow_html=True)

            cols = st.columns(gallery_cols)
            for j, it in enumerate(items_for_p):
                with cols[j % len(cols)]:
                    k = it.get("kind")
                    res = it.get("resolution", "?")
                    type_label = it.get("type_label", "Media")
                    url = it.get("url")

                    # Badges
                    if k == "video":
                        badge_class = "badge-video"
                    elif "cover" in k:
                        badge_class = "badge-cover"
                    else:
                        badge_class = "badge-image"

                    item_collabs = it.get("collabs", [])
                    item_collab_badge = f"<span class='badge-cover' style='background-color:#28a745;'>🤝 @{', @'.join(item_collabs)}</span> " if item_collabs else ""

                    st.markdown(f"{item_collab_badge}<span class='{badge_class}'>{type_label}</span> <strong>{res}</strong>", unsafe_allow_html=True)

                    if show_previews:
                        if k == "video":
                            st.video(url)
                        else:
                            img = load_image(url)
                            if img:
                                st.image(img, use_container_width=True)
                            else:
                                st.caption("Image preview unavailable")

                    if show_url_box:
                        st.code(url, language="text")

                    # Download button
                    ext, mime = infer_download_meta(url, k, res)
                    st.download_button(
                        label=f"⬇️ Download {ext.upper()}",
                        data=url,
                        file_name=f"{target_name}_{pid}_{j+1}.{ext}",
                        mime=mime,
                        key=f"dl_{pid}_{j}",
                        use_container_width=True,
                    )

            st.divider()

    with tab_table:
        st.subheader("Interactive Asset Table")
        table_rows = [
            {
                "Post ID": m.get("post_id"),
                "Type": m.get("type_label"),
                "Resolution": m.get("resolution"),
                "Collaborators": ", ".join(m.get("collabs", [])) if m.get("collabs") else "None",
                "Source": m.get("source"),
                "Shortcode": m.get("shortcode") or "N/A",
                "Caption": m.get("caption", "")[:60],
                "URL": m.get("url")
            }
            for m in media_items
        ]
        st.dataframe(table_rows, use_container_width=True, hide_index=True)

    with tab_downloads:
        st.subheader("Bulk Export & Downloads")
        st.write("Download all extracted asset URLs in your preferred format.")

        formatted_txt = format_results_txt(media_items, target_name)
        formatted_csv = format_results_csv(media_items, target_name)
        formatted_json = format_results_json(media_items, target_name)

        d1, d2, d3 = st.columns(3)
        d1.download_button(
            label="📄 Download TXT Report",
            data=formatted_txt,
            file_name=f"{target_name}_media_report.txt",
            mime="text/plain",
            key="btn_dl_txt",
            use_container_width=True,
        )
        d2.download_button(
            label="📊 Download CSV Table",
            data=formatted_csv,
            file_name=f"{target_name}_media_table.csv",
            mime="text/csv",
            key="btn_dl_csv",
            use_container_width=True,
        )
        d3.download_button(
            label="📋 Download JSON Dump",
            data=formatted_json,
            file_name=f"{target_name}_media_data.json",
            mime="application/json",
            key="btn_dl_json",
            use_container_width=True,
        )

        st.divider()
        st.subheader("Report Preview")
        st.text_area("Results Summary", value=formatted_txt, height=350, disabled=True)


def main() -> None:
    _init_state()
    render_header()
    ui = render_sidebar()

    if ui.get("clear_cache_clicked"):
        load_image.clear()
        fetch_media_bytes.clear()
        st.toast("Media cache cleared!")

    if ui.get("reset_clicked"):
        st.session_state["target_input"] = ""
        st.session_state["last_run_target"] = ""
        st.session_state["run_error"] = None
        st.session_state["media_found"] = None
        st.session_state["media_items"] = None
        st.session_state["last_run_ts"] = None
        st.rerun()

    if ui.get("run_clicked"):
        raw_in = str(ui.get("target_input", "")).strip()
        st.session_state["target_input"] = raw_in
        st.session_state["run_error"] = None
        st.session_state["media_found"] = None
        st.session_state["media_items"] = None

        cookie_val = str(ui.get("cookie_input", "")).strip()
        proxy_val = str(ui.get("proxy_input", "")).strip()
        st.session_state["cookie_input"] = cookie_val
        st.session_state["proxy_input"] = proxy_val

        if not raw_in:
            st.session_state["run_error"] = "Target username or URL is required."
            st.rerun()

        target_info = parse_target_input(raw_in)
        target_name = target_info.get("username") or target_info.get("shortcode") or raw_in
        st.session_state["last_run_target"] = target_name
        st.session_state["last_run_ts"] = int(time.time())

        with st.spinner(f"Extracting Reels, Videos & Images for {target_name}..."):
            items, error = scan_target(
                target_info,
                scan_reels=bool(ui.get("scan_reels")),
                scan_tagged=bool(ui.get("scan_tagged")),
                scan_feed=bool(ui.get("scan_feed")),
                cookie_str=cookie_val,
                proxy_url=proxy_val,
                delay=float(ui.get("scan_delay", 1.5))
            )

            if error:
                st.session_state["run_error"] = error

            if not items:
                st.session_state["media_found"] = False
                st.session_state["media_items"] = None
            else:
                st.session_state["media_found"] = True
                st.session_state["media_items"] = items

            st.rerun()

    target_name = st.session_state.get("last_run_target") or ""
    media_items = st.session_state.get("media_items")

    if not target_name and not media_items and st.session_state.get("media_found") is None and not st.session_state.get("run_error"):
        render_empty_state()
    else:
        render_run_status()
        if media_items:
            render_results(target_name, media_items, ui)

    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #888; font-size: 0.85em; margin-top: 20px;'>
          <p>InstaTrace © 2026 | Enhanced Reels, Videos & Collab Media Extractor | Research & Educational Use</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()