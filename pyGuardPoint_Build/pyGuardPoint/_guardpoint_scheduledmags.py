from attr import validators

from .guardpoint_dataclasses import ScheduledMag, Cardholder
from .guardpoint_error import GuardPointError


class ScheduledMagsAPI:

    def get_scheduled_mags(self, cardholder: Cardholder = None):
        url = self.baseurl + "/odata/API_ScheduledMags"
        if cardholder.uid:
            if not validators.uuid(cardholder.uid):
                raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')
            url_query_params = f"?$filter=cardholderUid%20eq%20'{cardholder.uid}'"
        else:
            url_query_params = ""

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
            raise GuardPointError(str(code))

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        # Compose list of security groups
        scheduled_mags = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                sm = ScheduledMag(entry)
                scheduled_mags.append(sm)
        return scheduled_mags

    def add_scheduled_mag(self, scheduled_mag: ScheduledMag):
        url = self.baseurl + "/odata/API_ScheduledMags"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = scheduled_mag.dict(editable_only=True)

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