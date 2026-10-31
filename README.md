# InstaTrace  
**Private Instagram Media Extractor (Reels, Videos, Collabs & Images POC)**

<p align="center">
  <img src="https://img.shields.io/badge/status-research_poc-orange?style=for-the-badge&logo=instagram&logoColor=white&labelColor=000" alt="Status: Research POC">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/features-reels%20%2B%20videos%20%2B%20photos-green?style=for-the-badge" alt="Features: Reels, Videos, Photos">
  <img src="https://img.shields.io/badge/responsive-desktop%20%7C%20tablet%20%7C%20mobile-blue?style=for-the-badge" alt="Responsive Design">
</p>

**⚠️ IMPORTANT LEGAL & ETHICAL NOTICE**  
This tool is strictly for **security research, forensics, and educational purposes**.
Only test accounts you own or have explicit authorization to audit.

---

## Capabilities & Enhancements

- **📱 Fully Responsive Across All Devices:**
  - Optimized for **Desktops, Laptops, Tablets, and Mobile Phones**.
  - Fluid typography (`clamp`), responsive metric grids, touch-friendly buttons (≥44px), and adaptive navigation tabs.
  - Automatically collapses sidebar on mobile screens (`initial_sidebar_state="auto"`).
  - Prevents horizontal overflow and cut-off text on long CDN URLs and captions.
- **🎬 Reels & Video Support:**
  - Scans both the main profile timeline and the `/reels/` tab.
  - Supports direct Reel (`/reel/CODE`) and Post (`/p/CODE`) URLs.
  - Extracts direct MP4 CDN video streams with native embedded playback in the web UI.
  - Extracts Reel cover poster frames and video thumbnails.
- **🤝 Collab & Tagged Posts:**
  - Inspects `/tagged/` and shared timeline edges for co-authored / collaborative posts.
- **📷 High-Resolution Photos & Carousels:**
  - Extracts full-resolution candidate images and sidecars.
- **🖥️ Streamlit Web App:**
  - In-browser MP4 video players and photo galleries.
  - Filter by media type (Videos/Reels vs Images), post ID, and source.
  - Bulk exports to **TXT**, **CSV**, and **JSON**.
  - Direct individual asset downloads (`.mp4`, `.jpg`).

---

## How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Launch the Streamlit application:
```bash
python -m streamlit run InstaTrace.py
```

3. Open your browser at `http://localhost:8502` (or `http://localhost:8501`).
