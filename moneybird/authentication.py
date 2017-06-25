import logging
import uuid
from urllib.parse import urljoin, urlencode, parse_qs

import requests

logger = logging.getLogger('moneybird')


class Authentication(object):
    """
    Base class for authentication implementations.
    """
    def is_ready(self) -> bool:
        """
        Checks whether authentication can be performed. A negative result means that it is certain that a request will
        not authenticate.

        :return: Whether the authentication is ready to be used.
        """
        raise NotImplementedError()

    def get_session(self) -> requests.Session:
        """
        Creates a new session with the authentication settings applied.

        :return: The new session.
        """
        raise NotImplementedError()


class TokenAuthentication(Authentication):
    """
    Token authentication for the MoneyBird API.

    :param auth_token: The authentication token to use.
    """
    def __init__(self, auth_token: str = ''):
        self.auth_token = auth_token

    def set_token(self, auth_token: str):
        """
        Sets the authentication token.

        :param auth_token: The authentication token to use.
        """
        self.auth_token = auth_token

    def is_ready(self) -> bool:
        return bool(self.auth_token)

    def get_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'Authorization': 'Bearer %s' % self.auth_token,
        })
        return session


class OAuthAuthentication(Authentication):
    """
    OAuth authentication for the MoneyBird API.

    This is a wrapper around TokenAuthentication since token authentication is used after the OAuth process has been
    performed. This authentication method cannot be used directly, some work is required since the user has to perform
    a number of actions before a token can be obtained.

    :param redirect_url: The URL to redirect to after successful authorization.
    :param client_id: The OAuth client id obtained from MoneyBird.
    :param client_secret: The OAuth client secret obtained from MoneyBird.
    :param auth_token: The optional token from an earlier authorization.
    """
    base_url = 'https://moneybird.com/oauth/'
    auth_url = 'authorize/'
    token_url = 'token/'

    def __init__(self, redirect_url: str, client_id: str, client_secret: str, auth_token: str = ''):
        self.redirect_url = redirect_url
        self.client_id = client_id
        self.client_secret = client_secret

        self.real_auth = TokenAuthentication(auth_token)

    def authorize_url(self, scope: list, state: str = None) -> tuple:
        """
        Returns the URL to which the user can be redirected to authorize your application to access his/her account. It
        will also return the state which can be used for CSRF protection. A state is generated if not passed to this
        method.

        Example:
            >>> auth = OAuthAuthentication('https://example.com/oauth/moneybird/', 'your_id', 'your_secret')
            >>> auth.authorize_url()
            ('https://moneybird.com/oauth/authorize?client_id=your_id&redirect_uri=https%3A%2F%2Fexample.com%2Flogin%2F
            moneybird&state=random_string', 'random_string')

        :param scope: The requested scope.
        :param state: Optional state, when omitted a random value is generated.
        :return: 2-tuple containing the URL to redirect the user to and the randomly generated state.
        """
        url = urljoin(self.base_url, self.auth_url)
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_url,
            'scope': ' '.join(scope),
            'state': state if state is not None else self._generate_state(),
        }

        return "%s?%s" % (url, urlencode(params)), params['state']

    def obtain_token(self, redirect_url: str, state: str) -> str:
        """
        Exchange the code that was obtained using `authorize_url` for an authorization token. The code is extracted
        from the URL that redirected the user back to your site.

        Example:
            >>> auth = OAuthAuthentication('https://example.com/oauth/moneybird/', 'your_id', 'your_secret')
            >>> auth.obtain_token('https://example.com/oauth/moneybird/?code=any&state=random_string', 'random_string')
            'token_for_auth'
            >>> auth.is_ready()
            True

        :param redirect_url: The full URL the user was redirected to.
        :param state: The state used in the authorize url.
        :return: The authorization token.
        """
        url_data = parse_qs(redirect_url.split('?', 1)[1])

        if 'error' in url_data:
            logger.warning("Error received in OAuth authentication response: %s" % url_data.get('error'))
            raise OAuthAuthentication.OAuthError(url_data['error'], url_data.get('error_description', None))

        if 'code' not in url_data:
            logger.error("The provided URL is not a valid OAuth authentication response: no code")
            raise ValueError("The provided URL is not a valid OAuth authentication response: no code")

        if state and [state] != url_data['state']:
            logger.warning("OAuth CSRF attack detected: the state in the provided URL does not equal the given state")
            raise ValueError("CSRF attack detected: the state in the provided URL does not equal the given state")

        try:
            response = requests.post(
                url=urljoin(self.base_url, self.token_url),
                data={
                    'grant_type': 'authorization_code',
                    'code': url_data['code'][0],
                    'redirect_uri': self.redirect_url,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                },
            ).json()
        except ValueError:
            logger.error("The OAuth server returned an invalid response when obtaining a token: JSON error")
            raise ValueError("The OAuth server returned an invalid response when obtaining a token: JSON error")

        if 'error' in response:
            logger.warning("Error while obtaining OAuth authorization token: %s" % response['error'])
            raise OAuthAuthentication.OAuthError(response['error'], response.get('error', ''))

        if 'access_token' not in response:
            logger.error("The OAuth server returned an invalid response when obtaining a token: no access token")
            raise ValueError("The remote server returned an invalid response when obtaining a token: no access token")

        self.real_auth.set_token(response['access_token'])
        logger.debug("Obtained authentication token for state %s: %s" % (state, self.real_auth.auth_token))

        return response['access_token']

    def is_ready(self) -> bool:
        return self.real_auth.is_ready()

    def get_session(self) -> requests.Session:
        return self.real_auth.get_session()

    @staticmethod
    def _generate_state() -> str:
        """
        Generates a new random string to be used as OAuth state.
        :return: A randomly generated OAuth state.
        """
        state = str(uuid.uuid4()).replace('-', '')
        logger.debug("Generated OAuth state: %s" % state)
        return state

    class OAuthError(Exception):
        """
        Exception for OAuth protocol errors.
        """
        def __init__(self, error_code: str, description: str = None):
            if not error_code:
                error_code = 'unknown'
            if not description:
                description = "Unknown reason"

            self.error_code = error_code

            msg = "OAuth error (%s): %s" % (error_code, description)

            super(OAuthAuthentication.OAuthError, self).__init__(msg)
