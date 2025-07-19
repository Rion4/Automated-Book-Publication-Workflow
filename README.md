# Automated Book Publication Workflow

Welcome to the Automated Book Publication Workflow! This project is designed to streamline the process of creating and refining book content using the power of AI. It leverages advanced language models (like Gemini) and a robust database (ChromaDB) to automate various stages of content generation, from web scraping to AI-driven writing and reviewing, with a crucial human-in-the-loop stage for quality control.

## What it Does

This workflow automates several key steps in content creation:

1.  **Web Content Ingestion:** Scrapes content from specified URLs, evaluates its quality, and stores it for further processing.
2.  **AI Writer Agent:** Rewrites and "spins" the ingested text, generating new versions of the content.
3.  **AI Reviewer Agent:** Critiques the AI-generated content, providing detailed feedback and suggestions for improvement.
4.  **Human-in-the-Loop (HITL):** Allows a human to review the AI's output, provide feedback, and approve or request further revisions, ensuring the final content meets human standards.
5.  **Semantic Search (Optional):** Provides a way to search through the content archive based on semantic similarity.

## How to Use

To run this workflow, you'll need to set up your environment with the necessary dependencies and API keys.

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/rion4/Automated-Book-Publication-Workflow.git
    cd Automated-Book-Publication-Workflow
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file is assumed to exist or will need to be created with project dependencies.)*
3.  **Configure API Keys:**
    Create a `.env` file in the root directory and add your Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
4.  **Run the workflow:**
    ```bash
    python main_workflow.py
    ```
    Follow the prompts in the terminal to navigate through the workflow stages.

## Project Structure

-   `main_workflow.py`: The main entry point for the automated workflow.
-   `scraper_agent.py`: Handles web content ingestion.
-   `writer_agent.py`: Manages AI-driven text generation.
-   `reviewer_agent.py`: Provides AI-powered content review and feedback.
-   `ChromaDB.py`: Manages interactions with the ChromaDB database for content storage.
-   `config.py`: Contains configuration settings for the workflow.
-   `voice_interface.py`: (If applicable) Handles voice input/output for the HITL stage.
-   `db/`: Directory for ChromaDB data.

## Contributing

Feel free to explore, use, and contribute to this project! If you have suggestions or find issues, please open an issue or submit a pull request.

---

*This project was developed to automate and enhance the book publication process, making content creation more efficient and intelligent.*
