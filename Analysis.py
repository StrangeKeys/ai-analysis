from openai import OpenAI
import openai
import PyPDF2
import streamlit as st
import pandas as pd
from docx import Document

openai.api_key = 

# Function to read and process the uploaded DOCX file
def process_docx(uploaded_file):
    if uploaded_file is not None:
        # Load the DOCX file
        docx = Document(uploaded_file)
        
        # Extract text from each paragraph in the document
        text = []
        for para in docx.paragraphs:
            text.append(para.text)
        
        # Join the extracted text into a single string
        docx_text = '\n'.join(text)
        
        return docx_text
# Function to read and process Excel (XLSX) file
def process_excel(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        return df

# Function to read and process plain text (TXT) file
def process_txt(uploaded_file):
    if uploaded_file is not None:
        txt_content = uploaded_file.read().decode("utf-8")
        return txt_content

# Function to read and process PDF file
def process_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()
        return pdf_text

with st.sidebar:
    choice = st.radio("Pick the output you would like.",["Questions", "Data Analysis", "Summarization Tool"])
    uploaded_file = st.file_uploader("Upload/Read files", None, accept_multiple_files=False)

st.title("💬 Data Analysis and Content Summary Tool")
st.caption("🚀 A chatbot to answer questions, analyze data and summarize text powered by OpenAI LLM")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    if uploaded_file:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            docx_text = process_docx(uploaded_file)
            if docx_text:
                prompt += "\n" + docx_text
        elif uploaded_file.type == "text/plain":
            txt_content = process_txt(uploaded_file)
            if txt_content:
                prompt += "\n" + txt_content
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            excel_df = process_excel(uploaded_file)
            if excel_df is not None:
                excel_text = excel_df.to_string(index=False)
                if excel_text:
                    prompt += "\n" + excel_text
        elif uploaded_file.type == "application/pdf":
            pdf_text = process_pdf(uploaded_file)
            if pdf_text:
                prompt += "\n" + pdf_text

    client = OpenAI(api_key=openai.api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    if (choice == "Summarization Tool"):
        response = openai.chat.completions.create(
        model="gpt-3.5-turbo", # GPT model
        messages=[
            # System role with description of being a "AI Data Analyzer Assistant" to interpret user's input data
            {"role": "system", "content": "You are an AI Content Summarizer Assistant. Your task is to provide a concise summary of the input text while capturing all key information and important context. Include who, what, where, and why as needed"},
            # Role of user, takes user input as the prompt
            {"role": "user", "content": prompt}
            ]
    )
    if (choice == "Questions"):
        response = openai.chat.completions.create(
        model="gpt-3.5-turbo", # GPT model
        messages=[
            # System role with description of being a "AI Data Analyzer Assistant" to interpret user's input data
            {"role": "system", "content": "You are an AI Question Answering Assistant. Your task is to answer questions based on the input text, providing accurate and relevant information."},
            # Role of user, takes user input as the prompt
            {"role": "user", "content": prompt}
            ]
    )
    if (choice == "Data Analysis"):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # GPT model
            messages=[
                # System role with description of being a "AI Data Analyzer Assistant" to interpret user's input data
                {"role": "system", "content": "As an AI Data Analyzer Assistant, your task is to provide a comprehensive analysis of the input text, capturing all key information and important context. Your analysis should include both statistical and distribution analyses to offer a holistic understanding of the data. For statistical analysis, provide metrics such as Mean, Median, Mode, Range, Variance, Standard Deviation, Quartiles, Percentiles, and Skewness."},
                # Role of user, takes user input as the prompt
                {"role": "user", "content": prompt}
                ])
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
