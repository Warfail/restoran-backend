from app.repositories.menu_repository import MenuRepository
from app.utils import parse_json
from serializers import serialize_document, serialize_list, serialize_value

class MenuController:
    def __init__(self, db):
        self.menu_repo = MenuRepository(db)

    async def get_all_menu(self):
        menus = await self.menu_repo.find_all()
        return serialize_list(menus)

    async def get_available_menu(self):
        menus = await self.menu_repo.find_available()
        return serialize_list(menus)

    async def get_menu_by_id(self, menu_id: str):
        menu = await self.menu_repo.find_by_menu_id(menu_id)
        return serialize_document(menu)

    async def create_menu(self, menu_data: dict):
        return await self.menu_repo.create(menu_data)