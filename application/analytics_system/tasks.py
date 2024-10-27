import threading
from datetime import datetime
from queue import Queue, Empty
import logging
import time
from flask import current_app

logger = logging.getLogger(__name__)

class AnalyticsQueue:
    _instance = None
    _queue = Queue()
    _worker = None
    _running = False

    @classmethod
    def initialize(cls, app):
        if not cls._instance:
            cls._instance = cls()
            cls._app = app
            cls._running = True
            cls._start_worker()
        return cls._instance

    @classmethod
    def _start_worker(cls):
        if not cls._worker or not cls._worker.is_alive():
            cls._worker = threading.Thread(target=cls._process_queue, daemon=True)
            cls._worker.start()

    @classmethod
    def _process_queue(cls):
        while cls._running:
            try:
                # Try to get an item from the queue with timeout
                try:
                    event_data = cls._queue.get(timeout=1.0)
                except Empty:
                    time.sleep(0.1)  # Sleep briefly when queue is empty
                    continue

                if event_data is None:
                    continue

                with cls._app.app_context():
                    from .models import AnalyticsManager
                    from core.dependencies import app_sqlite_db  # Import the db directly

                    model = AnalyticsManager.get_model_for_project(event_data['project_id'])
                    event = model()
                    event.key = event_data['key']
                    event.set_value(event_data['value'])
                    event.timestamp = datetime.utcnow()

                    app_sqlite_db.session.add(event)
                    app_sqlite_db.session.commit()

                    # Mark task as done
                    cls._queue.task_done()

            except Exception as e:
                if cls._running:
                    logger.error(f"Error processing analytics event: {str(e)}")
                time.sleep(0.1)  # Sleep briefly on error

    @classmethod
    def enqueue(cls, project_id: int, key: str, value: any):
        if cls._running:
            cls._queue.put({
                'project_id': project_id,
                'key': key,
                'value': value,
            })

    @classmethod
    def shutdown(cls):
        if cls._running:
            cls._running = False
            try:
                cls._queue.join()  # Wait for all tasks to complete
            except:
                pass  # Ignore any shutdown errors