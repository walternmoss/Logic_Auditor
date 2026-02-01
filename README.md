# Logic_Auditor
The Logic Auditor is a Python-based digital humanities tool designed to deconstruct written arguments and identify structural logical fallacies. By leveraging the high-level reasoning capabilities of Gemini 3.0 Pro, it provides a rigorous, pair-wise analysis of claims and their underlying logical errors.

1. Installation

Before running the tool, you must install the required Python libraries:

Bash
pip3 install google-genai newspaper3k lxml_html_clean python-dotenv
2. Setting Up Your API Key

To use this tool, you need a Gemini API key from Google AI Studio.

In your project folder, create a new file named .env (ensure it starts with a dot).

Open the file in a text editor and add your key like this: GEMINI_API_KEY=your_actual_key_here

Security Note: If you are using GitHub, ensure you also create a file named .gitignore and add the line .env inside it. This prevents your private key from being uploaded to the public web.

3. How to Use

Launch: Open your terminal in the project folder and run: python3 logic_auditor.py

Choose Input:

URL: Paste a link to a web article (e.g., Substack, news, or blogs).

Local File: Provide the path to a .txt file.

View Report:

The script automatically repairs common web encoding errors (funny characters like â€™) before processing.

An HTML "Audit Ledger" will open in your browser, showing each fallacy, the literal quote from the text, and a detailed audit note.

4. Disclaimer

This tool is for research and educational purposes. The AI analysis should be used to supplement, not replace, human critical evaluation.
