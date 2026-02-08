# services/TableSettingsService.py
from services.BaseService import BaseService
from models.table_setting import TableSetting

class TableSettingsService(BaseService):
    def __init__(self):
        super().__init__(TableSetting)

    def get_by_table_name(self, table_name):
        return self.model.fetch_by_table_name(table_name)
