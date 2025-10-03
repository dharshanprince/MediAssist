MediAssist — Combined Single-file Demo

What I did:

- Created combined.html which inlines style.css and script.js and contains client-side-only versions of your pages (home, login/signup, patient dashboard, doctor dashboard, and patient profile). It uses localStorage to simulate users, patient data, and report uploads for local demos.
- Added serve.ps1 which opens combined.html in the default browser on Windows.

How to run (recommended for quick local demo on Windows):

1. Open PowerShell and cd into the project folder (where this README is located).
2. Run:

.\serve.ps1

This will open combined.html in your default browser. The page is a self-contained demo and does not require a server.

Optional: Run a static server (if you have Python installed):

From the project folder run:

python -m http.server 8000

Then open http://localhost:8000/combined.html in your browser.

Notes and limitations:

- combined.html is a client-side mock for demo and testing. It does not integrate with app.py or the Flask backend.
- If you want the Flask app (app.py) to serve the combined file and use server-side functionality (uploads, sessions), I can update app.py to serve combined.html and run Flask — tell me if you'd like that.
