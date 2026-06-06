"""The single module that knows about Redis.

Two distinct things live here:
    1. The RQ Queue -> "run this function in a worker process later"
    2. Job-hash helpers -> independent of RQ's internal bookkeeping.
    The status endpoint and the worker both read/write job state through
    these helpers, never by touching Redis directly.
"""

import json
from typing import Any

from redis import Redis
from rq import Queue

from app.core.config import settings

# One shared connection. decode_responses=True so hash read come back as
# str instead of bytes -- saves .decode() noise everywhere
redis_conn = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
)

# The RQ queue the API enqueues onto and the worker listens on.
# NOTE: RQ needs its own connection. decode_responses=True breaks RQ's
# internal (pickled, binary) bookkeeping, so give it a separate raw client

_rq_conn = Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
)
queue = Queue(
    settings.queue_name, connection=_rq_conn, default_timeout=settings.job_timeout
)


def _job_key(job_id: str) -> str:
    return f"job:{job_id}"


def save_job(job_id: str, data: dict[str, Any]) -> None:
    """Create/overwrite fields on a job's hash.

    Values must be Redis-storable (str/int/float). Anything structured
    (lists, dicts) gets JSON-encoded here and decoded in get_job
    """
    flat: dict[str, str] = {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            flat[k] = json.dumps(v)
        elif v is None:
            flat[k] = ""
        else:
            flat[k] = str(v)
    key = _job_key(job_id)
    redis_conn.hset(key, mapping=flat)
    # Expire the whole hash after job_ttl so finished jobs don't pile up forever
    redis_conn.expire(key, settings.job_ttl)


def update_job(job_id: str, **fields: Any) -> None:
    """Patch a few fields on an existing job hash (e.g. status, progress)"""
    save_job(job_id, fields)


def get_job(job_id: str) -> dict[str, str] | None:
    """Return the full job hash, or None if it doesn't exist / expired"""
    data = redis_conn.hgetall(_job_key(job_id))
    return data or None
