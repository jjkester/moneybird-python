from unittest import TestCase
from urllib.parse import unquote

from moneybird import TokenAuthentication, OAuthAuthentication


class TokenAuthenticationTest(TestCase):
    def setUp(self):
        self.auth = TokenAuthentication()

    def test_initial_state(self):
        self.assertFalse(self.auth.is_ready())

    def test_set_token(self):
        self.auth.set_token('test_token')
        self.assertEqual(self.auth.auth_token, 'test_token')
        self.assertTrue(self.auth.is_ready())

    def test_session(self):
        self.auth.set_token('test_token')
        session = self.auth.get_session().headers
        self.assertEqual(session['Authorization'], 'Bearer test_token')


class OAuthAuthenticationTest(TestCase):
    def setUp(self):
        self.auth = OAuthAuthentication(
            redirect_url='https://example.test/login/oauth/',
            client_id='test_client',
            client_secret='test_secret',
            auth_token='token',
        )

    def test_initial_state(self):
        self.assertEqual(self.auth.real_auth.auth_token, 'token')

    def test_authorize_url(self):
        url, state = self.auth.authorize_url(['one', 'two'], 'random_string')
        path, params = url.split('?', 1)
        param_dict = {item.split('=', 1)[0]: unquote(item.split('=', 1)[1]) for item in params.split('&')}

        self.assertEqual(state, 'random_string')
        self.assertEqual(path, 'https://moneybird.com/oauth/authorize/')
        self.assertDictEqual(param_dict, {
            'response_type': 'code',
            'client_id': 'test_client',
            'redirect_uri': 'https://example.test/login/oauth/',
            'scope': 'one+two',
            'state': 'random_string',
        })

    def test_generate_state(self):
        url, state = self.auth.authorize_url(['one', 'two', 'three'])
        self.assertGreater(len(state), 16)
        self.assertNotEqual(state, self.auth._generate_state())

        states = []
        for i in range(10000):
            state = OAuthAuthentication._generate_state()
            self.assertGreater(len(state), 16)
            self.assertNotIn(state, states)
            states.append(state)
