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

    def get_anime_dict(self, q, fields=None, limit=10, offset=0):
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
        params = MyAnimeListAPIHandler._abstract_query_params(limit, offset, q=q)
        params['q'] = q
        results = self._make_request(api_path='/anime', params=params)['data']

        if len(results) == 0:
            print(f'Cannot find anime with the given name "{q}".')
            return

        # return [AbstractAnimeObject(anim_dict) for anim_dict in results]
        return results

    def get_anime_details(self, anime_obj, fields=None, limit=1, offset=0):
        params = MyAnimeListAPIHandler._abstract_query_params(limit, offset, fields=fields)
        return self._make_request(api_path=f'/anime/{anime_obj.id}', params=params)

    def get_user_anime_list(self, user_name, status=None, fields=None, sort='list_score', limit=10, offset=0):
        params = MyAnimeListAPIHandler._abstract_query_params(limit, offset, status=status, fields=fields, sort=sort)
        return self._make_request(api_path=f'/users/{user_name}/animelist', params=params)

    def get_all_related_anime(self, anime_object, fields=None):
        all_related_anime_list = []
        closed_list = []
        open_list = [anime_object]

        while len(open_list) != 0:
            current_anime = RelatedAnimeObject(open_list.pop())
            if current_anime.id not in closed_list and current_anime.relation_type != 'character':
                anime_details = self.get_anime_details(current_anime, fields=fields)
                closed_list.append(anime_details['id'])
                open_list.extend(anime_details['related_anime'])
                all_related_anime_list.append(RelatedAnimeObject(anime_details))

        return all_related_anime_list

    def get_suggested_anime(self, fields=None, limit=10, offset=0):
        params = MyAnimeListAPIHandler._abstract_query_params(limit, offset, fields=fields)
        return self._make_request(api_path='/anime/suggestions', params=params)

    def _make_request(self, api_path, params):
        response = requests.get(self.base_url + api_path, params=params,
                                headers={'Authorization': 'Bearer ' + self.authenticator.access_token})
        return response.json()

    @staticmethod
    def _abstract_query_params(limit, offset, **kwargs):
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
            # TODO: raise exception for invalid fields
            params['fields'] = ','.join(fields)

        return params


class AbstractAnimeObject:
    id: int
    title: str
    main_picture: dict

    def __init__(self, kwarg_dict):
        if 'node' in kwarg_dict.keys():
            kwarg_dict = kwarg_dict['node']
        self.__dict__.update(kwarg_dict)

    def __str__(self):
        return f'AbstractAnimeObject({self.id}, "{self.title}")'

    def __repr__(self):
        return f'AbstractAnimeObject({self.id}, "{self.title}")'


class AnimeObject(AbstractAnimeObject):
    # region class variables
    list_status: object
    synopsis: object
    my_list_status: object
    alternative_titles: object
    start_date: object
    end_date: object
    mean: object
    rank: object
    popularity: object
    num_list_users: object
    num_scoring_users: object
    nsfw: object
    created_at: object
    updated_at: object
    status: object
    genres: object
    media_type: object
    num_episodes: object
    start_season: object
    broadcast: object
    source: object
    average_episode_duration: object
    rating: object
    pictures: object
    background: object
    related_anime: object
    related_manga: object
    recommendations: object
    studios: object
    statistics: object

    # endregion

    def __init__(self, kwarg_dict):
        super().__init__(kwarg_dict)
        if 'node' in kwarg_dict.keys():
            kwarg_dict = kwarg_dict['node']
        self.__dict__.update(kwarg_dict)


class RelatedAnimeObject(AnimeObject):
    relation_type: str

    def __init__(self, kwarg_dict):
        super().__init__(kwarg_dict)
        self.relation_type = kwarg_dict.get('relation_type', None)

    def __str__(self):
        return f'RelatedAnimeObject({self.id}, "{self.title}")'

    def __repr__(self):
        return f'RelatedAnimeObject({self.id}, "{self.title}")'
