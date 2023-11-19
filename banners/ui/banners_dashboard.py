import base64
import os

from firebase_admin import firestore
from flask import Blueprint, render_template, send_file
from flask_login import login_required
from PIL import Image, ImageDraw, ImageFilter, ImageColor
import io
import json
from random import randint, choice

from application import sign_up_enabled
from banners.banners_commands import get_daily_banner

dashboard_blueprint = Blueprint('dashboard_blueprint', __name__)


def get_banner_data_from_firestore(banner_id):
    firestore_db = firestore.client()

    try:
        # Attempt to get the document from Firestore
        banner_ref = firestore_db.collection('shared_banners').document(banner_id)
        banner_doc = banner_ref.get()
        if banner_doc.exists:
            return banner_doc.to_dict()
        else:
            # Handle the case where the banner doesn't exist
            print(f"No such banner with ID {banner_id}")
            return None
    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")
        return None


# Mock function to simulate getting banner data
def get_mock_banner_data(banner_id):
    banner_json = json.dumps(get_banner_data_from_firestore(banner_id))
    return json.loads(banner_json)


def apply_color_to_image(image, color):
    # Apply color to a given PIL image and return the colored image
    colored_image = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(colored_image)
    draw.rectangle([0, 0, image.size[0], image.size[1]], fill=color)
    return Image.alpha_composite(image, colored_image)


import os
from PIL import Image, ImageDraw, ImageChops


def apply_color_to_image(image, color):
    # Convert the hex color to an RGBA tuple
    color = ImageColor.getrgb(color) + (255,)

    # Create a solid color image and composite it using the source alpha
    color_layer = Image.new('RGBA', image.size, color)
    colored_image = ImageChops.multiply(image, color_layer)

    return colored_image


def upscale_image(image, factor):
    # Upscale the image using the nearest neighbor algorithm
    new_size = (image.size[0] * factor, image.size[1] * factor)
    return image.resize(new_size, Image.NEAREST)


def create_banner(layers, upscale_factor=1):
    # Base directory for patterns - adjust the path to where your app is running
    base_pattern_path = os.path.join('banners', 'assets', 'patterns')

    # Assume the base banner size from the first image
    first_image_path = os.path.join(base_pattern_path, layers[0]['patternName'] + ".png")

    with Image.open(first_image_path) as first_image:
        width, height = first_image.size

        banner = Image.new('RGBA', (width, height))

    # Composite layers onto the banner
    for layer in layers:
        show_it = layer.get('mIsVisible', True)  # Correct key name from 'misVisible' to 'mIsVisible'

        if not show_it:
            continue

        filename = layer['patternName'] + ".png"  # Ensure this is just the filename, not a URL
        pattern_file_path = os.path.join(base_pattern_path, filename)

        with Image.open(pattern_file_path) as layer_image:
            layer_image = layer_image.convert('RGBA')
            layer_image = layer_image.resize((width, height))  # Resize layer to match banner size

            colored_layer = apply_color_to_image(layer_image, layer['patternColor'])

            banner = Image.alpha_composite(banner, colored_layer)

    if upscale_factor != 1:
        banner = upscale_image(banner, upscale_factor)

    # Save the banner image to a bytes buffer
    img_byte_arr = io.BytesIO()
    banner.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr


@dashboard_blueprint.route('/be/dashboard')
@login_required
def banners_dashboard():
    daily_banner_data = get_daily_banner()

    if not daily_banner_data:
        return render_template('banners_dashboard.html', banner_data=None)

    banner_data = get_mock_banner_data(daily_banner_data.daily_banner_id)
    banner_image_io = create_banner(banner_data['mlayers'], 10)

    img_base64 = base64.b64encode(banner_image_io.getvalue()).decode('utf-8')
    img_data_url = f"data:image/png;base64,{img_base64}"

    # Render the template with the image data URL passed in the context
    return render_template(
        'banners_dashboard.html',
        sign_up_enabled=sign_up_enabled,
        name="Hellooooo",
        daily_banner_url=img_data_url
    )
