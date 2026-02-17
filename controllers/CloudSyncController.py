# controllers/CloudSyncController.py
from utils.session import Session
from models.Merchants import Merchants

class CloudSyncController:
    @staticmethod
    def get_assigned_merchant():
        user = Session.get_user()
        if not user:
            return None
        
        user_id_str = str(user.id)
        all_merchants = Merchants.index()
        for m in all_merchants:
            if m.merchant_users:
                assigned_users = [u.strip() for u in str(m.merchant_users).split(',') if u.strip()]
                if user_id_str in assigned_users:
                    return m.__dict__
        return None

    @staticmethod
    def push(entities, sync_all=False):
        merchant = CloudSyncController.get_assigned_merchant()
        if not merchant:
            return {"success": False, "message": "No merchant assigned to your account."}
        
        if not merchant.get('merchant_service_json') or not merchant.get('merchant_sheet_id'):
            return {"success": False, "message": "Merchant Google Sheets settings are not configured."}
        
        from services.MerchantSyncService import MerchantSyncService
        service = MerchantSyncService(merchant)
        return service.push(entities, sync_all=sync_all)

    @staticmethod
    def pull(entities):
        merchant = CloudSyncController.get_assigned_merchant()
        if not merchant:
            return {"success": False, "message": "No merchant assigned to your account."}
            
        if not merchant.get('merchant_service_json') or not merchant.get('merchant_sheet_id'):
            return {"success": False, "message": "Merchant Google Sheets settings are not configured."}
        
        from services.MerchantSyncService import MerchantSyncService
        service = MerchantSyncService(merchant)
        return service.pull(entities)
