from utils.auth import AuthManager
from dotenv import load_dotenv
from os import getenv

load_dotenv()
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')
MAL_USERNAME = getenv('MAL_USERNAME')
MAL_PASSWORD = getenv('MAL_PASSWORD')


if __name__ == '__main__':
    auth = AuthManager.init_with_credentials(client_id=CLIENT_ID,
                                             client_secret=CLIENT_SECRET,
                                             mal_username=MAL_USERNAME,
                                             mal_password=MAL_PASSWORD)
    auth.save_tokens(fp='../tokens.json')
