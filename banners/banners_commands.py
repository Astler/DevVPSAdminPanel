from app import app


@app.route('/get_all_banners', methods=['GET'])
def get_banners():
    return """All banners!"""
