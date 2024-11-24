# services/sync_service.py
class SyncService:
    def __init__(self, db_manager, file_manager):
        self.db_manager = db_manager
        self.file_manager = file_manager