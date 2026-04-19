"""In-memory rate limiter for AI features. Works for single-instance dev/prod."""
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# In-memory store: {user_id: [(count, reset_at), ...]}
_rewrite_counts: dict[int, list[tuple[int, datetime]]] = defaultdict(list)
_coverletter_counts: dict[int, list[tuple[int, datetime]]] = defaultdict(list)


def _clean_old(counts_dict: dict, user_id: int) -> None:
    """Remove expired entries for a user."""
    now = datetime.now(timezone.utc)
    counts_dict[user_id] = [
        (count, ts) for count, ts in counts_dict[user_id] if ts > now
    ]


def get_rewrite_remaining(user_id: int, daily_limit: int) -> int:
    """Return how many rewrites are left for today."""
    _clean_old(_rewrite_counts, user_id)
    used = sum(count for count, _ in _rewrite_counts[user_id])
    return max(0, daily_limit - used)


def record_rewrite(user_id: int, daily_limit: int) -> bool:
    """
    Record one rewrite. Returns True if allowed, False if rate limit exceeded.
    """
    _clean_old(_rewrite_counts, user_id)
    now = datetime.now(timezone.utc)
    reset_at = now + timedelta(hours=24)
    used = sum(count for count, _ in _rewrite_counts[user_id])
    if used >= daily_limit:
        return False
    _rewrite_counts[user_id].append((1, reset_at))
    return True


def get_coverletter_remaining(user_id: int, daily_limit: int) -> int:
    _clean_old(_coverletter_counts, user_id)
    used = sum(count for count, _ in _coverletter_counts[user_id])
    return max(0, daily_limit - used)


def record_coverletter(user_id: int, daily_limit: int) -> bool:
    _clean_old(_coverletter_counts, user_id)
    now = datetime.now(timezone.utc)
    reset_at = now + timedelta(hours=24)
    used = sum(count for count, _ in _coverletter_counts[user_id])
    if used >= daily_limit:
        return False
    _coverletter_counts[user_id].append((1, reset_at))
    return True