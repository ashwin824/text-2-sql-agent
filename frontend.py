import streamlit as st
#from streamlit_extras.stylable_container import stylable_container
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
    <p>Ask question in plain English, get answers from your MySQL database.</p>
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

    st.markdown("### 💡 Sample Questions")   
    samples=[
            "Employees whose name starts with 'A'.",
            "Employees with a Gmail address.",
            "Employees with no manager assigned.",
            "Total number of employees in the company.",
            "Find the average salary of employees."]
    
    with st.container(key="sample-buttons"):
        for q in samples:
            if st.button(q,
                                key=f"sample_{q}", 
                                use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages=[]
        st.rerun()       

    #----------- Helper: parse raw result into DataFrame -------
    def try_parse_to_df(raw_result:str):
        """Attempt to parse the SQLDatabase.run() string output into a DataFrame."""
        try:
            # Sql Database.run() often returns a string like "[{'column1': 'value1', 'column2': 'value2'}, ...]"
            data = eval(raw_result)  
            if (
                isinstance(data, list) 
                and len(data) > 0 
                and isinstance(data[0], tuple)
                ):
                return pd.DataFrame(data)
        except Exception as e:
            st.warning(f"Could not parse result into DataFrame: {e}")
            return None
    # ------- Display Chat History -------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                st.markdown(msg["content"]["answer"])

                with st.expander("🔍 View SQL Query"):
                    st.code(msg["content"]["sql_query"], language="sql")

                    df = try_parse_to_df(msg["content"]["query_result"])    
                    if (df is not None
                        and not df.empty):
                        with st.expander("📊 View Result Data"):
                            st.dataframe(df, use_container_width=True)
                    else:
                        with st.expander("📄 Raw Result"):
                            st.text(msg["content"]["query_result"])

    # ------- Handle Innput -------
    question = None

    # from sample button click
    if "pending_question" in st.session_state:
        question = st.session_state.pending_question
        del st.session_state.pending_question

    # from chat input
    user_input = st.chat_input("Ask a question about your database...")
    if user_input:
        question = user_input

     # ------- Process Question -------
    if question:
        # add user message
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking... generating SQL and querying database.."):
                try:
                    result = agent.query(question)

                    st.markdown(result["answer"])

                    with st.expander("🔍 View SQL Query"):
                        st.code(result["sql_query"], language="sql")

                        df = try_parse_to_df(result["raw_result"])    
                        if (df is not None
                            and not df.empty):
                            with st.expander("📊 View Result Data"):
                                st.dataframe(df, use_container_width=True)
                        else:
                            with st.expander("📄 Raw Result"):
                                st.text(result["raw_result"])

                        st.session_state.messages.append({"role": "assistant", "content": result})        
                except Exception as e:
                   error_msg = f"❌ Error: {str(e)}"
             
    #----------- footer -----
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888;'>"
        "Built with LangGraph + Streamlit + MySQL"
        "</p>",
        unsafe_allow_html=True)            

    