import os
import zipfile

import numpy as np
from PIL import Image
from flask import Blueprint, current_app, jsonify
from flask import render_template, request, url_for, send_from_directory
from flask_login import login_required
from sklearn.cluster import KMeans
from werkzeug.utils import secure_filename, send_file

tools_blueprint = Blueprint('tools_blueprint', __name__)


@tools_blueprint.route('/tools')
@login_required
def tools():
    buttons = [
        {
            'label': 'Colors Reducer',
            'url': url_for('tools_blueprint.colors_reducer'),
        }
    ]
    return render_template(
        'tools_page.html',
        buttons=buttons
    )


@tools_blueprint.route('/tools/colors_reducer', methods=['GET', 'POST'])
@login_required
def colors_reducer():
    buttons = [
        {'url': url_for('tools_blueprint.tools'), 'label': 'Back to Tools'},
    ]

    if request.method == 'GET':
        return render_template('png_colors_reducer.html', buttons=buttons)

    elif request.method == 'POST':
        if 'images' not in request.files:  # Changed from 'images[]' to 'images'
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('images')  # Changed from 'images[]' to 'images'
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
                    reduce_colors(original_path, num_colors, reduced_path)
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


def reduce_colors(image_path, num_colors, output_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    data = np.array(img)
    pixels = data.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=0).fit(pixels)
    new_colors = kmeans.cluster_centers_[kmeans.labels_]
    new_image = new_colors.reshape(data.shape).astype(np.uint8)
    result = Image.fromarray(new_image)
    result.save(output_path)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}
