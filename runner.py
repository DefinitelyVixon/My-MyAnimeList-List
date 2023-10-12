from utils.mal import MyAnimeListAPIHandler
from utils.auth import AuthManager
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()
    auth = AuthManager.init_with_tokens(fp='tokens.json')
    mal = MyAnimeListAPIHandler(authenticator=auth)
    mal.get_user_anime_list(user_name='Vixon',
                            status='completed',
                            fields='list_status',
                            limit=1,
                            sort='list_score')
