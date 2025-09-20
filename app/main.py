from __future__ import annotations
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session
from markdown import markdown
from .db import engine, get_db
from .models import Base, Report, Source
from .agent import Agent

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
    Base.metadata.create_all(bind=engine)

    @app.route("/")
    def index():
        with next(get_db()) as db:  # type: Session
            reports = db.query(Report).order_by(Report.created_at.desc()).all()
        return render_template("index.html", reports=reports)

    @app.route("/run", methods=["POST"])
    def run_query():
        query = request.form.get("query", "").strip()
        if not query:
            flash("Please enter a query.", "error")
            return redirect(url_for("index"))

        with next(get_db()) as db:  # type: Session
            agent = Agent(db)
            report = agent.run(query)
            if report.summary_md.startswith("# Search failed"):
                flash("Search failed. Report saved with error details.", "error")
            elif report.summary_md.startswith("# Summarization failed"):
                flash("Summarization failed. Report saved with search results only.", "error")
            else:
                flash("Report created successfully!", "success")
        return redirect(url_for("view_report", report_id=report.id))

    @app.route("/report/<int:report_id>")
    def view_report(report_id: int):
        with next(get_db()) as db:  # type: Session
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                flash("Report not found.", "error")
                return redirect(url_for("index"))
            sources = db.query(Source).filter(Source.report_id == report_id).all()

        html = markdown(
            report.summary_md,
            extensions=["fenced_code", "tables", "toc", "sane_lists"],
            output_format="html5",
        )
        return render_template("report.html", report=report, sources=sources, html=html)

    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=True)
