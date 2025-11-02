# src/dashboard/app.py
import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="News Analysis Dashboard", layout="wide", page_icon="📰")

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    .article-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    .analysis-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .entity-badge {
        background-color: #ff6b6b;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.2rem;
        font-size: 0.9em;
        font-weight: 500;
    }
    .per-badge {
        background-color: #ee5a6f;
    }
    .org-badge {
        background-color: #4ecdc4;
    }
    .loc-badge {
        background-color: #95e1d3;
    }
    .misc-badge {
        background-color: #f38181;
    }
    h1 {
        background: linear-gradient(120deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    .stats-box {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .confidence-bar {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        height: 25px;
        margin: 0.5rem 0;
    }
    .confidence-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

API_URL = st.secrets.get("API_URL", "http://localhost:8000") if hasattr(st, "secrets") else "http://localhost:8000"

# --------------------
# Helper: load logo safely
# --------------------
def show_logo():
    local_logo = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(local_logo):
        st.sidebar.image(local_logo, width=80)
        return
    # Show emoji with better styling if no logo
    st.sidebar.markdown("""
        <div style='text-align: center; font-size: 4em; margin: 1rem 0;'>
            📰
        </div>
        """, unsafe_allow_html=True)

show_logo()

# --------------------
# Sidebar
# --------------------
st.sidebar.markdown("## 🧭 Navigation")
mode = st.sidebar.radio("", ["📝 Analyze Article", "📡 Live Feed"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; 
                border-radius: 10px; 
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.15);'>
        <h4 style='margin:0; color: white;'>🤖 AI Powered Analytics</h4>
        <p style='margin:0.5rem 0 0 0; font-size: 0.85em; line-height: 1.5;'>
            Advanced NLP models for intelligent content understanding and extraction
        </p>
        <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.3);'>
            <div style='font-size: 0.85em; text-align: left;'>
                ✓ Text Classification<br>
                ✓ Auto Summarization<br>
                ✓ Named Entity Recognition<br>
                ✓ Sentiment Analysis
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.85em; margin-top: 2rem;'>
        💡 <strong>Tip:</strong> Paste longer articles<br>for better analysis results
    </div>
    """, unsafe_allow_html=True)

st.title("🧠 News Analysis Dashboard")
st.markdown("### *Intelligent news processing with AI-powered insights*")
st.markdown("---")

# Initialize session state containers
if "articles" not in st.session_state:
    st.session_state["articles"] = []
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = {}

# --------------------
# Analyze Article Mode
# --------------------
if mode == "📝 Analyze Article":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📄 Paste article text for analysis")
    
    text = st.text_area("", height=240, placeholder="Paste your article text here... (The longer the text, the better the analysis)", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze Article"):
            if not text.strip():
                st.warning("⚠️ Please paste some text")
            else:
                with st.spinner("🤖 Analyzing with AI..."):
                    try:
                        resp = requests.post(f"{API_URL}/analyze", json={"text": text}, timeout=60)
                    except Exception as e:
                        st.error(f"❌ Request failed: {e}")
                    else:
                        if resp.status_code != 200:
                            st.error(f"❌ API error {resp.status_code}: {resp.text}")
                        else:
                            try:
                                data = resp.json()
                            except Exception as e:
                                st.error(f"❌ Invalid JSON from API: {e}")
                                st.text(resp.text)
                            else:
                                st.markdown("---")
                                
                                # Stats overview
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    word_count = len(text.split())
                                    st.markdown(f"""
                                        <div class='stats-box'>
                                            <h2 style='margin:0; color: #2d3436;'>{word_count}</h2>
                                            <p style='margin:0.3rem 0 0 0; color: #636e72; font-size: 0.9em;'>Words Analyzed</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                with col2:
                                    ent_count = len(data.get("entities", []))
                                    st.markdown(f"""
                                        <div class='stats-box'>
                                            <h2 style='margin:0; color: #2d3436;'>{ent_count}</h2>
                                            <p style='margin:0.3rem 0 0 0; color: #636e72; font-size: 0.9em;'>Entities Found</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                with col3:
                                    summary_len = len(data.get("summary", "").split())
                                    st.markdown(f"""
                                        <div class='stats-box'>
                                            <h2 style='margin:0; color: #2d3436;'>{summary_len}</h2>
                                            <p style='margin:0.3rem 0 0 0; color: #636e72; font-size: 0.9em;'>Summary Words</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                st.markdown("")
                                
                                # Prediction section
                                st.markdown("### 🎯 Category Prediction")
                                pred = data.get("prediction", {})
                                label = pred.get('label', 'Unknown')
                                probs = pred.get("probs", [])
                                
                                if probs:
                                    max_prob = max(probs) * 100
                                    st.markdown(f"""
                                        <div class='metric-card'>
                                            <h2 style='margin:0; color: white;'>{label}</h2>
                                            <p style='margin:0.5rem 0 0 0; color: rgba(255,255,255,0.9);'>Primary Category</p>
                                            <div style='margin-top: 1rem;'>
                                                <div class='confidence-bar' style='background: rgba(255,255,255,0.3);'>
                                                    <div class='confidence-fill' style='width: {max_prob}%; background: rgba(255,255,255,0.9); color: #667eea;'>
                                                        {max_prob:.1f}% Confidence
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    st.markdown("#### 📊 Probability Distribution")
                                    df = pd.DataFrame({"Category": ["World","Sports","Business","Sci/Tech"], "Probability": probs})
                                    st.bar_chart(df.set_index("Category"), color="#667eea", height=250)

                                # Summary section
                                st.markdown("### 📋 AI-Generated Summary")
                                st.markdown(f"""
                                    <div style='background-color: #f8f9fa; 
                                                padding: 1.5rem; 
                                                border-radius: 10px; 
                                                border-left: 4px solid #667eea;
                                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                                        <p style='margin: 0; line-height: 1.6;'>{data.get("summary", "")}</p>
                                    </div>
                                    """, unsafe_allow_html=True)

                                # Entities section
                                st.markdown("### 🏷️ Named Entity Recognition")
                                ents = data.get("entities", [])
                                if ents:
                                    # Group entities by type
                                    entity_groups = {}
                                    for e in ents:
                                        eg = e.get('entity_group', 'MISC')
                                        if eg not in entity_groups:
                                            entity_groups[eg] = []
                                        entity_groups[eg].append(e.get('word', ''))
                                    
                                    entity_html = "<div style='padding: 1rem;'>"
                                    for eg, words in entity_groups.items():
                                        badge_class = "entity-badge"
                                        if eg == "PER":
                                            badge_class += " per-badge"
                                        elif eg == "ORG":
                                            badge_class += " org-badge"
                                        elif eg == "LOC":
                                            badge_class += " loc-badge"
                                        else:
                                            badge_class += " misc-badge"
                                        
                                        entity_html += f"<div style='margin-bottom: 1rem;'><strong>{eg}:</strong> "
                                        for word in words:
                                            entity_html += f"<span class='{badge_class}'>{word}</span> "
                                        entity_html += "</div>"
                                    entity_html += "</div>"
                                    st.markdown(entity_html, unsafe_allow_html=True)
                                else:
                                    st.info("ℹ️ No entities found.")

# --------------------
# Live Feed Mode
# --------------------
elif mode == "📡 Live Feed":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📡 Live News Feed")
    with col2:
        if st.button("🔄 Fetch Articles"):
            with st.spinner("📥 Fetching articles..."):
                try:
                    resp = requests.get(f"{API_URL}/fetch_sample", timeout=20)
                except Exception as e:
                    st.error(f"❌ Failed to fetch sample articles: {e}")
                    resp = None

                if resp is None:
                    pass
                elif resp.status_code != 200:
                    st.error(f"❌ API error {resp.status_code}: {resp.text}")
                else:
                    try:
                        articles = resp.json()
                    except Exception as e:
                        st.error(f"❌ Invalid JSON from /fetch_sample: {e}")
                        st.text(resp.text)
                        articles = []
                    st.session_state["articles"] = articles
                    st.success(f"✅ Fetched {len(articles)} articles")

    st.markdown("---")

    articles = st.session_state.get("articles", [])
    if not articles:
        st.markdown("""
            <div style='text-align: center; 
                        padding: 3rem; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 15px; 
                        color: white;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <h2 style='color: white; margin-bottom: 1rem;'>📰 No Articles Loaded</h2>
                <p style='font-size: 1.1em;'>Click 'Fetch Articles' button above to load the latest news</p>
                <p style='font-size: 0.9em; margin-top: 1rem; opacity: 0.9;'>✨ Get instant AI-powered insights on any article</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Show article count
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        padding: 1rem; 
                        border-radius: 10px; 
                        text-align: center;
                        margin-bottom: 1rem;'>
                <strong>📊 {len(articles)} Articles Ready for Analysis</strong>
            </div>
            """, unsafe_allow_html=True)
        
        for i, a in enumerate(articles):
            title = a.get("title", f"Article {i+1}")
            source = a.get("source", "Unknown")
            url = a.get("url") or a.get("link") or ""
            summary = a.get("summary", "")
            text = a.get("text", "") or summary or ""

            st.markdown(f"""
                <div class='article-card'>
                    <div style='display: flex; justify-content: space-between; align-items: start;'>
                        <div style='flex: 1;'>
                            <h3 style='color: white; margin: 0;'>📄 {title}</h3>
                            <p style='color: rgba(255,255,255,0.8); margin: 0.5rem 0; font-size: 0.9em;'>
                                📰 <strong>{source}</strong> • {len(text.split())} words
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if url:
                st.markdown(f"[🔗 Read full article]({url})")
            
            if summary:
                st.markdown(f"""
                    <div style='background-color: #f8f9fa; 
                                padding: 1rem; 
                                border-radius: 8px; 
                                margin: 0.5rem 0;
                                border-left: 3px solid #667eea;'>
                        {summary}
                    </div>
                    """, unsafe_allow_html=True)

            analyze_key = f"analyze_btn_{i}"
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"🔍 Analyze Article #{i+1}", key=analyze_key):
                    st.session_state["analysis_results"].pop(str(i), None)
                    with st.spinner("🤖 Analyzing article..."):
                        try:
                            resp = requests.post(f"{API_URL}/analyze", json={"text": text}, timeout=60)
                        except Exception as e:
                            st.error(f"❌ Request failed: {e}")
                            continue

                        if resp.status_code != 200:
                            st.error(f"❌ API error {resp.status_code}: {resp.text}")
                            continue

                        try:
                            data = resp.json()
                        except Exception as e:
                            st.error(f"❌ Invalid JSON from analyze: {e}")
                            st.text(resp.text)
                            continue

                        st.session_state["analysis_results"][str(i)] = data

            result = st.session_state["analysis_results"].get(str(i))
            if result:
                st.markdown("""
                    <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                                padding: 1.5rem; 
                                border-radius: 12px; 
                                margin: 1rem 0;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    """, unsafe_allow_html=True)
                
                pred = result.get("prediction", {})
                label = pred.get('label', 'Unknown')
                probs = pred.get("probs", [])
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if probs:
                        max_prob = max(probs) * 100
                        st.markdown(f"""
                            <div style='background: white; padding: 1rem; border-radius: 8px; text-align: center;'>
                                <h3 style='margin: 0; color: #667eea;'>{label}</h3>
                                <p style='margin: 0.3rem 0 0 0; color: #636e72; font-size: 0.85em;'>{max_prob:.1f}% Confidence</p>
                            </div>
                            """, unsafe_allow_html=True)
                with col2:
                    if probs:
                        df = pd.DataFrame({"Category": ["World","Sports","Business","Sci/Tech"], "Probability": probs})
                        st.bar_chart(df.set_index("Category"), color="#667eea", height=150)

                st.markdown("### 📋 Summary")
                st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                        {result.get("summary", "")}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("### 🏷️ Entities")
                ents = result.get("entities", [])
                if ents:
                    entity_html = "<div style='background: white; padding: 1rem; border-radius: 8px;'>"
                    for e in ents:
                        eg = e.get('entity_group', 'MISC')
                        badge_class = "entity-badge"
                        if eg == "PER":
                            badge_class += " per-badge"
                        elif eg == "ORG":
                            badge_class += " org-badge"
                        elif eg == "LOC":
                            badge_class += " loc-badge"
                        entity_html += f"<span class='{badge_class}'>{eg}: {e.get('word')}</span> "
                    entity_html += "</div>"
                    st.markdown(entity_html, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ No entities detected.")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")