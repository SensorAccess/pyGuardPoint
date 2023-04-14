pyGuardPoint
===============

pyGuardPoint providers pythonic programming interface to the WebAPI of GuardPoint 10 (GP10).
At the time of writing the current version of GuardPoint 10 is Version 1.90.3.
GuardPoint 10 is an Access Control System(ACS) - Learn more about GuardPoint 10 here https://www.sensoraccess.co.uk/guardpoint10/
GuardPoint 10 controls and monitors doors,lifts,readers etc. PyGuardPoint currently focuses more on the management of Cardholders over monitoring and setup of the physical infrastructure.
pyGuardPoint is not compatible with the legacy ACS GuardPoint Pro.

What is it good for?
------------------
Rapid development of applications and scripts using the GuardPoint ACS.
pyGuardPoint manages your authenticated connection to GuardPoint-10, so there is know need to construct complex OData URLs.
The Python object Cardholder represent a user/person on the system.
Modify your Cardholder's attributes and update them with just a couple of lines of code.

Examples
------------------

For example, to retrieve a list of cardholders:

    gp = GuardPoint(host="10.0.0.1", pwd="password")
    cardholders = gp.get_card_holders(search_terms="Jeff Buckley")
    for cardholder in cardholders:

To create a new cardholder:

    gp = GuardPoint(host="10.0.0.1", pwd="password")
    cardholder_pd = CardholderPersonalDetail(email="jeff.buckley@test.com")
    cardholder = Cardholder(firstName="Jeff", lastName="Buckley",
                            cardholderPersonalDetail=cardholder_pd)
    cardholder = gp.new_card_holder(cardholder)

To create a card for the cardholder - A card can represent an assortment of Identity tokens(magnetic-card, smartcard, QRCode , vehicle number plate etc) - as long as it contains a unique card-code:

    from pyGuardPoint import GuardPoint, Card

    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    cardholders = gp.get_card_holders(firstName="Jeff", lastName="Buckley")
    if len(cardholders) < 1:
        exit()

    card = Card(cardType="Magnetic", cardCode="1A1B1123")
    cardholders[0].cards.append(card)
    if gp.update_card_holder(cardholders[0]):
        updated_cardholder = gp.get_card_holder(uid=cardholders[0].uid)
        print(f"Cardholder {updated_cardholder.firstName} {updated_cardholder.lastName} Updated")
        print(f"\tEmail: {updated_cardholder.cardholderPersonalDetail.email}")
        print(f"\tCards: {updated_cardholder.cards}")

The get_cardholders method can be used with a whole host of flags for filtering:

    cardholders = gp.get_card_holders(search_terms="Frank Smith Countermac",
                                          cardholder_type_name='Visitor',
                                          filter_expired=True,
                                          select_ignore_list=['cardholderCustomizedField',
                                                              'cardholderPersonalDetail',
                                                              'securityGroup',
                                                              'cards',
                                                              'photo'],
                                          select_include_list=['uid', 'lastName', 'firstName', 'lastPassDate',
                                                               'insideArea', 'fromDateTime'],
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          threshold=10)

The class Cardholder has a couple of convenience functions:

    cardholder.dict(non_empty_only=True)) # Convert to python dictionary
    cardholder.pretty_print()   # Print nicely in the terminal window

To get a list of areas/zones, and count the number of cardholders in each:

    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    areas = gp.get_areas()

    areas = gp.get_areas()
    for area in areas:
        cardholder_count = gp.get_card_holders(count=True, areas=area)
        print(f"Cardholders in {area.name} = {str(cardholder_count)}")

To get a list of security groups:

    sec_groups = gp.get_security_groups()
    for sec_group in sec_groups:
        print(sec_group)

Scheduling the membership of an Access Group to a Cardholder:

    # Get a cardholder
    cardholder = gp.get_card_holder(card_code='1B1A1B1C')

    # Add and associate schedule access group to cardholder
    fromDateValid = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    toDateValid = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    sm = ScheduledMag(scheduledSecurityGroupUID=sec_groups[0].uid,
                      cardholderUID=cardholder.uid,
                      fromDateValid=fromDateValid,
                      toDateValid=toDateValid)
    gp.add_scheduled_mag(sm)

    scheduled_mags = gp.get_scheduled_mags()
    for scheduled_mag in scheduled_mags:
        print(scheduled_mag)

More
------------------

The code and further examples can be found at https://github.com/SensorAccess/pyGuardPoint