# Atticus

Atticus is a legal answering service that grounds its answers in legal statutes and case law using vector embeddings such that its responses are more reliable than a typical AI chatbot.

Atticus is a work in progress and likely has many bugs. Its answers are not to be trusted nor do they qualify as legal advice. Always consult a licensed attorney for professinoal legal advice.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them:

- Python 3.8 or newer (some issues with 3.11 on some machines)
- pip (Python package installer)
- Virtual environment (optional but recommended)

### Installation

1. **Clone the repository**

    ```sh
    git clone https://github.com/halfprice06/atticus
    ```

2. **Navigate to the project directory**

    ```sh
    cd atticus
    ```

3. **Set up a virtual environment** (optional but recommended)

    ```sh
    python -m venv venv  # create a virtual environment in the 'venv' directory
    source venv/bin/activate  # activate the virtual environment (Linux/Mac)
    venv\Scripts\activate  # activate the virtual environment (Windows)
    ```

4. **Install the dependencies**

    ```sh
    pip install -r requirements.txt
    ```

5. **Environment Variables and API Keys**

    - Make sure to set up necessary environment variables in the config.yaml.

### Running the Server

1. **Start the FastAPI server**

    ```sh
    uvicorn fastapi_server:app --reload
    ```

### Running the Webpage

1. **In a new terminal window, navigate to the webpage directory**

    ```sh
    cd legal_beagle/webpage
    ```

2. **Run a local HTTP server**

    - This is one way to avoid CORS and mixed content issues during development. You need to select a port other than 8000 to avoid conflicts with the FastAPI server.

    ```sh
    python -m http.server 8080
    ```
    if issues on macOS, try:

    ```sh
    /opt/homebrew/opt/python@3.11/bin/python3.11 -m http.server 8080
    ```

3. **Access the webpage**

    - Open your browser and navigate to `http://localhost:8080` or whichever port your HTTP server is using.

## Using the Chatbot

- You can interact with Atticus via the web interface to the api.