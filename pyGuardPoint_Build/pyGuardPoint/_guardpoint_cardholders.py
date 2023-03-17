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

    def update_card_holder(self, cardholder: Cardholder):
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        if cardholder.cardholderCustomizedField:
            if len(cardholder.cardholderCustomizedField.changed_attributes) > 0:
                self.update_custom_fields(cardholder.uid, cardholder.cardholderCustomizedField)

        if cardholder.cardholderPersonalDetail:
            if len(cardholder.cardholderPersonalDetail.changed_attributes) > 0:
                self.update_personal_details(cardholder.uid, cardholder.cardholderPersonalDetail)

        ch = cardholder.dict(editable_only=True, changed_only=True)

        if len(ch) < 1: # Nothing to update
            return True

        url = "/odata/API_Cardholders"
        url_query_params = f"({cardholder.uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            #'IgnoreNonEditable': ''
        }



        code, json_body = self.gp_json_query("PATCH", headers=headers, url=(url + url_query_params), json_body=ch)

        if code != 204:  # HTTP NO_CONTENT
            if 'error' in json_body:
                raise GuardPointError(json_body['error'])
            elif 'message' in json_body:
                raise GuardPointError(json_body['message'])
            else:
                raise GuardPointError(str(code))

        return True

    def new_card_holder(self, cardholder: Cardholder, overwrite_cardholder=False):

        #url = "/odata/API_Cardholders/CreateFullCardholder"
        url = "/odata/API_Cardholders"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'IgnoreNonEditable': ''
        }

        ch = cardholder.dict(editable_only=True)

        # When using CreateFullCardholder
        #body = {'cardholder': ch}
        # print(json.dumps(body))
        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=ch)

        if code == 201:  # HTTP CREATED
            return Cardholder(json_body)
        elif code == 422:  # unprocessable Entity
            if "errorMessages" in json_body:
                raise GuardPointError(f'{json_body["errorMessages"][0]["message"]}-{json_body["errorMessages"][0]["other"]}')
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
                                       "cardholderCustomizedField," \
                                       "cardholderPersonalDetail," \
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
                         sort_algorithm: SortAlgorithm = SortAlgorithm.SERVER_DEFAULT, threshold: int = 75,
                         count = False):

        url = "/odata/API_Cardholders"

        filter_str = _compose_filter(search_words=search_terms, areas=areas, filter_expired=filter_expired,
                                     cardholder_type_name=cardholder_type_name)

        url_query_params = ("?" + filter_str)

        if count:
            url_query_params += "$count=true&$top=0"
        else:
            url_query_params += "$expand=" \
                                    "cardholderType($select=typeName)," \
                                    "cards," \
                                    "cardholderPersonalDetail," \
                                    "cardholderCustomizedField," \
                                    "insideArea," \
                                    "securityGroup&" \
                                    "$orderby=fromDateValid%20desc&"
            url_query_params += "$top=" + str(limit) + "&$skip=" + str(offset)

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

        if count:
            return json_body['@odata.count']

        cardholders = []
        for x in json_body['value']:
            cardholders.append(Cardholder(x))

        if sort_algorithm == SortAlgorithm.FUZZY_MATCH:
            cardholders = fuzzy_match(search_words=search_terms, cardholders=cardholders, threshold=threshold)

        return cardholders
