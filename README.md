# AI Job Application Assistant 🤖✉️

Application is deployed. Access it using the [link](https://predator4hack-cold-email-genai-appapp-jd2g7b.streamlit.app/)

An AI-powered web app that generates personalized job application messages using your resume and job descriptions. Built with Streamlit, LangChain, and OpenAI.

## Features ✨

-   🔐 User authentication with persistent resume storage
-   📄 Resume parsing (PDF/DOCX) using LangChain document loaders
-   🌐 Job description input via URL or direct text paste
-   ✍️ AI-generated messages:
    -   Personalized message to company founders
    -   Professional HR cover letter
-   💾 Persistent user data with YAML storage
-   🚀 Free deployment ready for Streamlit/Hugging Face

## Installation 🛠️

1. Clone the repository:

```bash
git clone https://github.com/yourusername/job-application-assistant.git
cd job-application-assistant
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Setup GroqCloud API Key:

```bash
export GROQ_API_KEY="your-api-key"
```

4. Usage

```bash
streamlit run app/app.py
```

## Configuration ⚙️

```
OPENAI_API_KEY: Required for AI generation (Get key)

USER_DB: User data storage (users.yaml)

RESUME_DIR: Resume storage directory (resumes/)
```

## Folder Structure 📁

```
.
├── app
|   ├── app.py                 # Main application code
|   ├── users.yaml             # User database
|   ├── resumes/               # Uploaded resumes storage
|   ├── requirements.txt       # Dependencies
|   └── README.md              # This file
├── Chromadb.ipynb
├── CV Parser.ipynp
├── emailGenerator.ipynb
├── LangChain.ipynb
```

## License 📄

Distributed under the MIT License. See LICENSE for more information.
