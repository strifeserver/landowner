from models.user import User
from app_requests.UsersRequest import UsersRequest
from services.UsersService import UsersService
from utils.debug import print_r
import bcrypt

class UsersController:
    
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=5, page=1, searchAll=None):
        
        service = UsersService()

        indexData = service.index(
            filters=filters or {},
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=searchAll
        )
        
        return indexData

    @staticmethod
    def create():
        from models.user import User
        from views.users.user_form import UserForm
        
        # Still generate auto-ID to pass to custom form
        next_id = User.get_next_custom_id()

        return {
            "view_type": "custom",
            "view_class": UserForm,
            "initial_data": {"customId": next_id}
        }

    @staticmethod
    def store(data):
        request = UsersRequest(data, action="store")
        # Ensure we validate incoming data from custom form correctly
        validation = request.validate()

        if validation is not True:
            return {"success": False, "errors": validation}

        # Hash password before storing
        validated_data = request.get_validated_data()
        if 'password' in validated_data and validated_data['password']:
            hashed = bcrypt.hashpw(validated_data['password'].encode('utf-8'), bcrypt.gensalt())
            validated_data['password'] = hashed.decode('utf-8')

        service = UsersService()        
        result = service.store(validated_data)
        return {"success": True, "message": "User created successfully"} if result else {"success": False, "message": "Failed to create user"}

    @staticmethod
    def edit(data):
        from views.users.user_form import UserForm
        # 'data' here is the User object passed from the table selection
        return {
            "view_type": "custom",
            "view_class": UserForm,
            "initial_data": data
        }

    @staticmethod
    def update(id, data):
        request = UsersRequest(data, action='update')
        validation = request.validate()

        if validation is not True:
            return {"success": False, "errors": validation}

        service = UsersService()   
        print("Users Controller Update")
        result = service.update(id, request.get_validated_data())
        return {"success": True, "message": "User updated successfully"} if result else {"success": False, "message": "Failed to update user"}

    @staticmethod
    def destroy(id):
        service = UsersService()   
        print("Users Controller Delete")
        result = service.delete(id)
        return {"success": True, "message": "User deleted successfully"} if result else {"success": False, "message": "Failed to delete user"}
