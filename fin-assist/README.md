
# FinAssist

FinAssist is a chatbot application designed to help users with queries related to financial regulation documents, specifically concerning the Tax Consolidation Act (TCA).

## Prerequisites

- Python 3.8+
- Pip (Python package installer)

## Installation

### Backend Setup

1. **Clone the Repository**

If you have the zip file, skip the git clone step and simply extract the file
else, create a folder "genai-search" on your machine and clone the repository
   ```bash
   git clone https://github.com/thatAishwarya/genai-search
   ```
2. **Navigate to the project folder**
 ```bash
   cd genai-search/fin-assist
   ```
3. **Create and Activate a Virtual Environment (Can be skipped)** 

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. **Install Python Dependencies**

   Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**
   
   Navigate to your web browser and open url : http://localhost:8000/

## Usage

### Query the Chatbot

- Enter your query in the input field at the bottom of the chat interface and click "Submit" to receive a response from the chatbot. Additionally, select a model and compare responses from different models.