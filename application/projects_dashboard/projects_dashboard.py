import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from admin.data.flask_login import check_is_admin_or_exit
from admin.data.project_ids import ProjectId
from application.projects_dashboard.data.project_item import ProjectItem
from core.dependencies import app_sqlite_db

projects_blueprint = Blueprint('projects_blueprint', __name__)


@projects_blueprint.route('/projects')
@login_required
def projects_dashboard():
    if not check_is_admin_or_exit(ProjectId.PRESSF_CORE):
        return

    return render_template('projects_dashboard.html', projects=ProjectItem.query.all())


@projects_blueprint.route('/projects/add', methods=['POST'])
@login_required
def add_project():
    if not check_is_admin_or_exit(ProjectId.PRESSF_CORE):
        return

    name = request.form.get('name')

    if not name:
        flash('Name and API key are required')
        return redirect(url_for('projects_blueprint.projects_dashboard'))

    project = ProjectItem(
        name=name,
        api_key=str(uuid.uuid4()),
        date=int(datetime.now().timestamp())
    )

    try:
        app_sqlite_db.session.add(project)
        app_sqlite_db.session.commit()
        flash('Project added successfully')
    except Exception as e:
        app_sqlite_db.session.rollback()
        flash('Error adding project')

    return redirect(url_for('projects_blueprint.projects_dashboard'))


@projects_blueprint.route('/projects/<int:project_id>')
@login_required
def project_details(project_id):
    if not check_is_admin_or_exit(ProjectId.PRESSF_CORE):
        return

    project = ProjectItem.query.get_or_404(project_id)
    return render_template('project_details.html', project=project)


@projects_blueprint.route('/projects/<int:project_id>/update', methods=['POST'])
@login_required
def update_project(project_id):
    if not check_is_admin_or_exit(ProjectId.PRESSF_CORE):
        return

    project = ProjectItem.query.get_or_404(project_id)
    name = request.form.get('name')

    if not name:
        flash('Project name is required')
        return redirect(url_for('projects_blueprint.project_details', project_id=project_id))

    try:
        project.name = name
        app_sqlite_db.session.commit()
        flash('Project updated successfully')
    except Exception as e:
        app_sqlite_db.session.rollback()
        flash('Error updating project')

    return redirect(url_for('projects_blueprint.project_details', project_id=project_id))


@projects_blueprint.route('/projects/<int:project_id>/delete')
@login_required
def delete_project(project_id):
    if not check_is_admin_or_exit(ProjectId.PRESSF_CORE):
        return

    project = ProjectItem.query.get_or_404(project_id)

    try:
        app_sqlite_db.session.delete(project)
        app_sqlite_db.session.commit()
        flash('Project deleted successfully')
    except Exception as e:
        app_sqlite_db.session.rollback()
        flash('Error deleting project')

    return redirect(url_for('projects_blueprint.projects_dashboard'))
