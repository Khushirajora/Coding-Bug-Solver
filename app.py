import streamlit as st
import os
from google import genai

st.set_page_config(page_title="CodePatrol AI Code Reviewer", page_icon="🛡️", layout="wide")

st.title("🛡️ CodePatrol: AI Code Review & Triage Assistant (Gemini Powered)")
st.write("Paste your code snippet or bug report below to get instant AI analysis, severity ranking, and fix recommendations.")

# Sidebar for API Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input("Enter Gemini API Key", type="password", value="")
    
    # Locked to the current stable production model ID
    model_choice = st.selectbox(
        "Select Gemini Model", 
        ["gemini-3.7-flash", "gemini-3.5-flash"]
    )
    
    st.markdown("---")
    st.write("💡 Get your free key at [Google AI Studio](https://aistudio.google.com)")

# Layout columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Input Code / Bug Report")
    code_input = st.text_area(
        "Paste code or error logs here...", 
        height=300, 
        placeholder="def unsafe_query(user_id):\n    cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"
    )
    analyze_btn = st.button("Analyze Code", type="primary")

with col2:
    st.subheader("🔍 AI Analysis & Recommendations")
    if analyze_btn:
        if not api_key_input:
            st.error("Please provide your Gemini API key in the sidebar to run the analysis.")
        elif not code_input.strip():
            st.warning("Please enter some code to analyze.")
        else:
            with st.spinner("Gemini AI is analyzing your code..."):
                try:
                    # Initialize the official Google GenAI client
                    client = genai.Client(api_key=api_key_input)
                    
                    prompt = f"""
                    You are an expert code reviewer and security auditor. Analyze the following code or bug report. 
                    Provide your response in a clear format containing:
                    1. Severity (Critical, High, Medium, or Low)
                    2. Target Department (Security, Backend, Frontend, or Infra)
                    3. List of specific issues found
                    4. Suggested corrected code snippet

                    Code/Report:
                    {code_input}
                    """

                    response = client.models.generate_content(
                        model=model_choice,
                        contents=prompt,
                    )
                    
                    analysis_result = response.text
                    
                    st.success("Analysis Complete!")
                    st.markdown("### 📊 Report Summary")
                    st.markdown(analysis_result)

                except Exception as e:
                    st.error(f"An error occurred during AI analysis: {e}")