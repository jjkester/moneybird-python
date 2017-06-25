Authentication
==============

.. py:currentmodule:: moneybird.authentication

Two authentication methods are supported:

- Token authentication (via the :py:class:`TokenAuthentication` class)
- OAuth authentication (via the :py:class:`OAuthAuthentication` class)

Token authentication
--------------------

Token authentication is the simplest form of authentication. In the MoneyBird application a token can be generated,
which you can pass to your :py:class:`TokenAuthentication` instance.

Token authentication is useful when your application only accesses a single MoneyBird administration.
Token authentication is not recommended when you want to access multiple administrations, especially not when you
access administrations belonging to users of your application. Please use OAuth authentication instead in these
scenarios.

::

    from moneybird import TokenAuthentication

    auth = TokenAuthentication('my_moneybird_token')

.. warning::
    Never include your token in your source code since this token can be (mis)used to access your MoneyBird account!

I recommend to pass your token to your application using a local configuration file, or even better, an environment
variable.

OAuth authentication
--------------------

OAuth authentication can be used when your application accesses multiple administrations. Using OAuth, the user
authorizes your application using a secure process. OAuth requires interaction with the user to work.

This documentation assumes that the reader has a sufficient knowledge of the OAuth technology and the processes related
to it.

Details about the MoneyBird OAuth implementation can be found `here <http://developer.moneybird.com/authentication/>`_.

Prerequisites
~~~~~~~~~~~~~

For OAuth authentication your application has to be registered in MoneyBird. MoneyBird will provide you with a `client
id` and a `client secret`. Both these values are required by the OAuth authentication implementation.

.. warning::
    Never include your client id and/or client secret in your source code!

The OAuth authentication can be set up as follows::

    from moneybird import OAuthAuthentication

    auth = OAuthAuthentication(
        redirect_url='https://yoursite.example.com/oauth/callback/',
        client_id='your_client_id',
        client_secret='your_client_secret',
    )

Requesting authorization
~~~~~~~~~~~~~~~~~~~~~~~~

Before you can do any API calls, an access token needs to be obtained. This can be done by redirecting the user to the
authorize url. This url can be obtained using :py:func:`OAuthAuthentication.authorize_url`.

The response from MoneyBird can be processed and exchanged for an access token using
:py:func:`OAuthAuthentication.obtain_token`.

Authenticating a user
~~~~~~~~~~~~~~~~~~~~~

When an access token has been obtained this token can be used to perform API calls. The :py:class:`OAuthAuthentication`
instance can be (re)used, or the obtained token can be used with a new :py:class:`TokenAuthentication` instance.

.. code-block:: python

    from moneybird import MoneyBird, OAuthAuthentication

    auth = OAuthAuthentication(
        redirect_url='https://yoursite.example.com/oauth/callback/',
        client_id='your_client_id',
        client_secret='your_client_secret',
    )
    auth.obtain_token('https://yoursite.example.com/oauth/callback/?code=any&state=random_string', 'random_string')

    moneybird = MoneyBird(auth)

.. code-block:: python

    from moneybird import MoneyBird, OAuthAuthentication

    auth = OAuthAuthentication(
        redirect_url='https://yoursite.example.com/oauth/callback/',
        client_id='your_client_id',
        client_secret='your_client_secret',
    )
    access_token = auth.obtain_token('https://yoursite.example.com/oauth/callback/?code=any&state=random_string', 'random_string')

    moneybird = MoneyBird(TokenAuthentication(access_token))

The access token can be stored for later use. At the moment of writing MoneyBird access tokens do not expire. However,
a user might remove the authorization for the token, making the API inaccessible using the token.

For convenience, :py:func:`OAuthAuthentication.__init__` also acceps an ``auth_token`` parameter. This enables you
to always use an :py:class:`OAuthAuthentication` instance regardless of whether you already have a token or not.

Internal API
------------

.. automodule:: moneybird.authentication
    :members:
    :show-inheritance:
