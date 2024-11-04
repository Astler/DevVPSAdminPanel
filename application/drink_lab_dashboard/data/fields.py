from enum import Enum


class DrinkLabFields(Enum):
    # Basic fields
    NAME_EN = 'Name (EN)'
    NAME_RU = 'Name (RU)'
    DESCRIPTION = 'Description'
    INGREDIENTS = 'Ingredients'
    GADGETS = 'Gadgets'

    # Properties fields
    CATEGORY = 'Category'
    STRENGTH = 'Strength'
    TASTE = 'Taste'
    BASE = 'Base'
    GROUP = 'Group'
    METHOD = 'Method'

    @classmethod
    def property_fields(cls) -> list:
        """Returns list of fields that represent drink properties"""
        return [
            cls.STRENGTH.value,
            cls.TASTE.value,
            cls.BASE.value,
            cls.GROUP.value,
            cls.METHOD.value
        ]

    @classmethod
    def required_fields(cls) -> list:
        """Returns list of required fields"""
        return [
            cls.NAME_RU.value,
            # cls.NAME_EN.value
        ]