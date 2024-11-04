import json
import os
from datetime import datetime

from flask import Blueprint, render_template, url_for, flash, redirect, jsonify, current_app
from flask_login import login_required

from application.data.flask_login import check_is_admin_or_exit
from application.data.project_ids import ProjectId
from application.drink_lab_dashboard.data.drink_ingredient_model import DrinkIngredientModel
from application.drink_lab_dashboard.data.drink_model import DrinkModel, get_list_field
from application.drink_lab_dashboard.data.google_sheet_service import GoogleSheetsService
from application.drink_lab_dashboard.data.result_model import DrinkLabAnalysisResultModel

dashboard_drink_lab = Blueprint('dashboard_drink_lab', __name__)


@dashboard_drink_lab.route('/drink_lab/ingredients')
@login_required
def ingredients_list():
    if not check_is_admin_or_exit(ProjectId.DRINK_LAB):
        return

    ingredients = DrinkIngredientModel.get_all_ingredients()
    unique_values = DrinkIngredientModel.get_unique_values()

    return render_template(
        'ingredients_list.html',
        ingredients=ingredients,
        unique_values=unique_values
    )


@dashboard_drink_lab.route('/drink_lab/run_analysis')
@login_required
def run_analysis():
    if not check_is_admin_or_exit(ProjectId.DRINK_LAB):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        credentials_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not credentials_json:
            return jsonify({'error': 'Google credentials not configured'}), 500

        credentials_dict = json.loads(credentials_json)
        sheets_service = GoogleSheetsService(credentials_dict)

        analysis = DrinkLabAnalysisResultModel.start_new_analysis()

        ingredients_data = sheets_service.get_ingredients_data()
        DrinkIngredientModel.bulk_create_or_update(ingredients_data)

        known_ingredients = DrinkIngredientModel.get_all_ingredients()
        analysis.add_known_ingredients(known_ingredients)

        DrinkModel.delete_all_records()
        drinks_data = sheets_service.get_drinks_data()
        DrinkModel.bulk_create_or_update(drinks_data)

        known_drinks = DrinkModel.get_all_drinks()
        analysis.find_duplicates(known_drinks)
        # analysis.add_known_drinks(known_drinks)

        analysis.total_drinks = len(known_drinks)

        for drink in known_drinks:
            # Get lists from JSON strings
            strengths = get_list_field(drink.strength)
            tastes = get_list_field(drink.taste)
            bases = get_list_field(drink.base)
            groups = get_list_field(drink.group)
            methods = get_list_field(drink.method)

            # Add all properties
            for strength in strengths:
                analysis.add_strength(strength)
            for taste in tastes:
                analysis.add_taste(taste)
            for base in bases:
                analysis.add_base(base)
            for group in groups:
                analysis.add_group(group)
            for method in methods:
                analysis.add_method(method)

            # Validate ingredients
            analysis.validate_drink_ingredients(drink.name_ru, drink.ingredients)

        # Save analysis to DB
        analysis.save_analysis()

        return jsonify(analysis.to_dict())

    except Exception as e:
        current_app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_drink_lab.route('/drink_lab/drinks')
@login_required
def drinks_list():
    if not check_is_admin_or_exit(ProjectId.DRINK_LAB):
        return

    drinks = DrinkModel.get_all_drinks()
    return render_template(
        'drinks_list.html',
        drinks=drinks
    )


@dashboard_drink_lab.route('/drink_lab/dashboard')
@login_required
def drink_lab_dashboard():
    if not check_is_admin_or_exit(ProjectId.DRINK_LAB):
        return

    analysis = DrinkLabAnalysisResultModel.get_latest()
    stats = analysis.to_dict() if analysis else {
        'total_drinks': 0,
        'last_check': 'Never',
        'duplicate_names': [],
        'missing_ingredients': [],
        'strengths': [],
        'tastes': [],
        'bases': [],
        'groups': [],
        'methods': []
    }

    buttons = [
        {
            'label': 'Run Analysis',
            'url': url_for('dashboard_drink_lab.run_analysis'),
        },
        {
            'label': 'View Ingredients',
            'url': url_for('dashboard_drink_lab.ingredients_list'),
        },
        {
            'label': 'View Drinks',
            'url': url_for('dashboard_drink_lab.drinks_list'),
        }
    ]

    return render_template(
        'drink_lab_dashboard.html',
        stats=stats,
        buttons=buttons
    )
