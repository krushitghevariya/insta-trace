#!/usr/bin/env python3
"""
InstaTrace – Instagram Private & Collab Media Extractor (2025/2026 POC)
Streamlit Web Interface supporting Images, Videos, and Reels
Fully responsive across desktop, laptop, tablet, and mobile screens.
FOR SECURITY RESEARCH / EDUCATIONAL USE ONLY
"""

import streamlit as st
import requests
import json
import time
import re
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
        /* Tablet: Allow horizontal column containers to wrap */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.75rem 0.5rem !important;
        }
    }

    @media (max-width: 768px) {
        /* Tablet & Mobile: 2 columns per row */
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
        }
        
        /* Sidebar tap padding */
        [data-testid="stSidebar"] {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }

    @media (max-width: 540px) {
        /* Mobile phone: full width column stacking */
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* Preserve 2-column layout for small buttons inside sidebar */
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


def create_session() -> requests.Session:
    """Create a persistent session with mobile emulating headers."""
    session = requests.Session()
    session.headers.update({
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'upgrade-insecure-requests': '1',
    })
    return session


def fetch_tab_html(session: requests.Session, username: str, tab_path: str = "") -> Tuple[Optional[str], Optional[str]]:
    """Fetch profile tab HTML (feed, reels, tagged)."""
    url = f"https://www.instagram.com/{username}/{tab_path}"
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            return r.text, None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, f"Connection error: {e}"


def fetch_direct_url(session: requests.Session, url: str) -> Tuple[Optional[str], Optional[str]]:
    """Fetch direct post or reel page."""
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            return r.text, None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, f"Connection error: {e}"


def extract_media_from_node(node: dict, acc: List[Dict[str, Any]], current_pid: Optional[str] = None, source: str = "") -> None:
    """Extract photos, videos, and reels from a JSON dictionary node."""
    if not isinstance(node, dict):
        return

    pid = node.get("pk") or node.get("id") or current_pid or "unknown"
    pid = str(pid).replace("POLARIS_", "")

    shortcode = node.get("code") or node.get("shortcode")
    if not shortcode and pid.isdigit():
        try:
            shortcode = id_to_shortcode(int(pid))
        except Exception:
            shortcode = None

    media_type = node.get("media_type")  # 1=image, 2=video, 8=carousel
    product_type = str(node.get("product_type", "")).lower()  # "clips", "feed", etc.
    typename = str(node.get("__typename", "")).lower()
    is_video_node = (
        media_type == 2 or
        product_type == "clips" or
        "video" in typename or
        "video" in str(node.get("__isXIGPolarisMedia", "")).lower()
    )

    caption = ""
    cap_obj = node.get("caption")
    if isinstance(cap_obj, dict):
        caption = cap_obj.get("text", "") or ""
    elif isinstance(cap_obj, str):
        caption = cap_obj

    # 1. Video versions (highest-quality stream)
    if "video_versions" in node and isinstance(node["video_versions"], list) and node["video_versions"]:
        best_v = None
        best_v_score = -1
        for v in node["video_versions"]:
            if not isinstance(v, dict) or not v.get("url"):
                continue
            w = v.get("width")
            h = v.get("height")
            score = (w * h) if isinstance(w, int) and isinstance(h, int) else 0
            if score > best_v_score:
                best_v_score = score
                best_v = v

        if best_v and best_v.get("url"):
            w = best_v.get("width", "?")
            h = best_v.get("height", "?")
            label = "Reel (Video)" if product_type == "clips" else "Video"
            acc.append({
                "post_id": pid,
                "shortcode": shortcode,
                "kind": "video",
                "type_label": label,
                "resolution": f"{w}×{h}",
                "url": decode_url(best_v["url"]),
                "caption": caption,
                "source": source,
            })

    # 2. Direct video_url
    if "video_url" in node and isinstance(node["video_url"], str) and node["video_url"]:
        w = node.get("video_width") or node.get("dimensions", {}).get("width") or "?"
        h = node.get("video_height") or node.get("dimensions", {}).get("height") or "?"
        label = "Reel (Video)" if product_type == "clips" else "Video"
        acc.append({
            "post_id": pid,
            "shortcode": shortcode,
            "kind": "video",
            "type_label": label,
            "resolution": f"{w}×{h}",
            "url": decode_url(node["video_url"]),
            "caption": caption,
            "source": source,
        })

    # 3. Video resources list (GraphQL)
    if "video_resources" in node and isinstance(node["video_resources"], list):
        for vr in node["video_resources"]:
            if isinstance(vr, dict) and vr.get("src"):
                w = vr.get("config_width", "?")
                h = vr.get("config_height", "?")
                label = "Reel (Video)" if product_type == "clips" else "Video"
                acc.append({
                    "post_id": pid,
                    "shortcode": shortcode,
                    "kind": "video",
                    "type_label": label,
                    "resolution": f"{w}×{h}",
                    "url": decode_url(vr["src"]),
                    "caption": caption,
                    "source": source,
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
                w = cand.get("width")
                h = cand.get("height")
                score = (w * h) if isinstance(w, int) and isinstance(h, int) else 0
                if score > best_cand_score:
                    best_cand_score = score
                    best_cand = cand

            if best_cand and best_cand.get("url"):
                w = best_cand.get("width", "?")
                h = best_cand.get("height", "?")
                if is_video_node:
                    kind = "reel_cover" if product_type == "clips" else "video_cover"
                    label = "Reel Cover Frame" if product_type == "clips" else "Video Thumbnail"
                else:
                    kind = "image"
                    label = "Image"

                acc.append({
                    "post_id": pid,
                    "shortcode": shortcode,
                    "kind": kind,
                    "type_label": label,
                    "resolution": f"{w}×{h}",
                    "url": decode_url(best_cand["url"]),
                    "caption": caption,
                    "source": source,
                })

    # 5. Direct display_uri / display_url
    elif node.get("display_uri") or node.get("display_url"):
        d_url = node.get("display_uri") or node.get("display_url")
        if is_video_node:
            kind = "reel_cover" if product_type == "clips" else "video_cover"
            label = "Reel Cover Frame" if product_type == "clips" else "Video Thumbnail"
        else:
            kind = "image"
            label = "Image"

        acc.append({
            "post_id": pid,
            "shortcode": shortcode,
            "kind": kind,
            "type_label": label,
            "resolution": "Original",
            "url": decode_url(d_url),
            "caption": caption,
            "source": source,
        })


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
    """Extract media from all embedded scripts and regex patterns in the HTML page."""
    if not html:
        return []

    acc: List[Dict[str, Any]] = []
    soup = BeautifulSoup(html, "html.parser")

    # 1. Inspect all script tags
    for script in soup.find_all("script"):
        text = script.string or ""
        if not text:
            continue
        # Check if script might contain timeline, clips, reels, or media items
        if any(term in text for term in ["image_versions2", "video_versions", "video_url", "polaris", "clips", "timeline", "shortcode"]):
            try:
                data = json.loads(text)
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
            })
            existing_urls.add(clean_mp4)

    return acc


def scan_target(target_info: Dict[str, Any], scan_reels: bool = True, scan_tagged: bool = True, scan_feed: bool = True) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Scan the target for feed, reels, and collab posts."""
    session = create_session()
    
    # Pre-warm session to obtain Instagram session cookies
    try:
        session.get("https://www.instagram.com/", timeout=8)
    except Exception:
        pass

    all_media: List[Dict[str, Any]] = []
    errors: List[str] = []

    if target_info["mode"] in ("direct_reel", "direct_post"):
        code = target_info["shortcode"]
        path_type = "reel" if target_info["mode"] == "direct_reel" else "p"
        direct_url = f"https://www.instagram.com/{path_type}/{code}/"
        html, err = fetch_direct_url(session, direct_url)
        if html:
            items = extract_media_from_html(html, source="Direct URL")
            all_media.extend(items)
        if err:
            errors.append(f"Direct fetch: {err}")

    elif target_info["mode"] == "profile":
        username = target_info["username"]
        scan_jobs = []
        if scan_feed:
            scan_jobs.append(("Feed / Timeline", ""))
        if scan_reels:
            scan_jobs.append(("Reels / Clips Tab", "reels/"))
        if scan_tagged:
            scan_jobs.append(("Tagged / Collabs Tab", "tagged/"))

        for label, tab_path in scan_jobs:
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


def format_results_csv(media_items: List[Dict[str, Any]], target_name: str) -> str:
    """Format results as CSV with columns."""
    if not media_items:
        return ""

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Post ID", "Shortcode", "Media Type", "Resolution", "Source", "Caption", "URL"])

    for it in media_items:
        writer.writerow([
            it.get("post_id", ""),
            it.get("shortcode", ""),
            it.get("type_label", ""),
            it.get("resolution", ""),
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
    st.session_state.setdefault("media_found", None)  # None/True/False
    st.session_state.setdefault("media_items", None)
    st.session_state.setdefault("last_run_ts", None)


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
            - **📷 Photos & Carousels:** Highest resolution variants.
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
            <li><strong>Multiple Formats:</strong> Export results as TXT, CSV, or structured JSON.</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_run_status() -> None:
    if st.session_state.get("run_error"):
        st.markdown(
            f"""
            <div class='error-box'>
              <strong>⚠️ Notice:</strong> {st.session_state['run_error']}
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
              Account may be strictly private without collabs/reels, empty, or rate-limited.
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

            st.markdown(
                f"""
                <div class='post-card'>
                  <div class='post-header-flex'>
                    <h3 style='margin:0; font-size: clamp(1.05rem, 2.2vw, 1.25rem);'>📌 Post #{p_idx} — ID: {pid}</h3>
                    {f"<a href='https://www.instagram.com/p/{shortcode}/' target='_blank' style='font-size: 0.85rem; font-weight: 600; text-decoration: none;'>🔗 View on Instagram ({shortcode})</a>" if shortcode else ""}
                  </div>
                  <p style='margin:4px 0 0 0; color:#666; font-size: clamp(0.8rem, 1.8vw, 0.9rem);'>
                    <strong>Source:</strong> {source} • <strong>Assets:</strong> {len(items_for_p)}
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

                    st.markdown(f"<span class='{badge_class}'>{type_label}</span> <strong>{res}</strong>", unsafe_allow_html=True)

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
                scan_feed=bool(ui.get("scan_feed"))
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