import streamlit as st
import nmap
import pandas as pd
import feedparser
import re
from fpdf import FPDF
from groq import Groq

# Dashboard Setup
st.set_page_config(page_title="AI-Shield Commander PRO", page_icon="🛡️", layout="wide")

# --- API KEY FROM SECRETS ---
# Jab aap Streamlit Cloud par deploy karenge, wahan settings mein ye key daal dena
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = None

def get_ai_analysis(scan_data):
    if not GROQ_API_KEY:
        return "⚠️ AI Error: Groq API Key missing in Streamlit Secrets!"
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"Analyze these network scan results: {str(scan_data)}. Identify potential CVE risks and give 3 actionable fix steps. Be professional."
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Failed: {str(e)}"

# --- PDF GENERATOR ---
def create_pdf(report_text, target):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI-Shield Commander: Security Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Architect: Ashok | Target: {target}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    clean_text = report_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- NEWS IMAGE EXTRACTOR ---
def get_news_img(entry, i):
    img_match = re.search(r'<img [^>]*src="([^"]+)"', entry.description)
    if img_match: return img_match.group(1)
    # Default cool cyber images
    imgs = ["https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400", 
            "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=400",
            "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=400"]
    return imgs[i % len(imgs)]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #00FF00;'>🛡️ ASHOK'S LABS</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("🗞️ Live Cyber News")
    try:
        feed = feedparser.parse("https://hnrss.org/newest?q=cybersecurity")
        for i, entry in enumerate(feed.entries[:3]):
            st.image(get_news_img(entry, i), use_container_width=True)
            st.markdown(f"<a href='{entry.link}' target='_blank' style='color:#00FF00; text-decoration:none; font-size:0.8rem;'><b>{entry.title}</b></a>", unsafe_allow_html=True)
            st.write("---")
    except: st.write("Feed unavailable")

# --- MAIN PAGE ---
st.title("🛡️ AI-Shield Commander PRO")
st.markdown("<h4 style='color: #888;'>Developed by: <span style='color: #00FF00;'>Ashok</span></h4>", unsafe_allow_html=True)
st.write("---")

target = st.text_input("Enter Target IP or Domain (e.g., 8.8.8.8)")

if st.button("🚀 RUN SECURITY AUDIT"):
    if target:
        with st.spinner("🔍 Deep Scanning & AI Analysis..."):
            try:
                nm = nmap.PortScanner()
                nm.scan(target, arguments='-sV -Pn')
                
                results = []
                for host in nm.all_hosts():
                    for proto in nm[host].all_protocols():
                        for port in nm[host][proto].keys():
                            results.append({
                                "Port": port, 
                                "Service": nm[host][proto][port]['name'],
                                "Version": nm[host][proto][port]['version']
                            })
                
                if results:
                    st.subheader("📊 Scan Results")
                    st.dataframe(pd.DataFrame(results), use_container_width=True)
                    
                    # AI Analysis
                    st.subheader("🤖 AI Vulnerability Report")
                    report = get_ai_analysis(results)
                    st.markdown(report)
                    
                    # PDF Export
                    st.divider()
                    pdf_data = create_pdf(report, target)
                    st.download_button("📄 Download Professional PDF Report", pdf_data, file_name=f"Ashok_Audit_{target}.pdf")
                else:
                    st.warning("No open ports found on this target.")
            except Exception as e:
                st.error(f"System Error: {e}")
    else:
        st.warning("Please provide a target.")

st.markdown("---")
st.caption("© 2026 Ashok's Labs | Professional AI Auditor Edition")