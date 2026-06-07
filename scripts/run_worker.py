"""Start an RQ worker for the transcription queue.

Run from the project root:   python -m scripts.run_worker

WHY THIS SCRIPT EXISTS:
On macOS, RQ's default worker fork()s a child process per job. faster-whisper
pulls in native libraries (objc / PyAV / ctranslate2) that are NOT safe to use
after a bare fork() without exec() on macOS -- the child aborts with signal 6
and an "objc[...] +[NSMutableString initialize] may have been in progress..."
crash. The fix is SimpleWorker, which runs jobs IN the worker process (no fork).

On Linux fork() is safe and the default forking
Worker is preferable -- it isolates crashes in a child process. So we pick the
class by platform: SimpleWorker on macOS, the normal Worker elsewhere.
"""

import platform

from rq import SimpleWorker, Worker

from app.core.config import settings

# Reuse the same queue object the API enqueues onto - it already holds the
# RQ-safe raw connection (NOT the decode_response=True one, which would
# corrupt RQ's binary job data). See the note in app/core/queue.py
from app.core.queue import queue


def main() -> None:
    is_macos = platform.system() == "Darwin"
    worker_class = SimpleWorker if is_macos else Worker

    # Use the queue's own (RQ-safe) connection for the worker too
    worker = worker_class([queue], connection=queue.connection)

    print(
        f"Starting {worker_class.__name__} on queue "
        f"'{settings.queue_name}' (platform={platform.system()})"
    )
    worker.work()


if __name__ == "__main__":
    main()
