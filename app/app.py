import os
import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_openai import OpenAI
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
import yaml
from uuid import uuid4
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Configuration
USER_DB = 'users.yaml'
RESUME_DIR = 'resumes/'
os.makedirs(RESUME_DIR, exist_ok=True)

# Initialize Langchain OpenAI
llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")
llm_msg = ChatGroq(temperature=0.5, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="deepseek-r1-distill-llama-70b", reasoning_format="hidden")

# User Authentication Functions
def load_users():
    try:
        with open(USER_DB, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

def save_user(username, password):
    users = load_users()
    users[username] = {'password': password, 'resume': None}
    with open(USER_DB, 'w') as f:
        yaml.dump(users, f)

# Resume Processing with Langchain
def parse_resume(file_path):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    pages = loader.load()
    full_text = "\n".join([p.page_content for p in pages])
    
    # Structure resume text using LLM
    prompt_extract = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT FROM RESUME:
        {resume_data}
        ### INSTRUCTION:
        The scraped text is from a resume.
        Your job is to structure the data in JSON format containing the 
        following keys: `skills`, `experience`, `projects`, and `achievements`.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE):    
        """
    )

    chain_extract = prompt_extract | llm 
    res = chain_extract.invoke(input={'resume_data': full_text})
    json_parser = JsonOutputParser()
    return json_parser.parse(res.content)

# Job Description Scraper
def get_job_description(input_text):
    if input_text.startswith('http'):
        try:
            response = requests.get(input_text)
            soup = BeautifulSoup(response.text, 'html.parser')
            return ' '.join(soup.get_text().split()[:1000])
        except:
            return "Could not scrape URL, please paste description directly"
    return input_text

# Message Generation Templates
founder_template = """
Given the resume contents of the user, create a personalized message to the startup founder (within 100 words) that:
1. Come up with story on how resonate with problem that the company is trying to solve (Optional-mention only when applicable)
2. Connects my experience in experience/projects/achievements with the company's work
3. Highlights my relevant skills aligning with company's needs mnd job description
4. Ends with a call to schedule a chat

Experience, Projects, achievements, Job Description are mentioned below delimeted by triple backticks:
Experience: ```{experience}```
Projects: ```{projects}```
Achievements: ```{achievements}```
Job Description: ```{job_desc}```

Keep the message as human-like as you can showcasing genuine enthusiasm to contribute to the company.
You can answer in the following style:
<Job Description>
Terra is an API that makes it easy for apps to connect to wearables. Currently, apps and developers in the fitness, wellness, sleep, and other health spaces are using us. Terra was launched in early 2021, and since then we’ve been growing like crazy. But this is just the beginning.

The goal and vision

Think if Spotify and Netflix create music and movies based on your heart rate, and stress levels, in real time. We want to enable apps to achieve that reality, through our super easy to use API.
</Job Description>
<Sample Answer>
I came across Terra and was immediately drawn to the vision of personalizing experiences—like listening to the right songs based on heart rate. I can’t tell you how many times I’ve been at the gym, ready to push my limits, only for a slow, offbeat song to kill the momentum. It’s frustrating, and I completely resonate with the need for smarter, real-time personalization.

As an ML/DL enthusiast, I love building AI-driven products that enhance user experiences. My experience in machine learning, deep learning, and API-driven AI solutions makes me a great fit for an AI Engineer role at Terra. I’d love to contribute to making seamless, intelligent integrations a reality.

Looking forward to exploring this further!
</Sample Answer>
"""

hr_template = """Given the resume contents of the user, write a professional cover letter (keep under 150 words) that:
1. Expresses interest in job
2. Connects my experience in experience/projects/achievements with company's job requirements through job description
3. Highlights my relevant skills
4. Requests next steps

Experience, Projects, achievements, Job Description are mentioned below delimeted by triple backticks:
Experience: ```{experience}```
Projects: ```{projects}```
Achievements: ```{achievements}```
Job Description: ```{job_desc}```

Keep the message human-like tone(Should not sound machine written) showcasing genuine enthusiasm to contribute to the company
"""

# Streamlit App
def main_app():
    st.title("AI Job Application Assistant")
    
    # User Resume Management
    if not st.session_state.user['resume']:
        resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=['pdf','docx'])
        if resume_file:
            filename = f"{st.session_state.user['username']}_{uuid4()}{os.path.splitext(resume_file.name)[1]}"
            file_path = os.path.join(RESUME_DIR, filename)
            
            with open(file_path, 'wb') as f:
                f.write(resume_file.getbuffer())
            
            # Update user DB
            users = load_users()
            users[st.session_state.user['username']]['resume'] = file_path
            with open(USER_DB, 'w') as f:
                yaml.dump(users, f)
            
            st.session_state.user['resume'] = file_path
            st.rerun()
    else:
        st.success("✅ Resume on file")
        if st.button("Upload New Resume"):
            st.session_state.user['resume'] = None
            st.rerun()

    # Job Input
    job_input = st.text_area("Paste Job URL or Description", height=150)
    job_desc = get_job_description(job_input) if job_input else ""
    
    if st.session_state.user['resume'] and job_desc:
        # Parse resume
        resume_data = parse_resume(st.session_state.user['resume'])
        
        # Generate Content
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Founder Message"):
                message = LLMChain(llm=llm_msg, prompt=PromptTemplate.from_template(founder_template)).run({
                    'skills': resume_data['skills'],
                    'experience': resume_data['experience'],
                    'job_desc': job_desc,
                    'projects': resume_data['projects'],
                    'achievements': resume_data['achievements']
                })
                st.write(message)
                st.download_button("Download Message", message, file_name="founder_message.txt")
        
        with col2:
            if st.button("Generate HR Cover Letter"):
                letter = LLMChain(llm=llm_msg, prompt=PromptTemplate.from_template(hr_template)).run({
                    'skills': resume_data['skills'],
                    'experience': resume_data['experience'],
                    'projects': resume_data['projects'],
                    'achievements': resume_data['achievements'],
                    'job_desc': job_desc
                })
                st.write(letter)
                st.download_button("Download Letter", letter, file_name="cover_letter.txt")

# Login/Register
def auth_page():
    st.title("🔒 Login/Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            users = load_users()
            if users.get(username) and users[username]['password'] == password:
                st.session_state.user = {'username': username, 'resume': users[username]['resume']}
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type='password')
        if st.button("Create Account"):
            if new_user in load_users():
                st.error("Username exists")
            else:
                save_user(new_user, new_pass)
                st.success("Account created! Please login")

# Main Flow
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    main_app()
else:
    auth_page()