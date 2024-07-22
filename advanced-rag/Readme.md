# Advanced Retrieval with LangChain

## Overview

This project demonstrates advanced retrieval techniques using LangChain. It integrates various retrieval methods such as multi-query, contextual compression, parent document retrieval, ensemble retrieval, and self-querying with a user-friendly interface using Streamlit.

## Directory Structure

- `data/TCA/` - Contains the data files (PDFs) for retrieval.
- `app/` - Contains application logic and interface.
- `.env` - Environment variables file.
- `requirements.txt` - Python dependencies.

## Setup

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Set up environment variables:
    ```bash
    cp .env.example .env
    # Edit .env with your OpenAI API key
    ```

3. Run the Streamlit app:
    ```bash
    streamlit run app/chat_interface.py
    ```

## Usage

Use the Streamlit interface to interact with the search engine, ask questions, and get responses.
