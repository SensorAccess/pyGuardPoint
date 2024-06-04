Usage
=====

.. _installation:

Installation
------------

To use Lumache, first install it using pip:

.. code-block:: console

   (.venv) $ pip install pyGuardPoint

Establishing a Server Connection
--------------------------------

To setup a connection to a GuardPoint Server.

Connection parameters are passed at initialisation:

>>> from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, CardholderCustomizedField
>>> gp = GuardPoint(host="http://sensoraccess.duckdns.org:10695", pwd="password")

It is recommended to use a secure connection with client certificates:

>>> GP_USER = 'admin'
>>> GP_PASS = 'admin'
>>> TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
>>> TLS_P12_PWD = "test"
>>>
>>> gp = GuardPoint(host=GP_HOST,
>>>                 username=GP_USER,
>>>                 pwd=GP_PASS,
>>>                 p12_file=TLS_P12,
>>>                 p12_pwd=TLS_P12_PWD)

A connection failure will cause one of the following Exceptions:

.. autoexception:: pyGuardPoint.GuardPointError
.. autoexception:: pyGuardPoint.GuardPointUnauthorized
.. exception:: Exception

Once successfully connected, your instance of GuardPoint will maintain a token used to authenticate subsequent API calls.

To view the token:

>>> jwt = gp.get_token()
>>> print(jwt)



