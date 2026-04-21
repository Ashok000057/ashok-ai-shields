import streamlit as st
import nmap
import pandas as pd
import feedparser
import re
from fpdf import FPDF
from groq import Groq  # Ollama ki jagah Groq import kiya

# Dashboard Setup
st.set_page_config(page_title="AI-Shield Commander PRO", page_icon="🛡️", layout="wide")

# --- API KEY FROM SECRETS (Cloud Deployment ke liye) ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = None

# --- PDF GENERATION ---
def create_pdf(report_text, target):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI-Shield Commander: Security Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Architect & Developer: Ashok Bakoliya | Target: {target}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    # Cleaning text for PDF compatibility
    clean_text = report_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- IMAGE EXTRACTOR (Unique Images Logic) ---
def get_unique_image(entry, index):
    img_match = re.search(r'<img [^>]*src="([^"]+)"', entry.description)
    if img_match:
        return img_match.group(1)
    
    cyber_images = [
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400",
        "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=400",
        "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=400",
        "https://images.unsplash.com/photo-1510915228340-29c85a43dcfe?w=400",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400"
    ]
    return cyber_images[index % len(cyber_images)]

# --- STYLING ---
st.markdown("""
    <style>
    .stButton>button { background-color: #00FF00 !important; color: black !important; font-weight: bold; border-radius: 5px; width: 100%; }
    .branding { color: #00FF00; font-weight: bold; font-size: 1.3rem; }
    .news-box { padding: 8px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; background-color: #0a0a0a; }
    .news-title { color: #00FF00; font-weight: bold; text-decoration: none; font-size: 0.85rem; display: block; margin-top: 8px; }
    .guide-box { padding: 10px; background-color: #1e1e1e; border-radius: 5px; font-size: 0.8rem; color: #00FF00; border: 1px solid #333; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='branding'>🛡️ ASHOK'S LABS</div>", unsafe_allow_html=True)
    st.write("---")
    
    # Model selection for Groq
    ai_model = st.selectbox("Select AI Engine (Groq Cloud)", options=["llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"])
    
    st.divider()
    st.subheader("📖 How it works?")
    st.info("Nmap captures network data, then Ashok's Cloud AI analyzes it for CVE exploits.")

    st.subheader("🔢 Port Numbers Guide")
    st.markdown("""<div class='guide-box'>80: Web | 443: Web-Sec | 22: SSH | 3389: RDP</div>""", unsafe_allow_html=True)
    
    st.divider()
    st.header("🗞️ Cyber Intelligence")
    
    try:
        feed = feedparser.parse("https://hnrss.org/newest?q=cybersecurity")
        for i, entry in enumerate(feed.entries[:5]):
            img_url = get_unique_image(entry, i)
            st.markdown(f"<div class='news-box'>", unsafe_allow_html=True)
            st.image(img_url, use_container_width=True)
            st.markdown(f"<a class='news-title' href='{entry.link}' target='_blank'>{entry.title}</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    except:
        st.write("News Feed Error.")

# --- MAIN UI ---
st.title("🛡️ AI-Shield Commander PRO")
st.markdown(f"<h4 style='color: #888;'>Architect & Developer: <span style='color: #00FF00;'>Ashok Bakoliya</span></h4>", unsafe_allow_html=True)
st.write("---")

target = st.text_input("Target IP / Domain", placeholder="e.g. 8.8.8.8")

if st.button("🚀 INITIATE SYSTEM AUDIT"):
    if not GROQ_API_KEY:
        st.error("⚠️ Error: Groq API Key missing! Please add it to Streamlit Secrets.")
    elif target:
        with st.spinner("🔍 Deep Scanning & Cloud AI Analysis..."):
            try:
                # Nmap Scan
                nm = nmap.PortScanner()
                nm.scan(target, arguments='-sV --version-intensity 5 -Pn')
                
                results = []
                for host in nm.all_hosts():
                    for proto in nm[host].all_protocols():
                        for port in nm[host][proto].keys():
                            results.append({
                                "Port": port, "Service": nm[host][proto][port]['name'],
                                "Version": nm[host][proto][port]['version'], "State": nm[host][proto][port]['state']
                            })
                
                if results:
                    st.subheader("🔍 Scan Findings")
                    st.dataframe(pd.DataFrame(results), use_container_width=True)

                    # Scorecard Logic
                    st.divider()
                    num_ports = len(results)
                    score = max(0, 100 - (num_ports * 15))
                    c1, c2 = st.columns(2)
                    c1.metric("Security Score", f"{score}/100")
                    if score > 80: c2.success("Status: Safe")
                    elif score > 50: c2.warning("Status: At Risk")
                    else: c2.error("Status: Critical!")

                    # --- GROQ AI REPORT ENGINE ---
                    st.subheader(f"🤖 AI Expert Report ({ai_model})")
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        prompt = f"As a cybersecurity expert, analyze these nmap results: {str(results)}. Identify CVE risks and give 3 clear actionable fixes. Keep it professional."
                        
                        completion = client.chat.completions.create(
                            model=ai_model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.5,
                        )
                        report = completion.choices[0].message.content
                        st.markdown(report)
                        
                        # Exports
                        st.divider()
                        col1, col2 = st.columns(2)
                        col1.download_button("📥 Download Text Report", report, file_name=f"Audit_{target}.txt")
                        
                        pdf_data = create_pdf(report, target)
                        col2.download_button("📄 Download PDF Report", pdf_data, file_name=f"Audit_Ashok.pdf")
                    
                    except Exception as ai_err:
                        st.error(f"AI Generation Error: {ai_err}")

                else:
                    st.warning("No open ports detected. Target might be blocking scans or is secure.")
            except Exception as e:
                st.error(f"System Error: {e}")
    else:
        st.warning("Please provide a target IP or Domain.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>AI-Shield Commander PRO | <b>Designed by Ashok Bakoliya</b> | © 2026</div>", unsafe_allow_html=True)
