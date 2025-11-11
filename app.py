# app.py
from flask import Flask, render_template, request, jsonify
from classify_event import classify_event
from agent_core import analyze_event
from config import OUTPUT_DIR
import datetime, json

app = Flask(__name__, template_folder="templates", static_folder="static")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    event_text = request.form.get("event") or request.json.get("event")

    ml_result = classify_event(event_text)
    llm_report = analyze_event(event_text, ml_result)

    # JSON 저장
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    out_path = OUTPUT_DIR / f"{timestamp}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(llm_report, f, ensure_ascii=False, indent=2)

    return render_template("dashboard.html", report=llm_report)

@app.route("/api/recent", methods=["GET"])
def recent():
    """최근 분석 결과 조회 API"""
    json_files = sorted(OUTPUT_DIR.glob("*.json"))
    if not json_files:
        return jsonify({"error": "No reports found."}), 404
    latest = json_files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
