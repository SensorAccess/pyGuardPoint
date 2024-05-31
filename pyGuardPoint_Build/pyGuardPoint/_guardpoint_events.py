import validators

from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import AlarmEvent, AccessEvent
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class EventsAPI:
    def get_access_events(self, limit=None, offset=None):
        url = f"/odata/API_AccessEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = "?$orderby=dateTime%20desc"

        if limit:
            url_query_params += "&$top=" + str(limit)
        if offset:
            url_query_params += "&$skip=" + str(offset)

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Access Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        access_events = []
        for x in json_body['value']:
            access_events.append(AccessEvent(x))
        return access_events

    def get_alarm_events(self, limit=None, offset=None):
        url = "/odata/API_AlarmEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = "?$orderby=dateTime%20asc"

        if limit:
            url_query_params += "&$top=" + str(limit)
        if offset:
            url_query_params += "&$skip=" + str(offset)

        code, json_body = self.gp_json_query("GET", headers=headers, url=(url+url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Alarm Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        alarm_events = []
        for x in json_body['value']:
            alarm_events.append(AlarmEvent(x))
        return alarm_events
