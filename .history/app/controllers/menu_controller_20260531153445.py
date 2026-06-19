from app.repositories.menu_repository import MenuRepository

class MenuController:
    def __init__(self, db):
        self.menu_repo = MenuRepository(db)
    
    async def get_all_menu(self):
        return await self.menu_repo.find_all()
    
    async def get_available_menu(self):
        return await self.menu_repo.find_available()
    
    async def get_menu_by_id(self, menu_id: str):
        return await self.menu_repo.find_by_menu_id(menu_id)
    
    async def create_menu(self, menu_data: dict):
        return await self.menu_repo.create(menu_data)