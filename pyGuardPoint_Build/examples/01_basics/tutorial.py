from pyGuardPoint import GuardPointError, Cardholder, GuardPointAsync

gp = GuardPointAsync(host="sensoraccess.duckdns.org", pwd="password")


def task_complete(response):
    if isinstance(response, GuardPointError):
        print(f"Got back a GuardPointError: {response}")
    if isinstance(response, Cardholder):
        cardholder = response
        print("Cardholder:")
        print("\tUID: " + cardholder.uid)
        print("\tFirstname: " + cardholder.firstName)
        print("\tLastname: " + cardholder.lastName)


gp.get_card_holder(task_complete, card_code="1B1A1B1C")

'''
cardholder = gp.get_card_holder(card_code='1B1A1B1C')

print("Cardholder:")
print("\tUID: " + cardholder.uid)
print(f"\tFirstname: {cardholder.firstName if hasattr(cardholder, 'firstName') else ' '}")
print("\tLastname: " + cardholder.lastName)
print("\tCardholder Type: " + cardholder.cardholderType.typeName)
print("\tNum of Cards: " + str(len(cardholder.cards)))
print("\tOwnerSiteUID:" + cardholder.ownerSiteUID)

cardholders = gp.get_card_holders(search_terms="Frida")
print("Got back a: " + str(type(cardholders)) + " containing: " + str(len(cardholders)) + " entries.")
for cardholder in cardholders:
    print("Cardholder: ")
    print("\tUID: " + cardholder.uid)
    print("\tFirstname: " + cardholder.firstName)
    print("\tLastname: " + cardholder.lastName)

'''

'''cardholder = gp.get_card_holder(card_code='1B1A1B1C')

        print("Cardholder:")
        print("\tUID: " + cardholder.uid)
        print(f"\tFirstname: {cardholder.firstName if hasattr(cardholder, 'firstName') else ' '}")
        print("\tLastname: " + cardholder.lastName)
        print("\tCardholder Type: " + cardholder.cardholderType.typeName)
        print("\tNum of Cards: " + str(len(cardholder.cards)))
        print("\tOwnerSiteUID:" + cardholder.ownerSiteUID)'''
