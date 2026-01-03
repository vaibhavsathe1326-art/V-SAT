import streamlit as st
import yt_dlp
import os
import json
from datetime import datetime
from pathlib import Path

# ---------------- CONFIG ----------------
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="V-SAT | Engineered Media Engine",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://github.com/VaibhavSathe/V-SAT',
        'Report a bug': 'https://github.com/VaibhavSathe/V-SAT/issues',
        'About': "### V-SAT Media Engine v2.0\nProfessional YouTube Downloader"
    }
)

# ---------------- SESSION STATE ----------------
if 'download_history' not in st.session_state:
    st.session_state.download_history = []
if 'total_downloads' not in st.session_state:
    st.session_state.total_downloads = 0
if 'engine_mode' not in st.session_state:
    st.session_state.engine_mode = "video"

# ---------------- V-SAT ENHANCED CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    :root {
        --vsat-primary: #6366f1;
        --vsat-secondary: #8b5cf6;
        --vsat-accent: #3b82f6;
        --vsat-dark: #0a0a15;
        --vsat-darker: #05050d;
        --vsat-card: rgba(25, 25, 45, 0.85);
        --vsat-glow: rgba(99, 102, 241, 0.6);
    }
    
    .stApp {
        background-color: var(--vsat-darker);
        background-image: 
            radial-gradient(ellipse at 15% 10%, rgba(99, 102, 241, 0.18) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 90%, rgba(139, 92, 246, 0.15) 0%, transparent 55%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    /* Hide Default Elements */
    footer {visibility: hidden;}
    
    /* V-SAT Header Design */
    .vsat-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        position: relative;
    }
    
    .vsat-logo {
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 15%, #a5b4fc 35%, var(--vsat-primary) 60%, var(--vsat-secondary) 85%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
        margin: 0;
        text-shadow: 0 0 30px var(--vsat-glow);
    }
    
    .vsat-tagline {
        background: linear-gradient(90deg, var(--vsat-primary), var(--vsat-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-top: -10px;
        margin-bottom: 1rem;
    }
    
    /* Professional Cards */
    .vsat-card {
        background: var(--vsat-card);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1.8rem;
        backdrop-filter: blur(15px);
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
    }
    
    /* Stats Cards */
    .stat-card {
        background: rgba(30, 30, 55, 0.8);
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.15);
        height: 100%;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, var(--vsat-primary), var(--vsat-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    /* Input Styling */
    .stTextInput input {
        background: rgba(20, 20, 40, 0.9) !important;
        border: 2px solid rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.9rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--vsat-primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Tabs Styling - FIXED */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 10px !important;
        margin: 0 0.2rem !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, var(--vsat-primary), var(--vsat-secondary)) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    button[data-baseweb="tab"][aria-selected="false"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Select Box Styling */
    div[data-baseweb="select"] {
        background: rgba(20, 20, 40, 0.9) !important;
        border: 2px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
    }
    
    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(90deg, var(--vsat-primary), var(--vsat-secondary)) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        border-radius: 12px !important;
        letter-spacing: 1px !important;
        margin-top: 1.5rem !important;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(99, 102, 241, 0.6) !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--vsat-primary), var(--vsat-secondary)) !important;
        border-radius: 8px !important;
    }
    
    /* Footer Styling */
    .vsat-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .creator-text {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #ffffff;
        text-shadow: 0 0 8px rgba(99, 102, 241, 0.8);
        margin-bottom: 0.3rem;
    }
    
    .version-text {
        color: rgba(255, 255, 255, 0.35);
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        font-family: 'Courier New', monospace;
    }
    
    /* Quality Badges */
    .quality-badge {
        display: inline-block;
        background: linear-gradient(90deg, var(--vsat-primary), var(--vsat-secondary));
        color: white;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        margin: 0.3rem 0.3rem 0.3rem 0;
    }
    
    /* Thumbnail Container */
    .thumbnail-container {
        border-radius: 12px;
        overflow: hidden;
        margin: 1rem 0;
        border: 2px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- V-SAT HEADER ----------------
st.markdown("""
<div class="vsat-header">
    <h1 class="vsat-logo">V-SAT</h1>
    <div class="vsat-tagline">ENGINEERED MEDIA ENGINE</div>
</div>
""", unsafe_allow_html=True)

# ---------------- QUICK STATS ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_files = len([f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))])
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{total_files}</div>
        <div class="stat-label">FILES STORED</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_size = sum(os.path.getsize(os.path.join(DOWNLOAD_DIR, f)) for f in os.listdir(DOWNLOAD_DIR) 
                    if os.path.isfile(os.path.join(DOWNLOAD_DIR, f)))
    total_size_mb = total_size / (1024 * 1024)
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{total_size_mb:.1f}MB</div>
        <div class="stat-label">STORAGE USED</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{st.session_state.total_downloads}</div>
        <div class="stat-label">DOWNLOADS</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">v2.0</div>
        <div class="stat-label">ENGINE VERSION</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- URL INPUT CARD ----------------
st.markdown('<div class="vsat-card">', unsafe_allow_html=True)
st.markdown("### 🔗 MEDIA SOURCE URL")
url = st.text_input(
    "Paste YouTube video or playlist link",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed"
)

# Thumbnail Preview
if url and ('youtube.com' in url or 'youtu.be' in url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and 'thumbnail' in info:
                st.markdown('<div class="thumbnail-container">', unsafe_allow_html=True)
                st.image(info.get('thumbnail'), use_container_width=True, 
                        caption=f"📺 {info.get('title', 'No title')[:50]}...")
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.caption(f"*Could not load thumbnail: {str(e)[:50]}...*")
elif url:
    st.warning("⚠️ Please enter a valid YouTube URL")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ENGINE CONFIGURATION CARD ----------------
st.markdown('<div class="vsat-card">', unsafe_allow_html=True)
st.markdown("### ⚙️ ENGINE CONFIGURATION")

# Create tabs with proper labels
tab1, tab2 = st.tabs(["🚀 VIDEO ENGINE", "🎵 AUDIO ENGINE"])

with tab1:
    st.markdown("##### Select Video Quality")
    v_res = st.selectbox(
        "Video Resolution",
        [
            "🎯 Best Available (Auto)",
            "📺 1080p Full HD", 
            "📹 720p HD", 
            "📱 480p SD"
        ],
        key="video_quality",
        label_visibility="collapsed"
    )
    
    # Show selected quality badge
    if "Best" in v_res:
        st.markdown('<span class="quality-badge">Auto Select</span>', unsafe_allow_html=True)
    elif "1080" in v_res:
        st.markdown('<span class="quality-badge">1080p Full HD</span>', unsafe_allow_html=True)
    elif "720" in v_res:
        st.markdown('<span class="quality-badge">720p HD</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="quality-badge">480p SD</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Video formats: MP4 with H.264 encoding")

with tab2:
    st.markdown("##### Select Audio Quality")
    a_bit = st.selectbox(
        "Audio Bitrate",
        [
            "🎵 320kbps (Lossless)",
            "🎵 192kbps (High)", 
            "🎵 128kbps (Standard)"
        ],
        key="audio_quality",
        label_visibility="collapsed"
    )
    
    # Show selected audio quality badge
    if "320" in a_bit:
        st.markdown('<span class="quality-badge">Studio Quality</span>', unsafe_allow_html=True)
    elif "192" in a_bit:
        st.markdown('<span class="quality-badge">High Quality</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="quality-badge">Standard Quality</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Audio format: MP3 with AAC encoding")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DOWNLOAD BUTTON ----------------
if st.button("🚀 IGNITE V-SAT ENGINE", key="download_btn"):
    if not url:
        st.error("⚠️ Please provide a valid YouTube URL")
    else:
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        # Configure based on active tab
        current_tab = st.session_state.get('current_tab', 'video')
        
        if current_tab == 'video' or tab1._active:  # Video Engine selected
            if "Best" in v_res:
                ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'}
            elif "1080" in v_res:
                ydl_opts = {'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'}
            elif "720" in v_res:
                ydl_opts = {'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'}
            else:
                ydl_opts = {'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'}
            format_type = "Video"
        else:  # Audio Engine selected
            bitrate = a_bit.split(" ")[0].replace("🎵", "").replace("kbps", "").strip()
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
            }
            format_type = "Audio"
        
        # Add common options with better error handling
        ydl_opts.update({
            'outtmpl': os.path.join(DOWNLOAD_DIR, 'V-SAT_%(title).100s.%(ext)s'),
            'progress_hooks': [lambda d: update_progress(d, progress_bar, status_container)],
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'merge_output_format': 'mp4' if format_type == "Video" else None,
            'socket_timeout': 30,
            'extract_flat': False,
        })
        
        try:
            status_container.info("🚀 Initializing V-SAT Engine...")
            
            # First verify we can extract info
            with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as test_ydl:
                info = test_ydl.extract_info(url, download=False)
            
            if not info:
                raise Exception("Could not extract video information. URL might be invalid or video might be unavailable.")
            
            title = info.get('title', 'Unknown Video')
            
            # Now proceed with download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                download_result = ydl.download([url])
            
            # Update session state
            st.session_state.total_downloads += 1
            st.session_state.download_history.append({
                'title': title,
                'url': url,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'format': format_type
            })
            
            # Success message
            progress_bar.progress(100)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.success(f"✅ Download Complete: **{title[:60]}...**")
                st.info(f"📁 Saved to: `{os.path.abspath(DOWNLOAD_DIR)}`")
            
            with col2:
                if st.button("📂 Open Folder", key="open_folder"):
                    os.startfile(os.path.abspath(DOWNLOAD_DIR))
            
            st.balloons()
            
        except yt_dlp.utils.DownloadError as e:
            st.error(f"❌ Download Error: {str(e)}")
            st.info("💡 **Possible causes:**")
            st.markdown("""
            - Video is private or age-restricted
            - URL is incorrect or video has been removed
            - Region restrictions are blocking access
            - Try copying the URL directly from YouTube
            """)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 **Troubleshooting Tips:**")
            st.markdown("""
            1. **Check your internet connection**
            2. **Verify the URL is correct** - copy directly from YouTube
            3. **Try a different video** - some videos have restrictions
            4. **Ensure video is not private/age-restricted**
            5. **Try using VPN** if there are region restrictions
            """)

def update_progress(d, progress_bar, status_container):
    """Update progress bar and status"""
    if d['status'] == 'downloading':
        if d.get('total_bytes'):
            percent = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
            progress_bar.progress(percent)
            
            speed = d.get('speed', 0)
            speed_mb = speed / (1024 * 1024) if speed else 0
            
            status_container.info(f"""
            **V-SAT Engine Active...**  
            📊 Progress: {percent}%  
            🚀 Speed: {speed_mb:.1f} MB/s  
            📝 Processing: {d.get('filename', '').split('/')[-1][:40]}...
            """)
    elif d['status'] == 'finished':
        status_container.success("✅ Processing complete! Finalizing download...")

# ---------------- ADVANCED OPTIONS ----------------
with st.expander("⚙️ ADVANCED ENGINE SETTINGS", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Keep original filename", value=True, key="keep_filename")
        st.checkbox("Skip existing files", value=True, key="skip_existing")
    
    with col2:
        st.checkbox("Extract subtitles", value=False, key="extract_subs")
        st.checkbox("Add metadata", value=True, key="add_metadata")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.download_history = []
            st.session_state.total_downloads = 0
            st.success("History cleared!")
    
    with col2:
        if st.button("🧹 Clean Folder", use_container_width=True):
            deleted_count = 0
            for f in os.listdir(DOWNLOAD_DIR):
                try:
                    os.remove(os.path.join(DOWNLOAD_DIR, f))
                    deleted_count += 1
                except:
                    pass
            st.success(f"Cleared {deleted_count} files from downloads folder!")

# ---------------- V-SAT FOOTER ----------------
st.markdown("""
<div class="vsat-footer">
    <div class="creator-text">CREATED BY VAIBHAV SATHE</div>
    <div class="version-text">V-SAT ENGINE v2.0 • MEDIA TECHNOLOGIES • PREMIUM BUILD</div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR (NOW VISIBLE) ----------------
with st.sidebar:
    st.markdown("<h2 style='color:#6366f1; text-align: center;'>🔧 V-SAT TOOLS</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Folder info
    st.markdown("### 📁 Download Folder")
    folder_path = os.path.abspath(DOWNLOAD_DIR)
    st.code(folder_path, language="text")
    
    if st.button("📂 Open Downloads", use_container_width=True):
        os.startfile(folder_path)
        st.toast("Opened downloads folder!")
    
    if st.button("🗑️ Clear All Downloads", use_container_width=True):
        for f in os.listdir(DOWNLOAD_DIR):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, f))
            except:
                pass
        st.success("All downloads cleared!")
        st.rerun()
    
    st.markdown("---")
    
    # Recent Downloads
    st.markdown("### 📥 Recent Downloads")
    if st.session_state.download_history:
        for item in reversed(st.session_state.download_history[-3:]):
            st.markdown(f"""
            <div style="background: rgba(99, 102, 241, 0.1); padding: 10px; border-radius: 8px; margin: 5px 0;">
                <div style="font-weight: 600;">{item['title'][:40]}...</div>
                <div style="font-size: 0.8rem; color: #aaa;">{item['timestamp']}</div>
                <div style="font-size: 0.8rem; color: #6366f1;">{item['format']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No downloads yet")
    
    st.markdown("---")
    
    # App Info
    st.markdown("### ℹ️ About V-SAT")
    st.markdown("""
    **Version:** 2.0  
    **Developer:** Vaibhav Sathe  
    **Engine:** yt-dlp + FFmpeg  
    **Formats:** MP4, MP3  
    
    *For personal use only.*
    """)