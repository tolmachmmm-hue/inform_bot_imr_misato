import os
import json
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(BASE_DIR, "values", "DataGoogleSheets.json")

class DataManager:

    DATA_FILE = DATA_FILE_PATH

    @staticmethod
    def load_data():
        try:
            with open(DataManager.DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as e:
            print(f"File not found: {DataManager.DATA_FILE}")
            raise e

    @staticmethod
    def save_data(data):
        os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
        try:
            with open(DATA_FILE_PATH, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Failed to save data: {e}")
            traceback.print_exc()

    @staticmethod
    def update_data(new_data):
        with open(DataManager.DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)