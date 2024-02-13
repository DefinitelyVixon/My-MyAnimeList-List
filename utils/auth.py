import requests
import pkce
import secrets
import json
from time import sleep
from os import getenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from dataclasses import dataclass
from .exceptions import *


@dataclass
class AuthManager:
    client_id: str = None
    client_secret: str = None
    mal_username: str = None
    mal_password: str = None
    redirect_uri: str = None
    access_token: str = None
    refresh_token: str = None

    @staticmethod
    def init_with_credentials(client_id, client_secret, mal_username, mal_password, redirect_uri=None):
        """
        Initialize an authenticator with MyAnimeList API and user credentials.
        The application needs to be published on https://myanimelist.net/apiconfig and have a client_secret.

        Parameters
        ----------
        client_id : str
            Client ID of the app.
        client_secret : str
            Client secret of the app.
        mal_username : str
            MyAnimeList username of the app owner.
        mal_password : str
            MyAnimeList password of the app owner.
        redirect_uri : str
            (optional) Redirect uri to be used in client authentication. Not using this parameter is highly advised.

        Returns
        -------
        authenticator : AuthManager
            Authenticator object
        """
        auth = AuthManager()

        auth.client_id = client_id or getenv('CLIENT_ID')
        if auth.client_id is None:
            raise MissingConfigurationException('client_id')

        auth.client_secret = client_secret or getenv('CLIENT_SECRET')
        if auth.client_secret is None:
            raise MissingConfigurationException('client_secret')

        auth.mal_username = mal_username or getenv('MAL_USERNAME')
        if auth.mal_username is None:
            raise MissingConfigurationException('mal_username')

        auth.mal_password = mal_password or getenv('MAL_PASSWORD')
        if auth.mal_password is None:
            raise MissingConfigurationException('mal_password')

        auth.redirect_uri = redirect_uri
        if auth.redirect_uri is None:
            MissingRedirectUriWarning()

        auth.access_token, auth.refresh_token = auth.request_oauth_2(response_type='code',
                                                                     code_challenge_method='plain')
        return auth

    @staticmethod
    def init_with_tokens(fp):
        """
        Initialize a partial-authenticator object that holds "access_token" and "refresh_token" from a JSON file.

        Parameters
        ----------
        fp : str
            File path to json file that holds the 'access_token' and 'refresh_token' values.

        Returns
        -------
        authenticator : AuthManager
            Authenticator object that holds the access and refresh tokens.
        """
        auth = AuthManager()
        auth.access_token, auth.refresh_token = AuthManager.fetch_tokens(fp=fp)
        return auth

    def request_oauth_2(self, response_type, code_challenge_method):
        code_verifier, code_challenge = pkce.generate_pkce_pair()

        state = secrets.token_urlsafe(32)

        driver = webdriver.Chrome()
        auth_code = self.get_auth_code(driver=driver,
                                       response_type=response_type,
                                       state=state,
                                       code_challenge=code_challenge,
                                       code_challenge_method=code_challenge_method)
        driver.quit()

        # Using code_verifier=code_verifier raises an error
        access_token, refresh_token = self.generate_user_tokens(grant_type='authorization_code',
                                                                code=auth_code,
                                                                code_verifier=code_challenge)
        return access_token, refresh_token

    def get_auth_code(self, driver: webdriver.Chrome, response_type, state, code_challenge, code_challenge_method):
        params = {
            'response_type': response_type,
            'client_id': self.client_id,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': code_challenge_method
        }

        if self.redirect_uri is not None:
            params['redirect_uri'] = self.redirect_uri

        url = 'https://myanimelist.net/v1/oauth2/authorize' + AuthManager.query_params_to_str(params)
        driver.get(url)

        if driver.current_url == 'https://myanimelist.net/login.php?from=%2Fdialog%2Fauthorization&':
            driver.find_element(By.ID, 'loginUserName').send_keys(self.mal_username)
            driver.find_element(By.ID, 'login-password').send_keys(self.mal_password)
            driver.find_elements(By.CLASS_NAME, 'button--primary')[0].click()
            sleep(1)

        driver.find_elements(By.CLASS_NAME, 'button--primary')[0].click()
        sleep(1)

        code, check_state = tuple(map(lambda k: k.split('=')[-1], driver.current_url.split('?')[-1].split('&')))

        if check_state != state:
            raise Exception('Client and server states do not match.')

        return code

    # Step 2
    def generate_user_tokens(self, grant_type, code, code_verifier):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': grant_type,
            'code': code,
            'code_verifier': code_verifier
        }
        if self.redirect_uri is not None:
            params['redirect_uri'] = self.redirect_uri

        return AuthManager.post_user_tokens(params=params)

    def save_tokens(self, fp='tokens.json'):
        with open(fp, mode='w', encoding='utf8') as out_file:
            json.dump({'access_token': self.access_token, 'refresh_token': self.refresh_token}, out_file)
            print('Saved user tokens to', out_file.name)

    def refresh_user_tokens(self):
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        return AuthManager.post_user_tokens(params=params)

    @staticmethod
    def post_user_tokens(params):
        url = 'https://myanimelist.net/v1/oauth2/token'
        response = requests.post(url, params).json()

        return response['access_token'], response['refresh_token']

    @staticmethod
    def fetch_tokens(fp):
        try:
            with open(fp, mode='r', encoding='utf8') as in_file:
                tokens = json.load(in_file)
                return tokens['access_token'], tokens['refresh_token']
        except FileNotFoundError:
            raise MissingTokensException()

    @staticmethod
    def query_params_to_str(param_dict):
        return '?' + '&'.join(f'{k}={v}' for k, v in param_dict.items())
