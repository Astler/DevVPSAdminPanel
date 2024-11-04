import json
from datetime import datetime

from application.drink_lab_dashboard.data.drink_model import get_list_field
from core.dependencies import app_sqlite_db


class DrinkIngredientModel(app_sqlite_db.Model):
    id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    name_ru = app_sqlite_db.Column(app_sqlite_db.String(200), unique=True)
    name_en = app_sqlite_db.Column(app_sqlite_db.String(200))
    category = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    strength = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    taste = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    base = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    description = app_sqlite_db.Column(app_sqlite_db.Text)
    created_at = app_sqlite_db.Column(app_sqlite_db.BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = app_sqlite_db.Column(app_sqlite_db.BigInteger, onupdate=lambda: int(datetime.now().timestamp()))

    @classmethod
    def get_all_ingredients(cls):
        return cls.query.order_by(cls.name_ru).all()

    @staticmethod
    def set_list_field(value) -> str:
        """Convert list or comma-separated string to JSON string"""
        if isinstance(value, str):
            items = [item.strip() for item in value.split(',') if item.strip()]
        elif isinstance(value, list):
            items = value
        else:
            items = []
        return json.dumps(items, ensure_ascii=False)

    @classmethod
    def get_unique_values(cls):
        def get_unique_from_field(field):
            values = set()
            for row in app_sqlite_db.session.query(field).distinct():
                if row[0]:
                    items = get_list_field(row[0])
                    values.update(items)
            return sorted(list(values))

        return {
            'categories': get_unique_from_field(cls.category),
            'strengths': get_unique_from_field(cls.strength),
            'tastes': get_unique_from_field(cls.taste),
            'bases': get_unique_from_field(cls.base)
        }

    @classmethod
    def bulk_create_or_update(cls, ingredients_data):
        for data in ingredients_data:
            existing = cls.query.filter_by(name_ru=data['Name (RU)']).first()
            if existing:
                for key, value in data.items():
                    if key == 'Name (RU)':
                        continue
                    field_name = cls._map_column_name(key)
                    if field_name in ['category', 'strength', 'taste', 'base']:
                        value = cls.set_list_field(value)
                    setattr(existing, field_name, value)
                existing.updated_at = int(datetime.now().timestamp())
            else:
                new_ingredient = cls(
                    name_ru=data['Name (RU)'],
                    name_en=data.get('Name (EN)', ''),
                    category=cls.set_list_field(data.get('Catehory', '')),
                    strength=cls.set_list_field(data.get('Strength', '')),
                    taste=cls.set_list_field(data.get('Taste', '')),
                    base=cls.set_list_field(data.get('Base', '')),
                    description=data.get('Description', '')
                )
                app_sqlite_db.session.add(new_ingredient)

        app_sqlite_db.session.commit()


    def to_dict(self):
        return {
            'name_ru': self.name_ru,
            'name_en': self.name_en,
            'category': get_list_field(self.category),
            'strength': get_list_field(self.strength),
            'taste': get_list_field(self.taste),
            'base': get_list_field(self.base),
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def _map_column_name(key):
        mapping = {
            'Name (RU)': 'name_ru',
            'Name (EN)': 'name_en',
            'Catehory': 'category',
            'Strength': 'strength',
            'Taste': 'taste',
            'Base': 'base',
            'Description': 'description'
        }
        return mapping.get(key, key.lower())