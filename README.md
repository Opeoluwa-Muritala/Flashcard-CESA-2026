# Flashcard Generator (Flask + Free Hosted API)

A small Flask app that turns a topic or your notes into five study flashcards. Flip each card to reveal the answer, then mark whether you got it right or wrong to track your score.

**Time:** about 20 minutes. **Cost:** internet only, using a free-tier API key.

## Project layout

```
flashcard-playbook/
├── app.py
├── README.md
├── PLAYBOOK.md
└── templates/
    └── index.html
```

## Step 1: Install Python and the tools

Install Python 3 from python.org, then run this in a terminal:

```bash
pip install flask requests
```

## Step 2: Get a free API key

Sign up at a free-tier provider (for example, Groq at console.groq.com), create an API key, and save it in your terminal:

```bash
export API_KEY="paste-your-key-here"
```

On Windows PowerShell, use:

```powershell
$env:API_KEY="paste-your-key-here"
```

Use the same terminal for Step 5.

## Step 3: Create the project

Unzip the project, or create the files exactly as shown in this playbook:

- `app.py` is the Flask server and calls the model.
- `templates/index.html` is the page with the flip card, the score buttons and the Next button.

## Step 4: Check the model settings

Open `app.py` and look at the two lines near the top:

```python
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"
```

If your provider changes its endpoint or model names, update these two lines from its docs.

## Step 5: Run it

From the project folder, run:

```bash
python app.py
```

Open the address shown in the terminal (usually http://127.0.0.1:5000). Then:

1. Type a topic or paste notes into the box.
2. Click **Generate Cards**.
3. Click the card to flip it and see the answer.
4. Click **I got it right** or **I got it wrong**. The score updates.
5. Click **Next** to move on. After the last card, you see your final score.

## Troubleshooting

- **"API_KEY is not set"**: the key is not set in this terminal. Repeat Step 2 in the same window, then run `python app.py` again.
- **"The model request failed"**: check the key, and check the model name in `app.py`.
- **"Could not read the cards"**: click Generate Cards again. The model sometimes returns text outside the JSON.
- **Card does not flip**: make sure you are on the page served by Flask (http://127.0.0.1:5000), not an opened HTML file.

## How the code works (for the talk)

- The browser sends the topic to `/generate`. The Flask server adds instructions and sends them to the model. This is the system design idea: the server controls the prompt and checks the output before showing it.
- The model replies with JSON. The server extracts and validates it, so a bad reply does not break the page.
- The card flips with a CSS 3D rotation. The score is tracked in the browser.
