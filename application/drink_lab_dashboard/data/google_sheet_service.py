from google.oauth2 import service_account
from googleapiclient.discovery import build

from application.drink_lab_dashboard.data.fields import DrinkLabFields


class GoogleSheetsService:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SPREADSHEET_ID = '1f2KzCB2B1nhMxwsB3LJRXWHfjeXAaNnQnwF9W_bXX2Q'

    def __init__(self, credentials_dict):
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=self.SCOPES
        )
        self.service = build('sheets', 'v4', credentials=credentials)
        self.sheet = self.service.spreadsheets()

    def get_ingredients_data(self):
        result = self.sheet.values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range='Ingredients!A2:G'
        ).execute()

        rows = result.get('values', [])
        ingredients = []

        for row in rows:
            if not row or not row[1]:
                continue

            row = row + [''] * (7 - len(row))

            ingredients.append({
                DrinkLabFields.NAME_EN.value: row[0],
                DrinkLabFields.NAME_RU.value: row[1],
                DrinkLabFields.CATEGORY.value: row[2],
                DrinkLabFields.STRENGTH.value: row[3],
                DrinkLabFields.TASTE.value: row[4],
                DrinkLabFields.BASE.value: row[5],
                DrinkLabFields.DESCRIPTION.value: row[6]
            })

        return ingredients

    def get_drinks_data(self):
        result = self.sheet.values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range='Drinks!A2:I'
        ).execute()

        rows = result.get('values', [])
        drinks = []

        for row in rows:
            if not row or not row[1]:  # Skip empty rows
                continue

            # Pad row if it's shorter than expected
            row = row + [''] * (9 - len(row))

            drinks.append({
                DrinkLabFields.NAME_EN.value: row[0],
                DrinkLabFields.NAME_RU.value: row[1],
                DrinkLabFields.STRENGTH.value: row[2],
                DrinkLabFields.TASTE.value: row[3],
                DrinkLabFields.BASE.value: row[4],
                DrinkLabFields.GROUP.value: row[5],
                DrinkLabFields.METHOD.value: row[6],
                DrinkLabFields.INGREDIENTS.value: row[7],
                DrinkLabFields.GADGETS.value: row[8]
            })

        return drinks
