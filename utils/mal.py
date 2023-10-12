import requests
from .auth import AuthManager
from .exceptions import *
from .static import Static


class MyAnimeListAPIHandler:
    def __init__(self, authenticator: AuthManager):
        """
        Create an API handler object with an AuthManager object.

        Parameters
        ----------
        authenticator : AuthManager
            Authentication manager object which was created with client_id, client_secret, and MAL credentials.
        """

        if authenticator is None:
            raise MissingAuthenticatorException()

        self.authenticator = authenticator
        self.access_token = self.authenticator.access_token
        self.refresh_token = self.authenticator.refresh_token
        self.base_url = 'https://api.myanimelist.net/v2'

    def get_anime(self, q, fields=None, limit=10, offset=0):
        """
        Returns anime dictionaries with their name similar to "q".

        Parameters
        ----------
        q : str
            Name of the anime
        fields : list or str
            Extra information about the anime
        limit : int
            Number of results to return
        offset : int
            Index of the first result returned from all results

        Returns
        -------
        results : dict
            Dictionary of anime results
        """
        params = self._abstract_query_params(limit, offset, q=q, fields=fields)
        params['q'] = q
        return self._make_request(api_path='/anime', params=params)

    def get_user_anime_list(self, user_name, status=None, fields=None, sort='list_score', limit=10, offset=0):
        params = self._abstract_query_params(limit, offset, status=status, fields=fields, sort=sort)
        return self._make_request(api_path=f'/users/{user_name}/animelist', params=params)

    def get_suggested_anime(self, fields=None, limit=10, offset=0):
        params = self._abstract_query_params(limit, offset, fields=fields)
        return self._make_request(api_path='/anime/suggestions', params=params)

    def _abstract_query_params(self, limit, offset, **kwargs):
        params = {'limit': limit, 'offset': offset}

        sort = kwargs.get('sort', None)
        if sort is not None:
            if sort not in Static.QUERY_SORT_OPTIONS:
                raise InvalidSortOptionException(sort)
            params['sort'] = sort

        status = kwargs.get('status', None)
        if status is not None:
            if status not in Static.ANIME_LIST_STATUSES:
                raise InvalidAnimeStatusException(status)
            params['status'] = status

        fields = kwargs.get('fields', None)
        if fields is not None:
            if type(fields) == list:
                params['fields'] = ','.join(fields)
            else:
                params['fields'] = fields

        return params

    def _make_request(self, api_path, params):
        response = requests.get(self.base_url + api_path, params=params,
                                headers={'Authorization': 'Bearer ' + self.authenticator.access_token})
        return response.json()
