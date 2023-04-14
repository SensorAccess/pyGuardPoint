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
