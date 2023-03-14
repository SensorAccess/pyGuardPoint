import validators

from ._odata_filter import _compose_filter
from ._str_match_algo import fuzzy_match
from .guardpoint_dataclasses import Cardholder, SortAlgorithm
from .guardpoint_error import GuardPointError


class CardholdersAPI:

    def delete_card_holder(self, cardholder: Cardholder):
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        url = self.baseurl + "/odata/API_Cardholders"
        url_query_params = "(" + cardholder.uid + ")"

        code, json_body = self.gp_json_query("DELETE", url=(url + url_query_params))

        if code != 204:  # HTTP NO_CONTENT
            try:
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
                else:
                    raise GuardPointError(str(code))
            except Exception:
                raise GuardPointError(str(code))

        return True

    # TODO use UpdateFullCardholder instead
    def update_card_holder(self, cardholder: Cardholder):
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        url = "/odata/API_Cardholders"
        url_query_params = f"({cardholder.uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'IgnoreNonEditable': ''
        }

        ch = cardholder.dict(editable_only=True)

        code, json_body = self.gp_json_query("PATCH", headers=headers, url=(url + url_query_params), json_body=ch)

        if code != 204:  # HTTP NO_CONTENT
            try:
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
                else:
                    raise GuardPointError(str(code))
            except Exception:
                raise GuardPointError(str(code))

        return True

    def add_card_holder(self, cardholder: Cardholder, overwrite_cardholder=False):

        url = "/odata/API_Cardholders/CreateFullCardholder"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'IgnoreNonEditable': ''
        }

        ch = cardholder.dict()

        # Filter out un-settable variables
        if 'uid' in ch:
            ch.pop('uid')
        if 'status' in ch:
            ch.pop('status')
        # if 'cardholderType' in body['cardholder']:
        #    body['cardholder'].pop('cardholderType')
        if 'securityGroup' in ch:
            ch.pop('securityGroup')
        if 'cards' in ch:  # Need to add cards in a second call
            for card in ch['cards']:
                if 'uid' in card:
                    card.pop('uid')

        body = {'cardholder': ch}
        # print(json.dumps(body))
        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code == 201:  # HTTP CREATED
            return json_body['value'][0]
        elif code == 422:  # unprocessable Entity
            if "errorMessages" in json_body:
                if json_body["errorMessages"][0]["errorCode"] == 59:  # Cardholder_0_AlreadyExists
                    self.update_card_holder(cardholder)
        else:
            if "errorMessages" in json_body:
                raise GuardPointError(json_body["errorMessages"][0]["other"])
            elif "error" in json_body:
                raise GuardPointError(json_body["error"]['message'])
            else:
                raise GuardPointError(str(code))

    def get_card_holder(self,
                        uid: str = None,
                        card_code: str = None):
        if card_code:
            # Part of the Cards_API
            return self.get_cardholder_by_card_code(card_code)
        else:
            return self._get_card_holder(uid)

    def _get_card_holder(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?" \
                                       "$expand=" \
                                       "cardholderType($select=typeName)," \
                                       "cards," \
                                       "cardholderPersonalDetail($select=email,company,idType,idFreeText)," \
                                       "securityGroup," \
                                       "insideArea"

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
            else:
                raise GuardPointError(str(code))

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")

        return Cardholder(json_body['value'][0])

    def get_card_holders(self, offset: int = 0, limit: int = 10, search_terms: str = None, areas: list = None,
                         filter_expired: bool = False, cardholder_type_name: str = None,
                         sort_algorithm: SortAlgorithm = SortAlgorithm.SERVER_DEFAULT, threshold: int = 75):
        url = "/odata/API_Cardholders"
        filter_str = _compose_filter(search_words=search_terms, areas=areas, filter_expired=filter_expired,
                                     cardholder_type_name=cardholder_type_name)
        url_query_params = ("?" + filter_str +
                            "$expand="
                            "cardholderType($select=typeName),"
                            "cards,"
                            "cardholderPersonalDetail,"
                            "insideArea,"
                            "securityGroup&"
                            "$orderby=fromDateValid%20desc&"
                            "$top=" + str(limit) + "&$skip=" + str(offset)
                            )

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        cardholders = []
        for x in json_body['value']:
            cardholders.append(Cardholder(x))

        if sort_algorithm == SortAlgorithm.FUZZY_MATCH:
            cardholders = fuzzy_match(search_words=search_terms, cardholders=cardholders, threshold=threshold)

        return cardholders
