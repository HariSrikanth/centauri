"""Celery tasks for alpha.me."""

from apps.workers.tasks.ai import (
    find_matches,
    generate_clarifier_questions,
    generate_newsletter,
    generate_narratives,
    process_match_feedback,
    update_user_embeddings,
)
from apps.workers.tasks.ingestion import (
    ingest_calendar_activities,
    ingest_gmail_activities,
    ingest_github_activities,
    ingest_twitter_activities,
    ingest_web_mentions,
    process_activity_embeddings,
)

__all__ = [
    # AI tasks
    "find_matches",
    "generate_clarifier_questions",
    "generate_newsletter",
    "generate_narratives",
    "process_match_feedback",
    "update_user_embeddings",
    # Ingestion tasks
    "ingest_calendar_activities",
    "ingest_gmail_activities",
    "ingest_github_activities",
    "ingest_twitter_activities",
    "ingest_web_mentions",
    "process_activity_embeddings",
] 