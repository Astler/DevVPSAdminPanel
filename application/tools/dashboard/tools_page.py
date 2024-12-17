import os
import time
import zipfile
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, session
from flask import render_template, request, url_for, send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename, send_file

from application.tools.colors_reducer.utils import reduce_image_colors
import re
import json
import shutil
from application.drink_lab_dashboard.data.google_sheet_service import GoogleSheetsService
from application.tools.user_storage import UserStorage

tools_blueprint = Blueprint('tools_blueprint', __name__)


@tools_blueprint.route('/tools')
def tools():
    buttons = [
        {
            'label': 'Colors Reducer',
            'url': url_for('tools_blueprint.colors_reducer'),
        },
        {
            'label': 'Sheets To Android Strings',
            'url': url_for('tools_blueprint.strings_exporter'),  # Updated URL
        }
    ]
    return render_template(
        'tools_page.html',
        buttons=buttons
    )


@tools_blueprint.route('/tools/colors_reducer', methods=['GET', 'POST'])
def colors_reducer():
    if request.method == 'GET':
        return render_template('png_colors_reducer.html')

    elif request.method == 'POST':
        storage = UserStorage(current_app.config['UPLOAD_FOLDER'])
        user_folder = storage.get_user_folder()

        if 'images' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('images')
        num_colors = int(request.form.get('num_colors', 256))
        processed_images = []

        # Cleanup old files in user's folder
        for filename in os.listdir(user_folder):
            if filename.startswith('temp_') or filename.startswith('reduced_'):
                os.remove(os.path.join(user_folder, filename))

        for file in files:
            if not file or not file.filename:
                continue

            if allowed_file(file.filename):
                try:
                    unique_id = str(uuid4())
                    original_ext = os.path.splitext(file.filename)[1]
                    temp_filename = f"temp_{unique_id}{original_ext}"
                    reduced_filename = f"reduced_{unique_id}{original_ext}"

                    temp_path = os.path.join(user_folder, temp_filename)
                    reduced_path = os.path.join(user_folder, reduced_filename)

                    file.save(temp_path)
                    reduce_image_colors(temp_path, num_colors, reduced_path)

                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                    if os.path.exists(reduced_path):
                        # Return cached URL for frontend
                        cache_url = url_for('tools_blueprint.uploaded_file',
                                            filename=reduced_filename,
                                            user_folder=session['user_folder'],
                                            _external=True,
                                            _scheme='https')
                        processed_images.append({
                            'reduced': cache_url,
                            'originalName': file.filename,
                            'success': True,
                            'cacheKey': unique_id  # For browser caching
                        })
                except Exception as e:
                    current_app.logger.error(f"Error processing {file.filename}: {str(e)}")
                    processed_images.append({
                        'originalName': file.filename,
                        'success': False,
                        'error': str(e)
                    })
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        if not processed_images:
            return jsonify({'error': 'No valid images were processed'}), 400

        # Cleanup old folders
        storage.cleanup_old_folders()

        return jsonify({
            'images': processed_images,
            'baseUrl': request.host_url.rstrip('/')
        })


@tools_blueprint.route('/tools/clear_compressed', methods=['POST'])
@login_required
def clear_compressed():
    """Clear all processed files"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    try:
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        current_app.logger.error(f"Error clearing upload folder: {str(e)}")
    return jsonify({'status': 'success'})


def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


@tools_blueprint.route('/tools/download_compressed')
@login_required
def download_compressed():
    upload_folder = current_app.config['UPLOAD_FOLDER'] + "/" + session['user_folder']
    zip_path = os.path.join(upload_folder, 'compressed_images.zip')

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(upload_folder):
            if file.startswith('reduced_'):
                file_path = os.path.join(upload_folder, file)
                zipf.write(file_path, file)

    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name='compressed_images.zip',
        environ=request.environ
    )


@tools_blueprint.route('/uploads/<user_folder>/<filename>')
@login_required
def uploaded_file(user_folder, filename):
    try:
        # Security check - only allow access to own folder
        if session.get('user_folder') != user_folder:
            return jsonify({'error': 'Unauthorized'}), 403

        user_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user_folder)
        response = send_from_directory(user_folder_path, filename)

        # Add caching headers
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        response.headers['ETag'] = f'"{hash(filename)}"'

        return response
    except Exception as e:
        current_app.logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': 'File not found'}), 404


@tools_blueprint.route('/tools/strings_exporter')
def strings_exporter():
    return render_template('strings_exporter.html')


@tools_blueprint.route('/tools/export_strings', methods=['POST', 'GET', 'OPTIONS'])
def export_strings():
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    # Get sheets URL either from GET or POST
    sheets_url = request.args.get('sheetsUrl') or request.json.get('sheetsUrl')

    if not sheets_url:
        return jsonify({'error': 'No sheets URL provided'}), 400

    try:
        spreadsheet_id = extract_spreadsheet_id(sheets_url)
        sheets_service = GoogleSheetsService(json.loads(os.environ.get('GOOGLE_CREDENTIALS')))

        sheet_metadata = sheets_service.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])

        temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'strings_temp')

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        for sheet in sheets:
            sheet_title = sheet['properties']['title']

            lang_dir = os.path.join(temp_dir, f'values-{sheet_title.lower()}')
            if sheet_title.lower() == 'en':
                lang_dir = os.path.join(temp_dir, 'values')
            os.makedirs(lang_dir)

            result = sheets_service.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_title}!A:B'
            ).execute()

            rows = result.get('values', [])
            if not rows:
                continue

            # Generate strings.xml
            with open(os.path.join(lang_dir, 'strings.xml'), 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write('<resources>\n')

                for row in rows[1:]:
                    if len(row) >= 2:
                        key = row[0].strip()
                        value = row[1].strip().replace('"', '\\"')
                        f.write(f'    <string name="{key}">{value}</string>\n')

                f.write('</resources>')

        zip_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'android_strings.zip')
        if os.path.exists(zip_path):
            os.remove(zip_path)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        shutil.rmtree(temp_dir)

        return send_file(
            zip_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name='android_strings.zip',
            environ=request.environ
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tools_blueprint.route('/tools/download_strings')
def download_strings():
    zip_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'android_strings.zip')
    if not os.path.exists(zip_path):
        return jsonify({'error': 'No exported strings found'}), 404

    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name='android_strings.zip',
        environ=request.environ
    )


def extract_spreadsheet_id(url):
    """Extract spreadsheet ID from Google Sheets URL"""
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    raise ValueError('Invalid Google Sheets URL')
