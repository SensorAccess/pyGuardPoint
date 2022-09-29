import logging
import validators as validators

from pyGuardPoint.dataclasses.cardholder import Cardholder
from pyGuardPoint.guardpoint_connection import GuardPointConnection, GuardPointAuthType

log = logging.getLogger(__name__)


class GuardPoint(GuardPointConnection):

    def __init__(self, **kwargs):
        # Set default values if not present
        host = kwargs.get('host', "localhost")
        port = kwargs.get('port', 10695)
        auth = kwargs.get('auth', GuardPointAuthType.BEARER_TOKEN)
        user = kwargs.get('username', "admin")
        pwd = kwargs.get('pwd', "admin")
        key = kwargs.get('key', "00000000-0000-0000-0000-000000000000")
        super().__init__(host=host, port=port, auth=auth, user=user, pwd=pwd, key=key)

    def get_card_holder(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = self.baseurl + "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?" \
                                       "$expand=" \
                                       "cardholderType($select=typeName)," \
                                       "cards($select=cardCode)," \
                                       "cardholderPersonalDetail($select=email,company,idType,idFreeText)," \
                                       "securityGroup($select=name)&" \
                                       "$select=uid," \
                                       "visitor_signature," \
                                       "host_signature," \
                                       "lastName," \
                                       "firstName," \
                                       "cardholderIdNumber," \
                                       "status," \
                                       "fromDateValid," \
                                       "isFromDateActive," \
                                       "toDateValid," \
                                       "isToDateActive," \
                                       "photo," \
                                       "cardholderType," \
                                       "cards," \
                                       "cardholderPersonalDetail," \
                                       "securityGroup"

        code, response_body = self.query("GET", url=(url + url_query_params))

        if code == 200:
            if len(response_body['value']) == 1:
                return Cardholder(response_body['value'][0])

        return response_body

    @staticmethod
    def _compose_filter(searchPhrase):
        filter_str = "$filter=(cardholderType/typeName%20eq%20'Visitor')"
        if searchPhrase:
            words = list(filter(None, searchPhrase.split(" ")))[
                    :5]  # Split by space, remove empty elements, ignore > 5 elements
            fields = ["firstName", "lastName", "CardholderPersonalDetail/company"]
            phrases = []
            for f in fields:
                for v in words:
                    phrases.append(f"contains({f},'{v}')")
            filter_str += f"%20and%20({'%20or%20'.join(phrases)})"
        filter_str += "&"
        return filter_str

    def get_card_holders(self, offset=0, limit=10, searchPhrase=None):
        url = self.baseurl + "/odata/API_Cardholders"
        filter_str = self._compose_filter(searchPhrase=searchPhrase)
        url_query_params = ("?" + filter_str +
                            "$expand="
                            "cardholderType($select=typeName),"
                            "cards($select=cardCode),"
                            "cardholderPersonalDetail($select=email,company,idType,idFreeText),"
                            "securityGroup($select=name)&"
                            "$select=uid,"
                            "lastName,"
                            "firstName,"
                            "cardholderIdNumber,"
                            "status,"
                            "fromDateValid,"
                            "isFromDateActive,"
                            "toDateValid,"
                            "isToDateActive,"
                            "photo,"
                            "cardholderType,"
                            "cards,"
                            "cardholderPersonalDetail,"
                            "securityGroup&"
                            "$orderby=fromDateValid%20desc&"
                            "$top=" + str(limit) + "&$skip=" + str(offset)
                            )

        code, response_body = self.query("GET", url=(url + url_query_params))

        if code == 200:
            cardholders = []
            for x in response_body['value']:
                cardholders.append(Cardholder(x))
            return cardholders

        return response_body


# conn = Connection()
# conn.query("GET", "/odata/$metadata")
# log.info("End")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")
    try:
        # Example getting a single cardholder
        cardholder = gp.get_card_holder("422edea0-589d-4224-af0d-77ed8a97ca57")
        print("Got back a: " + str(type(cardholder)))
        if isinstance(cardholder, Cardholder):
            print("Cardholder:")
            print("\tUID: " + cardholder.uid)
            print("\tFirstname: " + cardholder.firstName)
            print("\tLastname: " + cardholder.lastName)

        # Example getting a list of cardholders
        cardholders = gp.get_card_holders(limit=1, searchPhrase="john owen")
        print("Got back a: " + str(type(cardholders)) + " containing: " + str(len(cardholders)) + " entry.")
        if isinstance(cardholders, list):
            for cardholder in cardholders:
                print("Cardholder: ")
                print("\tUID: " + cardholder.uid)
                print("\tFirstname: " + cardholder.firstName)
                print("\tLastname: " + cardholder.lastName)

    except Exception as e:
        print(e)
