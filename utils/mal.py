import requests

from .auth import AuthManager
from .exceptions import *
from .static import Static


class MyAnimeListManager:
    def __init__(self, tokens_fp: str = None, authenticator: AuthManager = None):
        """
        Create the manager instance with a token filepath or an authenticator.

        Parameters
        ----------
        tokens_fp : str
            File path to json file that holds the 'access_token' and 'refresh_token' values.
        authenticator : AuthManager
            Authentication manager object which was created with client_id, client_secret, and MAL credentials.
        """

        if authenticator is not None:
            # Assign the given authenticator to manager
            self.authenticator = authenticator
        elif tokens_fp is not None:
            # Fetch tokens that may have already created and saved
            self.authenticator = AuthManager(tokens_fp=tokens_fp)
        else:
            raise MissingTokensException()

        self.access_token = self.authenticator.access_token
        self.refresh_token = self.authenticator.refresh_token
        self.base_url = 'https://api.myanimelist.net/v2'

    def get_user_anime_list(self, user_name, status=None, fields=None, sort='list_score', limit=10, offset=0):

        if status not in Static.LIST_STATUSES:
            raise InvalidAnimeStatusException(status)

        if sort not in Static.ANIME_SORT_OPTIONS:
            raise InvalidSortOptionException(sort)

        params = {'sort': sort, 'limit': limit, 'offset': offset}

        if status is not None:
            params['status'] = status
        if fields is not None:
            if type(fields) == list:
                params['fields'] = ','.join(fields)
            else:
                params['fields'] = fields

        print(params)

        url = self.base_url + f'/users/{user_name}/animelist'
        response = requests.get(url, params=params,
                                headers={'Authorization': 'Bearer ' + self.authenticator.access_token})
        return response.json()

    def get_suggested_anime(self, fields=None, limit=10, offset=0):
        params = {'limit': limit, 'offset': offset}
        if fields is not None:
            params['fields'] = ','.join(fields)

        url = self.base_url + '/anime/suggestions'
        response = requests.get(url, params=params,
                                headers={'Authorization': 'Bearer ' + self.authenticator.access_token})
        return response.json()
