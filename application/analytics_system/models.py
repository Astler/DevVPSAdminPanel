from datetime import datetime

from application.analytics_system.tasks import AnalyticsQueue
from core.dependencies import app_sqlite_db


class AnalyticsEvent(app_sqlite_db.Model):
    __abstract__ = True

    id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    key = app_sqlite_db.Column(app_sqlite_db.String(100), nullable=False)
    value_string = app_sqlite_db.Column(app_sqlite_db.String)
    value_int = app_sqlite_db.Column(app_sqlite_db.Integer)
    value_float = app_sqlite_db.Column(app_sqlite_db.Float)
    value_type = app_sqlite_db.Column(app_sqlite_db.String(20), nullable=False)
    timestamp = app_sqlite_db.Column(app_sqlite_db.DateTime, default=datetime.utcnow)

    def set_value(self, value):
        if isinstance(value, str):
            self.value_string = value
            self.value_type = 'string'
        elif isinstance(value, int):
            self.value_int = value
            self.value_type = 'int'
        elif isinstance(value, float):
            self.value_float = value
            self.value_type = 'float'

    def get_value(self):
        if self.value_type == 'string':
            return self.value_string
        elif self.value_type == 'int':
            return self.value_int
        elif self.value_type == 'float':
            return self.value_float


class AnalyticsManager:
    _event_models = {}

    @classmethod
    def get_model_for_project(cls, project_id):
        if project_id not in cls._event_models:
            table_name = f'analytics_events_project_{project_id}'

            # Create new model class for this project
            class ProjectAnalyticsEvent(AnalyticsEvent):
                __tablename__ = table_name
                __table_args__ = {'extend_existing': True}

            cls._event_models[project_id] = ProjectAnalyticsEvent

            # Create table if it doesn't exist
            if not ProjectAnalyticsEvent.__table__.exists(app_sqlite_db.engine):
                ProjectAnalyticsEvent.__table__.create(app_sqlite_db.engine)

        return cls._event_models[project_id]

    @classmethod
    def track_event(cls, project_id, key, value):
        AnalyticsQueue.enqueue(project_id, key, value)