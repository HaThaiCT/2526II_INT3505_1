# Week 12 - API Product Demo (Developer Portal)

This folder contains a small Flask demo that illustrates API-as-a-product concepts: developer portal, docs, sandbox, API key issuance, usage tracking and a simple monetization model.

Quick start:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r "Week 12\requirements.txt"
python "Week 12\app.py"
```

Then open http://localhost:5002 in your browser.

Files:
- `app.py`: Flask app (portal, API, KPIs)
- `business_model_canvas.md`: suggested business model canvas
- `templates/`: HTML templates for portal, docs, sandbox

Next steps you can ask me to do:
- Add persistent analytics dashboard (Grafana/Prometheus)
- Add subscription billing flow sample
- Add unit tests and CI
