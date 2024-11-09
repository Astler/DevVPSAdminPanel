import os
import zipfile

from flask import Blueprint, current_app, jsonify
from flask import render_template, request, url_for, send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename, send_file

from application.tools.colors_reducer.utils import reduce_image_colors
import re
import json
import shutil
from application.drink_lab_dashboard.data.google_sheet_service import GoogleSheetsService

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


# inspired by https://onlinepngtools.com/decrease-png-color-count
# todo https://onlinepngtools.com/find-png-color-count
@tools_blueprint.route('/tools/colors_reducer', methods=['GET', 'POST'])
@login_required
def colors_reducer():
    if request.method == 'GET':
        return render_template('png_colors_reducer.html')

    elif request.method == 'POST':
        if 'images' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('images')
        num_colors = int(request.form['num_colors'])

        processed_images = []
        upload_folder = current_app.config['UPLOAD_FOLDER']

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                original_path = os.path.join(upload_folder, filename)
                file.save(original_path)

                reduced_filename = f"reduced_{filename}"
                reduced_path = os.path.join(upload_folder, reduced_filename)

                try:
                    reduce_image_colors(original_path, num_colors, reduced_path)
                    processed_images.append({
                        'original': url_for('tools_blueprint.uploaded_file', filename=filename),
                        'reduced': url_for('tools_blueprint.uploaded_file', filename=reduced_filename)
                    })
                except Exception as e:
                    current_app.logger.error(f"Error processing image {filename}: {str(e)}")

        return jsonify({'images': processed_images})


@tools_blueprint.route('/tools/download_compressed')
@login_required
def download_compressed():
    upload_folder = current_app.config['UPLOAD_FOLDER']
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


@tools_blueprint.route('/tools/clear_compressed', methods=['POST'])
@login_required
def clear_compressed():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    for file in os.listdir(upload_folder):
        if file.startswith('reduced_'):
            os.remove(os.path.join(upload_folder, file))
    return jsonify({'status': 'success'})


@tools_blueprint.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


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
