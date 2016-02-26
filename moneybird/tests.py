import os
from unittest import TestCase
from urllib.parse import unquote

from moneybird import TokenAuthentication, OAuthAuthentication, MoneyBird

TEST_TOKEN = os.getenv('MONEYBIRD_TEST_TOKEN')


class TokenAuthenticationTest(TestCase):
    """
    Tests the behaviour of the TokenAuthentication implementation.
    """
    def setUp(self):
        self.auth = TokenAuthentication()

    def test_initial_state(self):
        self.assertFalse(self.auth.is_ready(), "Initially the authentication backend should not be ready.")

    def test_set_token(self):
        self.auth.set_token('test_token')
        self.assertEqual(self.auth.auth_token, 'test_token', "The token was changed by the implementation.")
        self.assertTrue(self.auth.is_ready(), "The authentication backend should be ready when a token is set.")

    def test_session(self):
        self.auth.set_token('test_token')
        session = self.auth.get_session().headers
        self.assertEqual(
            session['Authorization'],
            'Bearer test_token',
            "The implementation did not generate a proper HTTP Authorization header from the token.",
        )


class OAuthAuthenticationTest(TestCase):
    """
    Tests the behaviour of the OAuthAuthentication implementation.
    """
    def setUp(self):
        self.auth = OAuthAuthentication(
            redirect_url='https://example.test/login/oauth/',
            client_id='test_client',
            client_secret='test_secret',
        )

    def test_initial_state(self):
        self.assertEqual(
            self.auth.real_auth.auth_token,
            '',
            "The auth token should be the empty string when not explicitly set.",
        )
        self.assertFalse(self.auth.is_ready(), "Initially the authentication backend should not be ready.")

    def test_authorize_url(self):
        url, state = self.auth.authorize_url(['one', 'two'], 'random_string')
        path, params = url.split('?', 1)
        param_dict = {item.split('=', 1)[0]: unquote(item.split('=', 1)[1]) for item in params.split('&')}

        self.assertEqual(state, 'random_string', "The given state was changed by the implementation.")
        self.assertEqual(path, 'https://moneybird.com/oauth/authorize/', "The OAuth URL is incorrect.")
        self.assertDictEqual(param_dict, {
            'response_type': 'code',
            'client_id': 'test_client',
            'redirect_uri': 'https://example.test/login/oauth/',
            'scope': 'one+two',
            'state': 'random_string',
        }, "The generated URL parameters for authorization are incorrect for the given input.")

    def test_generate_state(self):
        url, state = self.auth.authorize_url(['one', 'two', 'three'])
        self.assertGreater(len(state), 16, "The generated state string is too short.")

        states = []
        for i in range(10000):
            state = OAuthAuthentication._generate_state()
            self.assertGreater(len(state), 16, "The generated state string is too short.")
            self.assertNotIn(state, states, "The randomization of the state is not random enough (%d)." % i)
            states.append(state)


class APIConnectionTest(TestCase):
    """
    Tests whether a connection to the API can be made.
    """
    def setUp(self):
        self.auth = TokenAuthentication(TEST_TOKEN)
        self.api = MoneyBird(self.auth)

    def test_get_administrations(self):
        result = self.api.get('administrations')
        self.assertIsNotNone(result, "The result is empty.")
        self.assertGreaterEqual(len(result), 1, "The result does not contain any data.")

    def test_contacts_roundtrip(self):
        # Get administration ID
        adm_id = self.api.get('administrations')[0]['id']

        # Build a contact
        contact = {
            'company_name': 'MoneyBird API',
            'firstname': 'John',
            'lastname': 'Doe',
        }

        # Create the contact in the administration
        post_result = self.api.post('contacts', {'contact': contact}, administration_id=adm_id)

        self.assertEqual(post_result['company_name'], 'MoneyBird API', "The contact has not been created properly.")
        self.assertEqual(post_result['firstname'], 'John', "The contact has not been created properly.")
        self.assertEqual(post_result['lastname'], 'Doe', "The contact has not been created properly.")
        self.assertIsNotNone(post_result['id'], "The contact has not been created properly.")

        # Set the id of the contact for further use.
        contact_id = post_result['id']

        contact = {
            'firstname': 'No',
            'lastname': 'One',
        }

        # Update the contact in the administration
        patch_result = self.api.patch('contacts/%s' % contact_id, {'contact': contact}, administration_id=adm_id)

        self.assertEqual(patch_result['company_name'], 'MoneyBird API', "The contact has not been updated properly.")
        self.assertEqual(patch_result['firstname'], 'No', "The contact has not been updated properly.")
        self.assertEqual(patch_result['lastname'], 'One', "The contact has not been updated properly.")

        # Delete the contact from the administration
        delete_result = self.api.delete('contacts/%s' % contact_id, administration_id=adm_id)

        self.assertEqual(delete_result['id'], contact_id, "The contact has not been deleted properly.")

        # Check deletion
        try:
            self.api.get('contacts/%s' % contact_id, administration_id=adm_id)
        except self.api.NotFound:
            pass
        else:
            self.fail("The contact has not been deleted properly.")
