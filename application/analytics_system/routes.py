from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
from flask_login import login_required
from sqlalchemy import func
from application.projects_dashboard.data.project_item import ProjectItem
from .models import AnalyticsManager
from core.dependencies import app_sqlite_db

analytics_blueprint = Blueprint('analytics', __name__)


def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return None
    return ProjectItem.query.filter_by(api_key=api_key).first()


@analytics_blueprint.route('/api/analytics/event', methods=['POST'])
def track_event():
    project = validate_api_key()
    if not project:
        return jsonify({'error': 'Invalid or missing API key'}), 401

    data = request.get_json()
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        AnalyticsManager.track_event(
            project_id=project.record_id,
            key=data['key'],
            value=data['value']
        )
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_blueprint.route('/api/analytics/events', methods=['GET'])
def get_events():
    project = validate_api_key()
    if not project:
        return jsonify({'error': 'Invalid or missing API key'}), 401

    days = request.args.get('days', 7, type=int)
    key = request.args.get('key')

    model = AnalyticsManager.get_model_for_project(project.record_id)
    query = model.query

    if key:
        query = query.filter_by(key=key)

    since = datetime.utcnow() - timedelta(days=days)
    query = query.filter(model.timestamp >= since)
    events = query.order_by(model.timestamp.desc()).all()

    return jsonify({
        'events': [{
            'key': event.key,
            'value': event.get_value(),
            'type': event.value_type,
            'timestamp': event.timestamp.isoformat()
        } for event in events]
    })


@analytics_blueprint.route('/api/analytics/aggregate', methods=['GET'])
def aggregate_events():
    project = validate_api_key()
    if not project:
        return jsonify({'error': 'Invalid or missing API key'}), 401

    days = request.args.get('days', 7, type=int)
    key = request.args.get('key')

    model = AnalyticsManager.get_model_for_project(project.record_id)
    since = datetime.utcnow() - timedelta(days=days)

    query = model.query.filter_by(key=key).filter(model.timestamp >= since)

    # Get value type for this key
    sample_event = query.first()
    if not sample_event:
        return jsonify({'error': 'No events found for this key'}), 404

    if sample_event.value_type in ('int', 'float'):
        # Numeric aggregations
        result = query.with_entities(
            func.avg(getattr(model, f'value_{sample_event.value_type}')).label('average'),
            func.min(getattr(model, f'value_{sample_event.value_type}')).label('minimum'),
            func.max(getattr(model, f'value_{sample_event.value_type}')).label('maximum'),
            func.count().label('count')
        ).first()

        return jsonify({
            'key': key,
            'type': sample_event.value_type,
            'stats': {
                'average': float(result.average) if result.average else 0,
                'minimum': result.minimum,
                'maximum': result.maximum,
                'count': result.count
            }
        })
    else:
        # String value frequency count
        values = query.with_entities(
            model.value_string,
            func.count(model.value_string).label('count')
        ).group_by(model.value_string).all()

        return jsonify({
            'key': key,
            'type': 'string',
            'values': [{
                'value': value,
                'count': count
            } for value, count in values]
        })


@analytics_blueprint.route('/analytics/test')
@login_required
def analytics_test_page():
    projects = ProjectItem.query.all()
    return render_template('analytics_test.html', projects=projects)


@analytics_blueprint.route('/analytics/test/send', methods=['POST'])
@login_required
def send_test_event():
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        project = ProjectItem.query.get_or_404(project_id)

        value = data['value']
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass

        AnalyticsManager.track_event(
            project_id=project.record_id,
            key=data['key'],
            value=value
        )

        return jsonify({'success': True, 'message': 'Event queued successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400