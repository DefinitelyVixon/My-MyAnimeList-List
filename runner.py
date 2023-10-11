from utils.mal import MyAnimeListManager
from utils.auth import AuthManager
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()
    auth_manager = AuthManager()
    mal_user = MyAnimeListManager(authenticator=auth_manager)
