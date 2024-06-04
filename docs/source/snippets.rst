Snippets
========

Searching for Cardholders
-------------------------
The code extract below shows and to find Cardholders with certain search terms.
You can set the filed threshold to a value of 0-100, higher indicates a closer match.

>>> cardholders = gp.get_card_holders(search_terms="Phil Sensor",
>>>                                           cardholder_type_name='Visitor',
>>>                                           filter_expired=False,
>>>                                           select_ignore_list=['cardholderCustomizedField',
>>>                                                               'cardholderPersonalDetail',
>>>                                                               'securityGroup',
>>>                                                               'photo'],
>>>                                           select_include_list=['uid', 'lastName', 'firstName', 'lastPassDate',
>>>                                                                'insideArea', 'fromDateTime', 'cards'],
>>>                                           sort_algorithm=SortAlgorithm.FUZZY_MATCH,
>>>                                           threshold=90
>>>                                           )
>>> for cardholder in cardholders:
>>>     print("Cardholder:")
>>>     print(f"\t{cardholder.lastName}")
>>>     cardholder.pretty_print()

The snippet below shows how to find cardholders by their email.
It also has a added filter to ignore the fields: 'cardholderCustomizedField', 'ownerSiteUID', 'photo'

>>> personalDetails = CardholderPersonalDetail(email="john.owen@countermac.com")
>>> cardholders = gp.get_card_holders(cardholderPersonalDetail=personalDetails,
>>>                                   select_ignore_list=['cardholderCustomizedField', 'ownerSiteUID', 'photo']
>>>                                  )
>>> for cardholder in cardholders:
>>>     print("Cardholder:")
>>>     print(f"\t{cardholder.lastName}")
>>>     print(f"\t{cardholder.cardholderPersonalDetail.email}")

Creating Cardholders
--------------------
The code below demonstrates how to create a Cardholder with a new Card and additional PersonalDetails and CustomFields:

>>> card = Card(cardType="Magnetic", cardCode="1A1B1C8B")
>>> cardholder_pd = CardholderPersonalDetail(email="john.owen@example.com")
>>> cardholder_cf = CardholderCustomizedField(cF_StringField_20="hello")
>>> cardholder = Cardholder(firstName="John", lastName="Owen9700",
>>>                                 cardholderPersonalDetail=cardholder_pd,
>>>                                 cardholderCustomizedField=cardholder_cf,
>>>                                 cards=[card])
>>> cardholder = gp.new_card_holder(cardholder)
>>> print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Created")