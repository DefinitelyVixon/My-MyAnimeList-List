import warnings
from .static import Static


# region Element Missing Exceptions
class MissingConfigurationException(Exception):
    def __init__(self, variable):
        super().__init__(f'"{variable}" is needed as a parameter or an environment variable.')


class MissingTokensException(Exception):
    def __init__(self):
        super().__init__('No generated tokens found. '
                         'Please create an AuthManager object and pass it as a parameter to MALUser object...')


# endregion

# region Invalid Element Exceptions
class InvalidAnimeStatusException(Exception):
    def __init__(self, variable):
        super().__init__(f'"{variable}" is not a valid anime status. '
                         f'Please provide an available status from: {Static.LIST_STATUSES}')


class InvalidQueryFieldException(Exception):
    def __init__(self, variable):
        super().__init__(f'"{variable}" s not a valid query field. '
                         f'Please provide an available field from: {Static.QUERY_FIELDS}')


class InvalidSortOptionException(Exception):
    def __init__(self, variable):
        super().__init__(f'"{variable}" s not a valid sort option. '
                         f'Please provide an available option from: {Static.ANIME_SORT_OPTIONS}')


# endregion

class MissingRedirectUriWarning:
    def __init__(self):
        warnings.warn(
            'You must provide a valid redirect uri as a parameter or from https://myanimelist.net/apiconfig',
            Warning)
