from datetime import datetime

import validators
from ._odata_filter import _compose_filter, _compose_select, _compose_expand
from ._str_match_algo import fuzzy_match
from .guardpoint_dataclasses import Cardholder, SortAlgorithm, Area
from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from .guardpoint_utils import GuardPointResponse


class CardholdersAPI:

    def delete_card_holder(self, cardholder: Cardholder):
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        url = self.baseurl + "/odata/API_Cardholders"
        url_query_params = "(" + cardholder.uid + ")"

        code, json_body = self.gp_json_query("DELETE", url=(url + url_query_params))
        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code != 204:  # HTTP NO_CONTENT
            if "errorMessages" in json_body:
                raise GuardPointError(json_body["errorMessages"][0]["other"])
            if 'error' in json_body:
                raise GuardPointError(json_body['error'])
            else:
                raise GuardPointError(str(code))


        return True

    def update_card_holder_area(self, cardholder_uid: str, area: Area):
        if not validators.uuid(cardholder_uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder_uid}')

        if not validators.uuid(area.uid):
            raise ValueError(f'Malformed Area UID {area.uid}')

        cardholder = Cardholder()
        cardholder.uid = cardholder_uid
        cardholder.insideAreaUID = area.uid

        return self.update_card_holder(cardholder)

    def update_card_holder(self, cardholder: Cardholder):
        if not validators.uuid(cardholder.uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')

        if cardholder.cardholderCustomizedField:
            if len(cardholder.cardholderCustomizedField.changed_attributes) > 0:
                self.update_custom_fields(cardholder.uid, cardholder.cardholderCustomizedField)

        if cardholder.cardholderPersonalDetail:
            if len(cardholder.cardholderPersonalDetail.changed_attributes) > 0:
                self.update_personal_details(cardholder.uid, cardholder.cardholderPersonalDetail)

        if cardholder.cards:
            if isinstance(cardholder.cards, list):
                for card in cardholder.cards:
                    if len(card.changed_attributes) > 0:
                        if validators.uuid(card.uid):
                            self.update_card(card)
                        else:
                            card.cardholderUID = cardholder.uid
                            self.new_card(card)

        ch = cardholder.dict(editable_only=True, changed_only=True)

        if len(ch) < 1:  # Nothing to update
            return True

        url = "/odata/API_Cardholders"
        url_query_params = f"({cardholder.uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'IgnoreNonEditable': ''
        }

        code, json_body = self.gp_json_query("PATCH", headers=headers, url=(url + url_query_params), json_body=ch)
        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code != 204:  # HTTP NO_CONTENT
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']
                elif 'message' in json_body:
                    error_msg = json_body['message']
                else:
                    error_msg = str(code)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        return True

    def new_card_holder(self, cardholder: Cardholder, overwrite_cardholder=False):

        # url = "/odata/API_Cardholders/CreateFullCardholder"
        url = "/odata/API_Cardholders"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'IgnoreNonEditable': ''
        }

        ch = cardholder.dict(editable_only=True, changed_only=True)

        # When using CreateFullCardholder
        # body = {'cardholder': ch}
        # print(json.dumps(body))
        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=ch)
        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code == 201:  # HTTP CREATED
            new_cardholder = Cardholder(json_body)
            if cardholder.cardholderPersonalDetail:
                self.update_personal_details(cardholder_uid=new_cardholder.uid,
                                             personal_details=cardholder.cardholderPersonalDetail)
            if cardholder.cardholderCustomizedField:
                self.update_custom_fields(cardholder_uid=new_cardholder.uid,
                                          customFields=cardholder.cardholderCustomizedField)
            if cardholder.cards:
                if isinstance(cardholder.cards, list):
                    for card in cardholder.cards:
                        if validators.uuid(card.uid):
                            self.update_card(card)
                        else:
                            card.cardholderUID = new_cardholder.uid
                            self.new_card(card)

            return self._get_card_holder(new_cardholder.uid)

        elif code == 422:  # unprocessable Entity
            if "errorMessages" in json_body:
                raise GuardPointError(
                    f'{json_body["errorMessages"][0]["message"]}-{json_body["errorMessages"][0]["other"]}')
        else:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']
                elif "errorMessages" in json_body:
                    error_msg = json_body["errorMessages"][0]["other"]
                elif "error" in json_body:
                    error_msg = GuardPointError(json_body["error"]['message'])
                else:
                    error_msg = str(code)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")


    def get_card_holder(self,
                        uid: str = None,
                        card_code: str = None):
        if card_code:
            # Part of the Cards_API
            return self.get_cardholder_by_card_code(card_code)
        else:
            return self._get_card_holder(uid)

    def get_card_holder_photo(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?$select=photo"

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))
        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code != 200:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        return json_body['value'][0]['photo']

    def _get_card_holder(self, uid):
        if not validators.uuid(uid):
            raise ValueError(f'Malformed UID {uid}')

        url = "/odata/API_Cardholders"
        url_query_params = "(" + uid + ")?" \
                                       "$expand=" \
                                       "cardholderType," \
                                       "cards," \
                                       "cardholderCustomizedField," \
                                       "cardholderPersonalDetail," \
                                       "securityGroup," \
                                       "insideArea"

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))
        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code == 404: # Not Found
            return None

        if code != 200:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        return Cardholder(json_body['value'][0])

    def get_card_holders(self, offset: int = 0, limit: int = 10, search_terms: str = None, areas: list = None,
                         filter_expired: bool = False, cardholder_type_name: str = None,
                         sort_algorithm: SortAlgorithm = SortAlgorithm.SERVER_DEFAULT, threshold: int = 75,
                         count: bool = False, earliest_last_pass: datetime = None,
                         select_ignore_list: list = None, select_include_list: list = None,
                         **cardholder_kwargs):

        # Filter arguments which have to exact match
        match_args = dict()
        for k, v in cardholder_kwargs.items():
            if hasattr(Cardholder, k):
                match_args[k] = v

        url = "/odata/API_Cardholders"

        filter_str = _compose_filter(search_words=search_terms,
                                     areas=areas,
                                     filter_expired=filter_expired,
                                     cardholder_type_name=cardholder_type_name,
                                     earliest_last_pass=earliest_last_pass,
                                     exact_match=match_args)

        select_str = _compose_select(select_ignore_list, select_include_list)

        expand_str = _compose_expand(select_ignore_list, select_include_list)

        url_query_params = ("?" + select_str + expand_str + filter_str)
        # url_query_params = ("?" + filter_str)

        if count:
            url_query_params += "$count=true&$top=0"
        else:
            url_query_params += "$orderby=fromDateValid%20desc&"
            url_query_params += "$top=" + str(limit) + "&$skip=" + str(offset)

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))
        # Check response body is formatted correctly
        if json_body:
            GuardPointResponse.check_odata_body_structure(json_body)

        if code != 200:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        if count:
            return json_body['@odata.count']

        cardholders = []
        for x in json_body['value']:
            cardholders.append(Cardholder(x))

        if sort_algorithm == SortAlgorithm.FUZZY_MATCH:
            cardholders = fuzzy_match(search_words=search_terms, cardholders=cardholders, threshold=threshold)

        return cardholders
