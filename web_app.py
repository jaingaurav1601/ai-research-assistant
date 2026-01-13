import streamlit as st
from groq import Groq
import requests
from datetime import datetime
import sys
import os

# Add the current directory to path to import research_assistant
sys.path.insert(0, os.path.dirname(__file__))
from research_assistant import search_topic, save_report, research_agent_core

# Initialize Groq client
client = Groq(api_key="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")

def frame_user_query(user_query):
    """Use LLM to frame user query into optimized search queries"""
    
    prompt = f"""Given this user query: "{user_query}"

Generate:
1. A main search query (most specific and relevant)
2. 2-3 additional search queries to get comprehensive information

Format your response as:
MAIN_QUERY: [main search query]
ADDITIONAL_QUERIES: [query1], [query2], [query3]

Focus on keywords that will yield maximum relevant results. Make queries specific and focused."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    
    response_text = response.choices[0].message.content
    
    # Parse the response
    queries = {"main": "", "additional": []}
    
    try:
        for line in response_text.split('\n'):
            if line.startswith('MAIN_QUERY:'):
                queries['main'] = line.replace('MAIN_QUERY:', '').strip()
            elif line.startswith('ADDITIONAL_QUERIES:'):
                additional = line.replace('ADDITIONAL_QUERIES:', '').strip()
                queries['additional'] = [q.strip() for q in additional.split(',')]
    except:
        # Fallback to original query if parsing fails
        queries['main'] = user_query
    
    return queries

# Streamlit UI
st.set_page_config(page_title="AI Research Assistant", page_icon="🔍", layout="wide")

st.title("🔍 AI Research Assistant")
st.markdown("Enter any topic and I'll research it for you with optimized search queries")

# Initialize session state
if 'research_count' not in st.session_state:
    st.session_state.research_count = 0

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    report_length = st.selectbox(
        "Report Length",
        ["short", "medium", "long"],
        index=1
    )
    
    show_search_queries = st.checkbox("Show optimized search queries", value=True)
    show_citations = st.checkbox("Show citations", value=True)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This agent uses an LLM layer to optimize your query and perform comprehensive research with citations.")
    
    st.markdown("---")
    st.metric("📊 Reports Generated", st.session_state.research_count)

# Main interface
col1, col2 = st.columns([4, 1])

with col1:
    topic = st.text_input(
        "Research Topic", 
        placeholder="e.g., impact of AI on healthcare, quantum computing applications",
        label_visibility="collapsed"
    )

with col2:
    research_button = st.button("🔍 Research", type="primary", use_container_width=True)

if research_button:
    if not topic:
        st.warning("Please enter a topic")
    else:
        # Step 1: Frame the user query
        with st.spinner("📝 Optimizing your query..."):
            try:
                framed_queries = frame_user_query(topic)
            except Exception as e:
                st.error(f"Error framing query: {str(e)}")
                framed_queries = {"main": topic, "additional": []}
        
        # Display framed queries if enabled
        if show_search_queries:
            with st.expander("📌 Optimized Search Queries", expanded=True):
                st.write(f"**Main Query:** `{framed_queries['main']}`")
                if framed_queries['additional']:
                    st.write(f"**Additional Queries:**")
                    for q in framed_queries['additional']:
                        st.write(f"  • `{q}`")
        
        # Step 2: Perform research using research_agent_core
        with st.spinner(f"🔍 Researching {topic}..."):
            try:
                result = research_agent_core(
                    framed_queries['main'],
                    framed_queries['additional'] if framed_queries['additional'] else None,
                    report_length
                )
            except Exception as e:
                st.error(f"Error during research: {str(e)}")
                result = {"report": None, "filename": None, "citations": []}
        
        if result.get("filename"):
            st.success("✅ Research complete!")
            
            # Display report
            st.markdown("### 📄 Report")
            st.markdown(result["report"])
            
            # Display citations if available and enabled
            if show_citations and result.get("citations"):
                with st.expander("📚 Citations"):
                    for citation in result["citations"]:
                        st.write(f"• {citation}")
            
            # Download button with citations
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{topic.replace(' ', '_')}_{timestamp}.txt"
            
            report_content = f"""Research Report: {topic}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Length: {report_length}
{'=' * 60}

{result['report']}"""
            
            if result.get("citations"):
                report_content += f"""

{'=' * 60}
CITATIONS
{'=' * 60}
"""
                for citation in result["citations"]:
                    report_content += f"{citation}\n"
            
            st.download_button(
                label="📥 Download Report",
                data=report_content,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
            
            # Update stats
            st.session_state.research_count += 1
        else:
            st.error("❌ Could not find enough information. Try a different topic or be more specific.")