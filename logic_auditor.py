import os
import json
import re
import unicodedata
from google import genai
from google.genai import types
from newspaper import Article
from dotenv import load_dotenv
import difflib

# Load variables from .env
load_dotenv()

def manual_encoding_repair(text):
    """Targets specific character artifacts like â€™ and â€œ."""
    if not text: return ""
    replacements = {
        "â€œ": '"', "â€": '"', "â€™": "'", "â€˜": "'",
        "â€”": "—", "â€“": "–", "â€¦": "...", "Â": "",
        "â€\x9d": '"', "â€\x9c": '"', "â€\x99": "'"
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return unicodedata.normalize('NFKC', text).strip()

def find_exact_quote(paraphrased_quote, full_text):
    """Prevents AI paraphrasing by finding the original literal sentence."""
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    matches = difflib.get_close_matches(paraphrased_quote, sentences, n=1, cutoff=0.5)
    return matches[0] if matches else paraphrased_quote

def get_api_key():
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def audit_text(text, api_key):
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_level="high")
    )
    prompt = f"""
    Act as a formal Logic Auditor. Analyze for logical fallacies.
    Output ONLY JSON:
    {{ "findings": [ {{ "quote": "literal sentence", "fallacy": "Name", "explanation": "Note" }} ] }}
    Text: {text[:20000]}
    """
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        config=config,
        contents=prompt
    )
    try:
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(json_match.group()).get('findings', [])
    except: return []

def generate_report(title, original_text, findings):
    html_items = []
    for f in findings:
        literal_quote = find_exact_quote(f['quote'], original_text)
        clean_quote = manual_encoding_repair(literal_quote)
        clean_explanation = manual_encoding_repair(f['explanation'])
        
        html_items.append(f"""
        <div style="border-left: 5px solid #e74c3c; background: #fdf2f2; padding: 20px; margin-bottom: 20px;">
            <b style="color: #c0392b;">{f['fallacy']}</b><br>
            <i style="color: #34495e; display: block; margin: 10px 0;">"{clean_quote}"</i>
            <p><b>Audit Note:</b> {clean_explanation}</p>
        </div>
        """)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Audit: {title}</title>
        <style>body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}</style>
    </head>
    <body>
        <h1>Logic Audit Ledger: {title}</h1>
        <hr>{''.join(html_items)}
    </body>
    </html>
    """
    filename = f"logic_ledger_{re.sub(r'[^a-zA-Z0-9]', '_', title[:20])}.html"
    with open(filename, 'w', encoding='utf-8') as f: f.write(html_content)
    os.system(f'open "{filename}"') if os.name != 'nt' else os.startfile(filename)

if __name__ == "__main__":
    key = get_api_key()
    print("\n--- Logic Auditor v1.9 ---")
    choice = input("Audit (1) URL or (2) Local Text File? [1/2]: ").strip()
    
    if choice == "1":
        url = input("Enter URL: ")
        article = Article(url)
        article.download(); article.parse()
        title, raw_content = article.title, manual_encoding_repair(article.text)
    else:
        path = input("Enter file path (.txt): ")
        with open(path, 'r', encoding='utf-8') as f:
            title, raw_content = os.path.basename(path), manual_encoding_repair(f.read())
    
    print("Performing deep audit (Gemini 3.0 Pro)...")
    results = audit_text(raw_content, key)
    generate_report(title, raw_content, results)