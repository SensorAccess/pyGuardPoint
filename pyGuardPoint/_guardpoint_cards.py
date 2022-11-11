import json
import validators

from pyGuardPoint.guardpoint_dataclasses import Card, Cardholder
from pyGuardPoint.guardpoint_error import GuardPointError


class CardsAPI:
    def get_cards(self):
        url = "/odata/API_Cards"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = self.gp_json_query("GET", headers=headers, url=url)

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

        cards = []
        for x in json_body['value']:
            cards.append(Card(x))
        return cards

    def delete_card(self, card: Card):
        if not validators.uuid(card.uid):
            raise ValueError(f'Malformed Card UID {card.uid}')

        url = "/odata/API_Cards"
        url_query_params = "(" + card.uid + ")"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = self.gp_json_query("DELETE", headers=headers, url=(url + url_query_params))

        if code != 204:  # HTTP NO_CONTENT
            try:
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
                else:
                    raise GuardPointError(str(code))
            except Exception:
                raise GuardPointError(str(code))

        return True

    def add_card(self, card: Card):
        url = "/odata/API_Cards"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = card.dict(editable_only=True)

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code == 201:  # HTTP CREATED
            return json_body['uid']
        else:
            if "errorMessages" in json_body:
                raise GuardPointError(json_body["errorMessages"][0]["other"])
            elif "error" in json_body:
                raise GuardPointError(json_body["error"]['message'])
            else:
                raise GuardPointError(str(code))

    def lookup(self, card_code):
        url = "/odata/API_Cards"
        url_query_params = f"?$filter=cardcode%20eq%20'{card_code}'%20and%20status%20eq%20'Used'%20" \
                           "&$expand=cardholder(" \
                           "$expand=securityGroup($select=name)," \
                           "cardholderType($select=typeName)," \
                           "cards," \
                           "cardholderPersonalDetail," \
                           "securityGroup)"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

        card_holders = []
        for x in json_body['value']:
            if 'cardholder' in x:
                card_holders.append(Cardholder(x['cardholder']))
        return card_holders
