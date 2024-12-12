import os
import shutil
import time
from uuid import uuid4
from flask import session


class UserStorage:
    def __init__(self, base_path):
        self.base_path = base_path

    def get_user_folder(self):
        """Get or create user-specific folder using session ID"""
        if 'user_folder' not in session:
            session['user_folder'] = str(uuid4())

        user_folder = os.path.join(self.base_path, session['user_folder'])
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        return user_folder

    def cleanup_old_folders(self, max_age_hours=24):
        """Cleanup folders older than max_age_hours"""
        current_time = time.time()
        for folder in os.listdir(self.base_path):
            folder_path = os.path.join(self.base_path, folder)
            if os.path.isdir(folder_path):
                folder_age = current_time - os.path.getctime(folder_path)
                if folder_age > max_age_hours * 3600:
                    shutil.rmtree(folder_path)
