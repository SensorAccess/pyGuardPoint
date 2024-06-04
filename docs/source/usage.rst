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

Creating Cardholders
--------------------

For example:

>>> from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, CardholderCustomizedField
>>> gp = GuardPoint(host="http://sensoraccess.duckdns.org:10695", pwd="password")
>>> card = Card(cardType="Magnetic", cardCode="1A1B1C8B")
>>> cardholder_pd = CardholderPersonalDetail(email="john.owen@eml.cc")
>>> cardholder_cf = CardholderCustomizedField(cF_StringField_20="hello")
>>> cardholder = Cardholder(firstName="John", lastName="Owen9700",
                                cardholderPersonalDetail=cardholder_pd,
                                cardholderCustomizedField=cardholder_cf,
                                cards=[card])
>>> cardholder = gp.new_card_holder(cardholder)
>>> print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Created")

