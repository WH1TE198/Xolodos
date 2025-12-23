from pages.home import HomeView
from pages.search import SearchView
from pages.settings import SettingsView
from pages.user import UserView
from pages.add_product import AddProductView
from pages.expiring import ExpiringView
from pages.recipes import RecipesView

class Router:
    def __init__(self, page):
        self.page = page
    def resolve(self, route: str):

        r = (route or "/").strip()

        if r in ("/", "/home"):
            return HomeView(self.page)
        elif r == "/search":
            return SearchView(self.page)
        elif r == "/settings":
            return SettingsView(self.page)
        elif r == "/user":
            return UserView(self.page)
        elif r == "/add":
            return AddProductView(self.page)
        elif r == "/expiring":
            return ExpiringView(self.page)
        elif r == "/recipes":
            return RecipesView(self.page)
        else:
            return HomeView(self.page)
