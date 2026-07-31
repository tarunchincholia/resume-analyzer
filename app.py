import streamlit as st
import pdfplumber
import io
import json
import requests

API_KEY = ""

st.title("Resume Analyzer")
st.write("This app analyzes your resume against a job description using AI")

# function to read pdf
def read_pdf(file):
    text = ""
    with pdfplumber.open(io.BytesIO(file.read())) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# function to call groq api
def get_ai_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"]

st.divider()

# upload resume
st.subheader("Upload Resume")
pdf_file = st.file_uploader("Choose your resume PDF", type="pdf")

resume_text = ""
if pdf_file is not None:
    resume_text = read_pdf(pdf_file)
    st.success("Resume uploaded successfully!")
    st.write("Characters extracted:", len(resume_text))

st.divider()

# job description input
st.subheader("Job Description")
job_desc = st.text_area("Paste the job description here", height=150)

st.divider()

# choose feature
st.subheader("What do you want to do?")
option = st.selectbox("Select an option", ["Match Analysis", "Resume Tips"])

# main button
if st.button("Analyze"):
    
    if resume_text == "":
        st.error("Please upload your resume")
    elif option == "Match Analysis" and job_desc == "":
        st.error("Please enter job description for match analysis")
    else:
        
        if option == "Match Analysis":
            st.info("Analyzing your resume...")
            
            prompt = """Look at this resume and job description. 
Give me a match score out of 100 and list the matching skills and missing skills.
Reply in JSON only like this:
{
  "score": 75,
  "matched_skills": ["python", "sql"],
  "missing_skills": ["docker", "aws"],
  "feedback": "write 2-3 lines about the candidate here"
}

Resume:
""" + resume_text + """

Job Description:
""" + job_desc
            
            response = get_ai_response(prompt)
            
            clean = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
            
            score = data["score"]
            st.subheader("Match Score: " + str(score) + "/100")
            
            if score >= 70:
                st.success("Good match!")
            elif score >= 40:
                st.warning("Average match, improve some skills")
            else:
                st.error("Low match, you need to learn more skills")
            
            st.write(data["feedback"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Skills you have:**")
                for skill in data["matched_skills"]:
                    st.write("✅ " + skill)
            
            with col2:
                st.write("**Skills you are missing:**")
                for skill in data["missing_skills"]:
                    st.write("❌ " + skill)
        
        elif option == "Resume Tips":
            st.info("Getting improvement tips...")
            
            prompt = """Read this resume and give 5 tips to improve it.
Write each tip clearly with what is wrong and how to fix it.
Keep it simple and easy to understand.

Resume:
""" + resume_text
            
            response = get_ai_response(prompt)
            
            st.subheader("Tips to Improve Your Resume")
            st.write(response)