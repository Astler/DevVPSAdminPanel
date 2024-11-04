class ParsedIngredient:
    def __init__(self, name: str, amount: str):
        self.name = name
        self.amount = amount

    @staticmethod
    def parse(ingredient_str: str) -> 'ParsedIngredient':
        parts = ingredient_str.strip().split(' ')
        name_parts = []
        amount_parts = []

        for part in reversed(parts):
            if any(c.isdigit() for c in part):
                amount_parts.insert(0, part)
            else:
                name_parts.insert(0, part)

        name = ' '.join(name_parts).strip()
        amount = ' '.join(amount_parts).strip()

        return ParsedIngredient(name=name, amount=amount)