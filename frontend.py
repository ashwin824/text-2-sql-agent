import streamlit as st
from backend import TextToSQLAgent
import pandas as pd

# --------- page config --------
st.set_page_config(
    page_title= "Text-to-SQL-Agent",
    page_icon="🗄️",
    layout="wide"
)

# -------- custom styling -------
st.markdown("""
<style>
    .stApp {background-color: #fafafa;}
    .main-header{
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        paddind: 1.5rem;
        boarder-radius: 10px;
        color: white;
        margin-bottom:2rem;
    }
    .sql-box{
        background-color: #1e1e1e;
        color: #d4d4d4,
        padding: 1rem,
        boarder-radius : 6px,
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)
#---------- Header -------------
st.markdown("""
<div class="main-header">
    <h1>🗄️Text-to-SQL Agent</h1>
    <p>Ask question in plain English, get answers from you MySQL database.</p>
</div>
""",unsafe_allow_html=True)
#--------- Initialize Agent ------
@st.cache_resource
def load_agent():
    return TextToSQLAgent()

try:
    agent = load_agent()
    connected = True
except Exception as e:
    st.error(f"❌ Database connection failed: {e}")
    connected = False
    st.stop()    

#--------- Initialize Chat History ------    
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.write(f"messages: {st.session_state.messages}")

#--------- Sidebar ---------
with st.sidebar:
    st.markdown("### 🔌 Connection Status")
    st.success("✅ Connected to MySQL")    
    
    with st.expander("Table List"):
            for table in agent.get_table_names():
                st.markdown(f"-`{table}`")

    with st.expander("📐 View Schema"):
        st.code(agent.get_schema_info(), language="sql")    