import json
import logging
from json import JSONDecodeError

import validators as validators

from pyGuardPoint.guardpoint_dataclasses import Cardholder
from pyGuardPoint.guardpoint_connection import GuardPointConnection, GuardPointAuthType

log = logging.getLogger(__name__)


class GuardPointError(Exception):
    pass


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

    def delete_card_holder(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = self.baseurl + "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")"

        code, response_body = self.query("DELETE", url=(url + url_query_params))

        if code == 204:  # HTTP NO_CONTENT
            return True
        else:
            try:
                response_body = json.loads(response_body)
                if 'error' in response_body:
                    raise GuardPointError(response_body['error'])
                else:
                    raise GuardPointError(str(code))
            except Exception:
                raise GuardPointError(str(code))

    def add_card_holder(self, cardholder: Cardholder):

        url = "/odata/API_Cardholders/CreateFullCardholder"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'IgnoreNonEditable': ''
        }

        body = cardholder.dict()
        if 'uid' in body['cardholder']:
            body['cardholder'].pop('uid')
        if 'status' in body['cardholder']:
            body['cardholder'].pop('status')
        #if 'cardholderType' in body['cardholder']:
        #    body['cardholder'].pop('cardholderType')
        #if 'securityGroup' in body['cardholder']:
        #    body['cardholder'].pop('securityGroup')
        if 'cards' in body['cardholder']: #Need to add cards in a second call
            body['cardholder'].pop('cards')

        #print(json.dumps(body))
        code, response_body = self.query("POST", headers=headers, url=url, body=json.dumps(body))

        # Try to convert body into json
        try:
            response_body = json.loads(response_body)
        except JSONDecodeError:
            response_body = None
        except Exception as e:
            log.error(e)
            response_body = None

        if code == 201:  # HTTP CREATED
            return response_body['value'][0]
        else:
            if "errorMessages" in response_body:
                raise GuardPointError(response_body["errorMessages"][0]["other"])
            else:
                raise GuardPointError(str(code))

    def get_card_holder(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?" \
                                       "$expand=" \
                                       "cardholderType($select=typeName)," \
                                       "cards($select=cardCode)," \
                                       "cardholderPersonalDetail($select=email,company,idType,idFreeText)," \
                                       "securityGroup($select=name)&" \
                                       "$select=uid," \
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

        # Try to convert body into json
        try:
            response_body = json.loads(response_body)
        except JSONDecodeError:
            response_body = None
        except Exception as e:
            log.error(e)
            response_body = None

        if code == 200:
            if isinstance(response_body, dict):
                if 'value' in response_body:
                    return Cardholder(response_body['value'][0])
                else:
                    raise GuardPointError("Badly formatted response.")
            else:
                raise GuardPointError("Badly formatted response.")
        else:
            if isinstance(response_body, dict):
                if 'error' in response_body:
                    raise GuardPointError(response_body['error'])
            raise GuardPointError(str(code))

    @staticmethod
    def _compose_filter(search_words, cardholder_type_name):
        filter_str = ""
        if cardholder_type_name or search_words:
            filter_str = "$filter="
        if cardholder_type_name:
            filter_str += f"(cardholderType/typeName%20eq%20'{cardholder_type_name}')"
            if search_words:
                filter_str += "%20and%20"
        if search_words:
            words = list(filter(None, search_words.split(" ")))[
                    :5]  # Split by space, remove empty elements, ignore > 5 elements
            fields = ["firstName", "lastName", "CardholderPersonalDetail/company"]
            phrases = []
            for f in fields:
                for v in words:
                    phrases.append(f"contains({f},'{v}')")
            filter_str += f"({'%20or%20'.join(phrases)})"
        if cardholder_type_name or search_words:
            filter_str += "&"
        return filter_str

    def get_card_holders(self, offset=0, limit=10, searchPhrase=None, cardholder_type_name=None):
        url = "/odata/API_Cardholders"
        filter_str = self._compose_filter(search_words=searchPhrase, cardholder_type_name=cardholder_type_name)
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

        # Try to convert body into json
        try:
            response_body = json.loads(response_body)
        except JSONDecodeError:
            response_body = None
        except Exception as e:
            log.error(e)
            response_body = None

        if code == 200:
            cardholders = []
            for x in response_body['value']:
                cardholders.append(Cardholder(x))
            return cardholders
        else:
            if isinstance(response_body, dict):
                if 'error' in response_body:
                    raise GuardPointError(response_body['error'])
            raise GuardPointError(str(code))

        return response_body


# conn = Connection()
# conn.query("GET", "/odata/$metadata")
# log.info("End")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")
    try:
        # Example getting a single cardholder
        cardholder = gp.get_card_holder("000a1e34-3bef-4bf5-90d5-37403ac0b014")
        print("Got back a: " + str(type(cardholder)))
        if isinstance(cardholder, Cardholder):
            print("Cardholder:")
            print("\tUID: " + cardholder.uid)
            print("\tFirstname: " + cardholder.firstName)
            print("\tLastname: " + cardholder.lastName)
            print("\tCardholder Type: " + cardholder.cardholderType.typeName)
            print("Cardholder as dictionary")
            print("\t" + json.dumps(cardholder.dict()), 3)
    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        # Example getting a list of cardholders
        cardholders = gp.get_card_holders(limit=1, searchPhrase="john owen")
        print("Got back a: " + str(type(cardholders)) + " containing: " + str(len(cardholders)) + " entry.")
        if isinstance(cardholders, list):
            for cardholder in cardholders:
                print("Cardholder: ")
                print("\tUID: " + cardholder.uid)
                print("\tFirstname: " + cardholder.firstName)
                print("\tLastname: " + cardholder.lastName)
    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        # Example get all cardholders in batches of 5
        all_cardholders = []
        batch_of_cardholders = gp.get_card_holders(limit=5, offset=0, cardholder_type_name="Visitor")
        while len(batch_of_cardholders) > 0:
            all_cardholders.extend(batch_of_cardholders)
            batch_of_cardholders = gp.get_card_holders(limit=5, offset=(len(all_cardholders)), cardholder_type_name="Visitor")

        print(f"Got a list of: {len(all_cardholders)}")
        for cardholder in all_cardholders:
            print("Cardholder: ")
            print("\tUID: " + cardholder.uid)
            print("\tFirstname: " + cardholder.firstName)
            print("\tLastname: " + cardholder.lastName)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        # Example delete the first cardholder
        cardholder_list = gp.get_card_holders(limit=1, offset=0, cardholder_type_name="Visitor")
        if len(cardholder_list) > 0:
            cardholder = cardholder_list[0]
            if gp.delete_card_holder(cardholder.uid):
                print("Cardholder: " + cardholder.firstName + " deleted.")

                uid = gp.add_card_holder(cardholder)
                print("Cardholder: " + cardholder.firstName + " added, with the new UID:" + uid)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
