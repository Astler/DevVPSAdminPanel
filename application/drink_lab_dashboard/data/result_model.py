import json
from collections import defaultdict
from datetime import datetime

from application.drink_lab_dashboard.data.duplicate_info import DuplicateInfo
from core.dependencies import app_sqlite_db
from application.drink_lab_dashboard.data.drink_amount_ingredient_model import ParsedIngredient


class DrinkLabAnalysisModel(app_sqlite_db.Model):
    id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True, default=1)
    timestamp = app_sqlite_db.Column(app_sqlite_db.BigInteger)
    total_drinks = app_sqlite_db.Column(app_sqlite_db.Integer, default=0)
    duplicate_names = app_sqlite_db.Column(app_sqlite_db.Text, default='{}')  # JSON string
    missing_ingredients = app_sqlite_db.Column(app_sqlite_db.Text, default='[]')  # JSON string
    strengths = app_sqlite_db.Column(app_sqlite_db.Text, default='[]')  # JSON string
    tastes = app_sqlite_db.Column(app_sqlite_db.Text, default='[]')  # JSON string
    bases = app_sqlite_db.Column(app_sqlite_db.Text, default='[]')  # JSON string
    groups = app_sqlite_db.Column(app_sqlite_db.Text, default='[]')  # JSON string
    methods = app_sqlite_db.Column(app_sqlite_db.Text, default='[]')  # JSON string

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset_analysis()

    def reset_analysis(self):
        """Reset all analysis data to initial state"""
        self._known_ingredients = set()
        self._duplicate_names = {
            'by_ru_name': [],
            'by_en_name': [],
            'by_ingredients': []
        }
        self._missing_ingredients = []
        self._strengths = set()
        self._tastes = set()
        self._bases = set()
        self._groups = set()
        self._methods = set()
        self.total_drinks = 0
        # Initialize DB fields with empty JSON strings
        self.duplicate_names = '{}'
        self.missing_ingredients = '[]'
        self.strengths = '[]'
        self.tastes = '[]'
        self.bases = '[]'
        self.groups = '[]'
        self.methods = '[]'

    def find_duplicates(self, drinks_data):
        duplicates = {
            'by_ru_name': defaultdict(list),
            'by_en_name': defaultdict(list),
            'by_ingredients': defaultdict(list)
        }

        # Check for name duplicates
        for i, drink in enumerate(drinks_data):
            name_ru = drink.name_ru.strip()
            name_en = drink.name_en.strip() if drink.name_en else ''

            duplicates['by_ru_name'][name_ru].append(i)
            if name_en:
                duplicates['by_en_name'][name_en].append(i)

            # Create normalized ingredients key for comparison
            if drink.ingredients:
                normalized_ingredients = ','.join(sorted(
                    [i.strip().lower() for i in drink.ingredients.split(',')]
                ))
                duplicates['by_ingredients'][normalized_ingredients].append(i)

        # Convert to final format
        self._duplicate_names = {
            'by_ru_name': [
                DuplicateInfo(
                    name=name,
                    count=len(indexes),
                    items=[drinks_data[i].to_dict() for i in indexes]
                ).__dict__
                for name, indexes in duplicates['by_ru_name'].items()
                if len(indexes) > 1
            ],
            'by_en_name': [
                DuplicateInfo(
                    name=name,
                    count=len(indexes),
                    items=[drinks_data[i].to_dict() for i in indexes]
                ).__dict__
                for name, indexes in duplicates['by_en_name'].items()
                if len(indexes) > 1
            ],
            'by_ingredients': [
                DuplicateInfo(
                    name=ingredients,
                    count=len(indexes),
                    items=[drinks_data[i].to_dict() for i in indexes]
                ).__dict__
                for ingredients, indexes in duplicates['by_ingredients'].items()
                if len(indexes) > 1
            ]
        }

    @classmethod
    def start_new_analysis(cls):
        """Start new analysis by updating or creating record with id=1"""
        instance = cls.query.get(1)
        if not instance:
            instance = cls(id=1)
        else:
            instance.reset_analysis()
        return instance

    def add_known_ingredients(self, ingredients):
        for ingredient in ingredients:
            self._known_ingredients.add(ingredient.name_ru)

    def validate_drink_ingredients(self, drink_name: str, ingredients_str: str):
        if not ingredients_str:
            return

        ingredients_list = ingredients_str.split(',')
        for ingredient_str in ingredients_list:
            parsed = ParsedIngredient.parse(ingredient_str)
            if parsed.name not in self._known_ingredients:
                self._missing_ingredients.append((drink_name, parsed.name))

    def save_analysis(self):
        """Save analysis results to the database"""
        self.timestamp = int(datetime.now().timestamp())
        self.duplicate_names = json.dumps(self._duplicate_names, ensure_ascii=False)
        self.missing_ingredients = json.dumps(self._missing_ingredients, ensure_ascii=False)
        self.strengths = json.dumps(list(self._strengths), ensure_ascii=False)
        self.tastes = json.dumps(list(self._tastes), ensure_ascii=False)
        self.bases = json.dumps(list(self._bases), ensure_ascii=False)
        self.groups = json.dumps(list(self._groups), ensure_ascii=False)
        self.methods = json.dumps(list(self._methods), ensure_ascii=False)

        app_sqlite_db.session.add(self)
        app_sqlite_db.session.commit()

    def to_dict(self):
        return {
            'total_drinks': self.total_drinks,
            'last_check': datetime.fromtimestamp(self.timestamp).strftime(
                '%Y-%m-%d %H:%M:%S') if self.timestamp else 'Never',
            'duplicate_names': json.loads(self.duplicate_names) if self.duplicate_names else {},
            'missing_ingredients': [
                f'"{drink}" не найден ингредиент "{ingredient}"'
                for drink, ingredient in json.loads(self.missing_ingredients)
            ] if self.missing_ingredients else [],
            'strengths': json.loads(self.strengths) if self.strengths else [],
            'tastes': json.loads(self.tastes) if self.tastes else [],
            'bases': json.loads(self.bases) if self.bases else [],
            'groups': json.loads(self.groups) if self.groups else [],
            'methods': json.loads(self.methods) if self.methods else []
        }

    @classmethod
    def get_latest(cls):
        """Get latest analysis result"""
        return cls.query.get(1)

    # Helper methods for analysi
    def add_strength(self, value):
        if value: self._strengths.add(value)

    def add_taste(self, value):
        if value: self._tastes.add(value)

    def add_base(self, value):
        if value: self._bases.add(value)

    def add_group(self, value):
        if value: self._groups.add(value)

    def add_method(self, value):
        if value: self._methods.add(value)
