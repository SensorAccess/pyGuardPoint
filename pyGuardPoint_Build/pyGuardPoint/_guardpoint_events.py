from ._odata_filter import _compose_filter
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import AlarmEvent, AccessEvent, EventOrder
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class EventsAPI:
    """
    A class to interact with the events API, providing methods to retrieve access and alarm events.

    Methods
    -------
    get_access_events(limit=None, offset=None)
        Retrieves access events from the API with optional pagination.

    get_alarm_events(limit=None, offset=None)
        Retrieves alarm events from the API with optional pagination.
    """

    def get_access_events_count(self):
        return self.get_access_events(self, count=True)

    def get_access_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC):
        """
        Retrieve access event logs from the GuardPoint API.

        This method fetches access event logs, ordered by date and time in descending order.
        It supports pagination through the `limit` and `offset` parameters.

        :param limit: The maximum number of access events to retrieve. If not specified, all available events are retrieved.
        :type limit: int, optional
        :param offset: The number of access events to skip before starting to collect the result set. Useful for pagination.
        :type offset: int, optional
        :return: A list of `AccessEvent` objects representing the access events.
        :rtype: list of AccessEvent
        :raises GuardPointUnauthorized: If the API returns a 401 Unauthorized status code.
        :raises GuardPointError: If the API returns a 404 Not Found status code or any other error occurs.
        :raises GuardPointError: If the response body is not formatted as expected.
        """

        url = f"/odata/API_AccessEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if count:
            url_query_params = "?$count=true&$top=0"
        else:
            if orderby == EventOrder.DATETIME_ASC:
                url_query_params = "?$orderby=dateTime%20asc"
            elif orderby == EventOrder.DATETIME_DESC:
                url_query_params = "?$orderby=dateTime%20desc"
            elif orderby == EventOrder.LOG_ID_ASC:
                url_query_params = "?$orderby=logID%20asc"
            else:
                url_query_params = "?$orderby=logID%20desc"

        if limit:
            url_query_params += "&$top=" + str(limit)
        if offset:
            url_query_params += "&$skip=" + str(offset)

        if self.site_uid is not None:
            match_args = {'ownerSiteUID': self.site_uid}
            filter_str = _compose_filter(exact_match=match_args)
            url_query_params += ("&" + filter_str)

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
        """
        Retrieve a list of alarm events from the GuardPoint API.

        This method fetches alarm event logs from the GuardPoint API, with optional
        parameters to limit the number of results and to offset the starting point
        of the results.

        :param limit: Optional; the maximum number of alarm events to retrieve.
        :type limit: int, optional
        :param offset: Optional; the number of alarm events to skip before starting to collect the result set.
        :type offset: int, optional
        :return: A list of AlarmEvent objects representing the alarm events.
        :rtype: list[AlarmEvent]
        :raises GuardPointUnauthorized: If the API response indicates an unauthorized request (HTTP 401).
        :raises GuardPointError: If the API response indicates an error or if the response is badly formatted.
        """
        url = "/odata/API_AlarmEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = "?$orderby=dateTime%20asc"
        if self.site_uid is not None:
            match_args = {'ownerSiteUID': self.site_uid}
            filter_str = _compose_filter(exact_match=match_args)
            url_query_params += ("&" + filter_str)

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
