Accessing the API
=================

.. py:currentmodule:: moneybird.api

The :py:class:`MoneyBird` class provides a low level of abstraction for communicating with the MoneyBird API. This means
that the library only provides ways to minimize repetitive work, but does not contain an internal data representation
of the MoneyBird data.

API docs
--------

Knowledge of the `MoneyBird API <http://developer.moneybird.com/>`_ is expected and required for working with this
library. API documentation can be fount at http://developer.moneybird.com/.

Set up
------

Before querying the API, it has to be set up properly. Every instance of the API requires a valid form of
authentication:

.. code-block:: python

    from moneybird import MoneyBird, TokenAuthentication

    moneybird = MoneyBird(TokenAuthentication('token'))

See :doc:`authentication` for details on authentication.

Queries
-------

For queries, there are four methods, one for each type of HTTP request:

- Get: :py:func:`MoneyBird.get`
- Post: :py:func:`MoneyBird.post`
- Patch: :py:func:`MoneyBird.patch`
- Delete: :py:func:`MoneyBird.delete`

Method signatures
~~~~~~~~~~~~~~~~~

The method signatures of these methods are pretty similar.

For all methods, the first argument is the resource url, as given by the MoneyBird API documentation, excluding the
domain, version, format, etc. So for the list of contacts this will be ``contacts``, for a specific contact this will be
``contacts/%(id)s``.

For the post and patch methods, which send data, the second argument is the data that is to be sent. The data should be
regular Python objects ready for JSON serializing. Dictionaries and lists are commonly used. The data should be
formatted according to the appropriate format for the resource.

The last argument, with the keyword ``administration_id``, should contain the administration id when this is required
for the used resource.

The methods always return the response from the API or throw an exception. The response will be a Python object built
from the JSON response.

The methods are described in detail below.

Example
~~~~~~~

.. code-block:: python

    from moneybird import MoneyBird, TokenAuthentication

    # API client
    moneybird = MoneyBird(TokenAuthentication('token'))

    # Get an administration id
    administrations = moneybird.get('administrations')

    # Get all contacts for all administrations
    for administration in administrations:
        id = administration['id']
        contacts = moneybird.get('contacts', administration_id=id)

        # Print invoices per contact
        for contact in contacts:
            print(contact['company_name'])

            for invoice in moneybird.get('sales_invoices?filter=contact_id:%s' % contact['id'], administration_id=id)
                print('  ', invoice['invoice_id'])

Internal API
------------

.. automodule:: moneybird.api
    :members:
    :show-inheritance:
