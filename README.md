# AI Research Agent

## Overview
The **AI Research Agent** is a lightweight system that combines an **LLM (OpenAI)** with two fixed tools:
1. **Web Search (Tavily API)** -> to discover relevant sources.
2. **Content Extractor (Trafilatura + PyPDF)** -> to fetch and clean text from web pages and PDFs.

It allows you to:
- Enter a query (e.g., *"Latest research on AI in education"* or *"Impact of Mediterranean diet on heart health"*).
- Search and extract 2-3 reliable sources.
- Summarize findings into a short, structured report using an LLM.
- Save reports in a database (SQLite).
- View past reports in a simple web interface.

Errors (timeouts, blocked sites, missing text) are handled gracefully with friendly labels like *Blocked by site* or *Source unavailable*.

---

## Architecture

```
[ User Query ]
      │
[ Tavily Search API ] -> Finds 2-3 URLs
      |
[ Trafilatura / PyPDF Extractor ] -> Cleans HTML/PDF text
      │
[ OpenAI LLM ] -> Summarizes findings into Markdown
      │
[ SQLite Database ] -> Saves query, summary, sources
      │
[ Flask Web UI ] -> History page + Report view
```

## How to Run

### 1. Clone repo & install dependencies
```bash
git clone https://github.com/Jayanth026/AI_Research_Agent.git
cd ai-research-agent
pip install -r requirements.txt
```

### 2. Configure environment
Create a `.env` file:
```env
OPENAI_API_KEY=sk-xxxx
OPENAI_MODEL=gpt-4o-mini
TAVILY_API_KEY=tvly-xxxx
FLASK_SECRET=your-secret-key
PORT=8000
```

### 3. Start server
```bash
python -m app.main
```
Then open: [http://localhost:8000](http://localhost:8000)

---

## Example Results

### Query: *Impact of Mediterranean diet on heart health*

**Key Findings**
- The Mediterranean diet emphasizes the removal of processed foods, saturated fats, and added sugars, which are linked to increased heart disease risk.  
- Incorporating fresh fruits, vegetables, and seeds is crucial for nutrient diversity and heart health.  
- Extra virgin olive oil provides significant cardiovascular benefits.  
- Regular nuts and fatty fish intake supports heart health.  
- Studies show adherence can reduce the risk of heart attack recurrence.  

**Where Sources Agree**
- Whole foods and healthy fats are consistently linked to better heart outcomes.  
- Avoiding processed foods aligns with reduced heart disease risk.  

**Caveats & Gaps**
- Benefits may vary by individual lifestyle.  
- The role of red wine remains debated.  
- Access to Mediterranean diet foods is limited in some regions.  

**Sources**
- The Mediterranean Diet: A Heart-Healthy Way To Eat  
- After a heart attack, the Mediterranean diet significantly reduces recurrence *(Source unavailable – timeout)*  
- Long-term impact of Mediterranean diet on cardiovascular disease *(Blocked by site)*  

---

## Where AI Helped
This project was developed with AI assistance for two parts:
- Frontend development: creating the HTML templates, CSS styling, and improving the user interface.
- Error handling & exceptions: designing clean, user-friendly error messages (e.g., Blocked by site, Source unavailable).

---

## Demo Video
- Demo video showing query -> results -> saved report -> viewing it on the web can be visiable in Demo_video.mp4 file
