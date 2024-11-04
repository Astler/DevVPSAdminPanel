from datetime import datetime
from typing import List
import json

from application.drink_lab_dashboard.data.fields import DrinkLabFields
from core.dependencies import app_sqlite_db


def get_list_field(field_value: str) -> List[str]:
    """Convert string field to list, handling both JSON and comma-separated values"""
    if not field_value:
        return []
    try:
        return json.loads(field_value)
    except json.JSONDecodeError:
        return [item.strip() for item in field_value.split(',') if item.strip()]


class DrinkModel(app_sqlite_db.Model):
    __tablename__ = 'drinks_models'

    id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    name_ru = app_sqlite_db.Column(app_sqlite_db.String(200))
    name_en = app_sqlite_db.Column(app_sqlite_db.String(200))
    category = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    strength = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    taste = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    base = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    group = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    method = app_sqlite_db.Column(app_sqlite_db.Text)  # JSON list
    ingredients = app_sqlite_db.Column(app_sqlite_db.Text)
    gadgets = app_sqlite_db.Column(app_sqlite_db.Text)
    description = app_sqlite_db.Column(app_sqlite_db.Text)
    created_at = app_sqlite_db.Column(app_sqlite_db.BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = app_sqlite_db.Column(app_sqlite_db.BigInteger, onupdate=lambda: int(datetime.now().timestamp()))

    @classmethod
    def get_all_drinks(cls):
        return cls.query.order_by(cls.name_ru).all()

    @classmethod
    def delete_all_records(cls):
        app_sqlite_db.session.query(cls).delete()

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
        """Get unique values across all list fields"""

        def get_unique_from_field(field):
            values = set()
            for row in app_sqlite_db.session.query(field).distinct():
                if row[0]:
                    items = get_list_field(row[0])
                    values.update(items)
            return sorted(list(values))

        return {
            'strengths': get_unique_from_field(cls.strength),
            'tastes': get_unique_from_field(cls.taste),
            'bases': get_unique_from_field(cls.base),
            'groups': get_unique_from_field(cls.group),
            'methods': get_unique_from_field(cls.method)
        }

    @classmethod
    def bulk_create_or_update(cls, drinks_data):
        for data in drinks_data:
            new_drink = cls(
                name_ru=data[DrinkLabFields.NAME_RU.value],
                name_en=data.get(DrinkLabFields.NAME_EN.value, ''),
                category=cls().set_list_field(data.get(DrinkLabFields.CATEGORY.value, '')),
                strength=cls().set_list_field(data.get(DrinkLabFields.STRENGTH.value, '')),
                taste=cls().set_list_field(data.get(DrinkLabFields.TASTE.value, '')),
                base=cls().set_list_field(data.get(DrinkLabFields.BASE.value, '')),
                group=cls().set_list_field(data.get(DrinkLabFields.GROUP.value, '')),
                method=cls().set_list_field(data.get(DrinkLabFields.METHOD.value, '')),
                ingredients=data.get(DrinkLabFields.INGREDIENTS.value, ''),
                gadgets=data.get(DrinkLabFields.GADGETS.value, ''),
                description=data.get(DrinkLabFields.DESCRIPTION.value, '')
            )
            app_sqlite_db.session.add(new_drink)
        # for data in drinks_data:
        #     existing = cls.query.filter_by(name_ru=data[DrinkLabFields.NAME_RU.value]).first()
        #     if existing:
        #         for key, value in data.items():
        #             if key == DrinkLabFields.NAME_RU.value:
        #                 continue
        #             field_name = cls._map_column_name(key)
        #             if field_name in ['category', 'strength', 'taste', 'base', 'group', 'method']:
        #                 value = existing.set_list_field(value)
        #             setattr(existing, field_name, value)
        #         existing.updated_at = int(datetime.now().timestamp())
        #     else:
        #         new_drink = cls(
        #             name_ru=data[DrinkLabFields.NAME_RU.value],
        #             name_en=data.get(DrinkLabFields.NAME_EN.value, ''),
        #             category=cls().set_list_field(data.get(DrinkLabFields.CATEGORY.value, '')),
        #             strength=cls().set_list_field(data.get(DrinkLabFields.STRENGTH.value, '')),
        #             taste=cls().set_list_field(data.get(DrinkLabFields.TASTE.value, '')),
        #             base=cls().set_list_field(data.get(DrinkLabFields.BASE.value, '')),
        #             group=cls().set_list_field(data.get(DrinkLabFields.GROUP.value, '')),
        #             method=cls().set_list_field(data.get(DrinkLabFields.METHOD.value, '')),
        #             ingredients=data.get(DrinkLabFields.INGREDIENTS.value, ''),
        #             description=data.get(DrinkLabFields.DESCRIPTION.value, '')
        #         )
        #         app_sqlite_db.session.add(new_drink)

        app_sqlite_db.session.commit()

    def to_dict(self):
        """Convert model to dictionary using DrinkLabFields"""
        return {
            DrinkLabFields.NAME_RU.value: self.name_ru,
            DrinkLabFields.NAME_EN.value: self.name_en,
            DrinkLabFields.CATEGORY.value: get_list_field(self.category),
            DrinkLabFields.STRENGTH.value: get_list_field(self.strength),
            DrinkLabFields.TASTE.value: get_list_field(self.taste),
            DrinkLabFields.BASE.value: get_list_field(self.base),
            DrinkLabFields.GROUP.value: get_list_field(self.group),
            DrinkLabFields.METHOD.value: get_list_field(self.method),
            DrinkLabFields.INGREDIENTS.value: self.ingredients,
            DrinkLabFields.GADGETS.value: self.gadgets,
            DrinkLabFields.DESCRIPTION.value: self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create model instance from dictionary using DrinkLabFields"""
        return cls(
            name_ru=data[DrinkLabFields.NAME_RU.value],
            name_en=data.get(DrinkLabFields.NAME_EN.value),
            category=cls().set_list_field(data.get(DrinkLabFields.CATEGORY.value)),
            strength=cls().set_list_field(data.get(DrinkLabFields.STRENGTH.value)),
            taste=cls().set_list_field(data.get(DrinkLabFields.TASTE.value)),
            base=cls().set_list_field(data.get(DrinkLabFields.BASE.value)),
            group=cls().set_list_field(data.get(DrinkLabFields.GROUP.value)),
            method=cls().set_list_field(data.get(DrinkLabFields.METHOD.value)),
            ingredients=data.get(DrinkLabFields.INGREDIENTS.value),
            gadgets=data.get(DrinkLabFields.GADGETS.value),
            description=data.get(DrinkLabFields.DESCRIPTION.value)
        )

    @staticmethod
    def _map_column_name(key):
        """Map external field names to model column names"""
        mapping = {
            DrinkLabFields.NAME_RU.value: 'name_ru',
            DrinkLabFields.NAME_EN.value: 'name_en',
            DrinkLabFields.CATEGORY.value: 'category',
            DrinkLabFields.STRENGTH.value: 'strength',
            DrinkLabFields.TASTE.value: 'taste',
            DrinkLabFields.BASE.value: 'base',
            DrinkLabFields.GROUP.value: 'group',
            DrinkLabFields.METHOD.value: 'method',
            DrinkLabFields.INGREDIENTS.value: 'ingredients',
            DrinkLabFields.GADGETS.value: 'gadgets',
            DrinkLabFields.DESCRIPTION.value: 'description'
        }
        return mapping.get(key, key.lower())
