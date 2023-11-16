import logging, sys
import os
import tempfile
from pprint import pprint

import pkg_resources
# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

ca_data = '''
-----BEGIN CERTIFICATE-----
MIIELTCCAxWgAwIBAgIURU7qH0JVb8BlRd7S/LdrHi9fBEAwDQYJKoZIhvcNAQEL
BQAwgaUxCzAJBgNVBAYTAkdCMQ8wDQYDVQQIDAZTdXNzZXgxETAPBgNVBAcMCEJy
aWdodG9uMRowGAYDVQQKDBFTZW5zb3IgQWNjZXNzIEx0ZDEMMAoGA1UECwwDVk1T
MR8wHQYDVQQDDBZTZW5zb3IgQWNjZXNzIFZNUyBSb290MScwJQYJKoZIhvcNAQkB
FhhzYWxlc0BzZW5zb3JhY2Nlc3MuY28udWswHhcNMjIwNDIwMDk0NTQ5WhcNMzIw
NDE3MDk0NTQ5WjCBpTELMAkGA1UEBhMCR0IxDzANBgNVBAgMBlN1c3NleDERMA8G
A1UEBwwIQnJpZ2h0b24xGjAYBgNVBAoMEVNlbnNvciBBY2Nlc3MgTHRkMQwwCgYD
VQQLDANWTVMxHzAdBgNVBAMMFlNlbnNvciBBY2Nlc3MgVk1TIFJvb3QxJzAlBgkq
hkiG9w0BCQEWGHNhbGVzQHNlbnNvcmFjY2Vzcy5jby51azCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBAKQQYYHRdfuwrvlPQ6qfaijtND2VIpo1KhN5AFnG
U6q79Iu1BerKFlazdSL1TsPEWdmHIvBnpLkzuW7IF4gGRzgRDPSK0v4Wjhl6a1lD
g1qKTOX/Z4Kc9espFIrlbA6B4TrbQsbePMSyca+Ru+qHvO30qqqZUNGR5s7G8wVl
dIhzccUPWGm9C6TyjFfL8lwqBVjYcWDP/iAlDfw1tcPodL1qcEd3EKHkASL8D7iE
nFoLSEcW15VZ68cdCufRPfxCmL7FjddmiQ/itildV2szX5hWxlQik6GRArDrKpnE
Dqigx1vxyE5896fwHmu1z5jMK0kzx6pzgutDKqVpBxodUBUCAwEAAaNTMFEwHQYD
VR0OBBYEFB00pM6wNS3yIFERdLKviHr0l6o2MB8GA1UdIwQYMBaAFB00pM6wNS3y
IFERdLKviHr0l6o2MA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEB
ACMXKnIGKAR3teHMmsHyu9cwm+T25FWQShRoI+YRGSpVemnnmz6xpetDs6KDRVy4
nEMdq24QO03ME8Z7luCBu0VHaZCdteu4QBrd5obbDSbfkHYnPnhwBhG+FTQt6pc8
hGsHW92XNwnQiAXATKNI/kxeqzsXxoMpKgfbDTT8bnNMLIXL1JxZKpguXsxc6wOd
mx9B6Vfbh9UnNgtnxsQUu9dCO0Ukczfpq902xK0QiKjYslH5kiypBskuhWxcEY3y
+Z0K2OQmT3LfJ1s1GNj799EIlti4HX81GPMZsTi7sjHeff+lyOgj8ezAT+QtnxAP
1MNRXg3aviuwZbDS2Juguf8=
-----END CERTIFICATE-----'''

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    ca_file = tempfile.NamedTemporaryFile(delete=False)
    ca_file.write(ca_data.encode())
    ca_file.close()
    print(ca_file.name)
    gp = GuardPoint(host="https://sensoraccess.duckdns.org", pwd="admin",
                    p12_file="C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12",
                    p12_pwd="test")

    try:
        #cardholder = gp.get_card_holder(card_code='1B1A1B1C')
        #print("Cardholder:")
        #cardholder.pretty_print()
        #&$filter=(((insideAreaUID%20eq%205d6e8e1f-b8c1-44b1-8b39-019791c95d6c)%20or%20(insideAreaUID%20eq%2000000000-0000-0000-0000-100000000001)%20or%20(insideAreaUID%20eq%2000000000-0000-0000-0000-100000000002)%20or%20(insideAreaUID%20eq%2000000000-0000-0000-0000-100000000003)%20or%20(insideAreaUID%20eq%20e87df205-782f-4147-b929-203d41ad85c4)))
        # &$orderby=fromDateValid%20desc&$top=4&$skip=10
        cardholders = gp.get_card_holders(offset=0,
                                          limit=4,
                                          search_terms="Partridge",
                                          #cardholder_type_name="Visitor",
                                          #filter_expired=False
                                          #sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          #threshold=10,
                                          #select_include_list=['uid', 'firstName', 'lastName', 'photo',
                                          #                     'cardholderPersonalDetail', 'cardholderType',
                                          #                     'cardholderCustomizedField'],
                                          #select_ignore_list=['cardholderCustomizedField', 'ownerSiteUID',
                                           #                   'photo'])
                                          )
        if len(cardholders) > 0:
            print("Cardholder:")
            for cardholder in cardholders:
                print(cardholder.firstName + "" +  cardholder.lastName )#+ ":" + cardholder.uid)
            #cardholders[0].pretty_print()
            #pprint(cardholders[0].dict())

            #photo = gp.get_card_holder_photo(uid=cardholders[0].uid)
            #print(f"Photo:{photo}")
        else:
            print("No Cardholders Found")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        os.unlink(ca_file.name)
