#!/usr/bin/env python3
"""
Script: Monthly Analysis Report

Generate comprehensive monthly report from saved articles.

Usage:
    python scripts/monthly_report.py [--month 2024-03]
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import get_session
from src.infrastructure.repositories.news_repository import NewsRepository
from loguru import logger


def generate_monthly_report(year_month=None):
    """
    Generate monthly analysis report.

    Args:
        year_month: Format "2024-03" or None for current month
    """
    if year_month is None:
        year_month = datetime.now().strftime("%Y-%m")

    logger.info(f"Generating report for {year_month}")

    # Get all articles
    session = get_session()
    news_repo = NewsRepository(session)

    articles = news_repo.find_all(limit=100000)

    # Convert to DataFrame
    data = []
    for article in articles:
        data.append(
            {
                "content": article.content,
                "category": article.category,
                "sentiment_label": article.sentiment_label,
                "sentiment_polarity": (
                    article.sentiment_score.polarity
                    if article.sentiment_score
                    else None
                ),
                "created_at": article.created_at,
                "word_count": len(article.content.split()),
            }
        )

    df = pd.DataFrame(data)

    if df.empty:
        logger.warning("No articles found")
        return

    # Filter by month
    df["month"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m")
    monthly_df = df[df["month"] == year_month]

    if monthly_df.empty:
        logger.warning(f"No articles for {year_month}")
        return

    # Generate report
    report = {
        "period": year_month,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_articles": len(monthly_df),
            "total_words": int(monthly_df["word_count"].sum()),
            "avg_words_per_article": float(monthly_df["word_count"].mean()),
        },
        "by_category": monthly_df["category"].value_counts().to_dict(),
        "by_sentiment": monthly_df["sentiment_label"].value_counts().to_dict(),
        "sentiment_by_category": {},
    }

    # Cross-analysis: sentiment by category
    for category in monthly_df["category"].unique():
        cat_df = monthly_df[monthly_df["category"] == category]
        report["sentiment_by_category"][category] = {
            "positive": int((cat_df["sentiment_label"] == "positive").sum()),
            "negative": int((cat_df["sentiment_label"] == "negative").sum()),
            "neutral": int((cat_df["sentiment_label"] == "neutral").sum()),
            "avg_polarity": (
                float(cat_df["sentiment_polarity"].mean())
                if "sentiment_polarity" in cat_df
                else None
            ),
        }

    # Top keywords (if available)
    # This would require tokenization of content

    # Save report
    reports_dir = Path("data/reports")
    reports_dir.mkdir(exist_ok=True)

    report_file = reports_dir / f"monthly_report_{year_month}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    logger.success(f"Report saved: {report_file}")

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"MONTHLY REPORT: {year_month}")
    print(f"{'=' * 60}")
    print(f"\n📊 Summary:")
    print(f"  Total Articles: {report['summary']['total_articles']:,}")
    print(f"  Total Words: {report['summary']['total_words']:,}")
    print(f"  Avg Words/Article: {report['summary']['avg_words_per_article']:.0f}")

    print(f"\n📚 By Category:")
    for cat, count in sorted(
        report["by_category"].items(), key=lambda x: x[1], reverse=True
    ):
        print(
            f"  {cat:20} {count:5} ({count / report['summary']['total_articles'] * 100:.1f}%)"
        )

    print(f"\n😊 By Sentiment:")
    for sent, count in sorted(
        report["by_sentiment"].items(), key=lambda x: x[1], reverse=True
    ):
        print(
            f"  {sent:20} {count:5} ({count / report['summary']['total_articles'] * 100:.1f}%)"
        )

    print(f"\n🎯 Most Positive Category:")
    most_positive = max(
        report["sentiment_by_category"].items(),
        key=lambda x: x[1].get("avg_polarity", 0),
    )
    print(f"  {most_positive[0]}: {most_positive[1].get('avg_polarity', 0):.2f}")

    print(f"\n{'=' * 60}\n")

    session.close()

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate monthly analysis report")
    parser.add_argument("--month", help="Month in format YYYY-MM (e.g., 2024-03)")
    args = parser.parse_args()

    generate_monthly_report(args.month)
