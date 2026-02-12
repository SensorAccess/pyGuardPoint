from .guardpoint_dataclasses import ManualEvent
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class ManualEventsAPI:

    def get_manual_events(self):
        url = self.baseurl + "/odata/API_ManualEvents/"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        code, json_body = self.gp_json_query("GET", headers=headers, url=(url))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                return None
            else:
                raise GuardPointError(f"{error_msg}")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        manual_events = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                manual_event = ManualEvent(entry)
                manual_events.append(manual_event)
        return manual_events

    def activate_manual_event(self, manual_event):
        url = self.baseurl + "/odata/API_ManualEvents/ActivateManualEvent"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = dict()
        body['uid'] = manual_event.uid

        code, json_body = self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"ManualEvent Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'success' in json_body:
            if json_body['success']:
                return True
            else:
                return False
        else:
            return False
