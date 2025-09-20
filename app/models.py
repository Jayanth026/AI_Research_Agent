from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Text, ForeignKey

class Base(DeclarativeBase):
    pass

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    summary_md: Mapped[str] = mapped_column(Text, nullable=False)

    sources: Mapped[list["Source"]] = relationship("Source", back_populates="report", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="ok")  # ok | blocked | error | skipped
    note: Mapped[str] = mapped_column(Text, nullable=True)

    report: Mapped[Report] = relationship("Report", back_populates="sources")
