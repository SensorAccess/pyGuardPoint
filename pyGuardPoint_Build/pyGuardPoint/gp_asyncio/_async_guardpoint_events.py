from enum import Enum

from .._odata_filter import _compose_filter
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import (AccessEvent, AlarmEvent, EventOrder, AuditEvent, CommEvent, GeneralEvent,
                                      TechnicalEvent, UserManualEvent, ExtendedUnionEvent)
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from .._action_helpers import date_range_phrases, single_entity
from ..guardpoint_dataclasses import AccessEvent


class EventsAPI:

    @staticmethod
    def _build_url_params(site_uid, limit, offset, count, orderby, min_log_id, since=None, until=None):
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

        greater_than_args = None
        if min_log_id is not None and min_log_id > 0:
            greater_than_args = {'logID': min_log_id}

        match_args = None
        if site_uid is not None:
            match_args = {'ownerSiteUID': site_uid}

        if match_args is not None or greater_than_args is not None:
            filter_str = _compose_filter(exact_match=match_args, greater_than=greater_than_args)
        else:
            filter_str = ""

        date_phrases = date_range_phrases(since, until)
        if date_phrases:
            if filter_str:
                # "$filter=(A)&" -> "$filter=((A)%20and%20(dateTime ...))&"
                inner = filter_str[len("$filter="):-1]
                filter_str = f"$filter=({'%20and%20'.join([inner] + date_phrases)})&"
            else:
                filter_str = f"$filter=({'%20and%20'.join(date_phrases)})&"

        if filter_str:
            url_query_params += ("&" + filter_str)

        if limit:
            url_query_params += "&$top=" + str(limit)
        if offset:
            url_query_params += "&$skip=" + str(offset)

        return url_query_params

    async def get_access_events_count(self, since=None, until=None):
        return await self.get_access_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_access_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                          min_log_id=None, since=None, until=None):
        url = f"/odata/API_AccessEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

        if count:
            return json_body['@odata.count']
        else:
            access_events = []
            for x in json_body['value']:
                access_events.append(AccessEvent(x))
            return access_events

    async def get_alarm_events_count(self, since=None, until=None):
        return await self.get_alarm_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_alarm_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC, since=None, until=None):
        url = "/odata/API_AlarmEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, None, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

        if count:
            return json_body['@odata.count']
        else:
            alarm_events = []
            for x in json_body['value']:
                alarm_events.append(AlarmEvent(x))
            return alarm_events

    async def get_audit_events_count(self, since=None, until=None):
        return await self.get_audit_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_audit_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                         min_log_id=None, since=None, until=None):

        url = "/odata/API_AuditEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Audit Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            audit_events = []
            for x in json_body['value']:
                audit_events.append(AuditEvent(x))
            return audit_events

    async def get_comm_events_count(self, since=None, until=None):
        return await self.get_comm_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_comm_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                              min_log_id=None, since=None, until=None):
        url = "/odata/API_CommEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Comm Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            comm_events = []
            for x in json_body['value']:
                comm_events.append(CommEvent(x))
            return comm_events

    async def get_general_events_count(self, since=None, until=None):
        return await self.get_general_events(limit=None, offset=None, count=True, orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_general_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                                 min_log_id=None, since=None, until=None):
        url = "/odata/API_GeneralEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"General Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            general_events = []
            for x in json_body['value']:
                general_events.append(GeneralEvent(x))
            return general_events

    async def get_technical_events_count(self, since=None, until=None):
        return await self.get_technical_events(limit=None, offset=None, count=True,
                                               orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_technical_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                                   min_log_id=None, since=None, until=None):
        url = "/odata/API_TechnicalEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Technical Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            technical_events = []
            for x in json_body['value']:
                technical_events.append(TechnicalEvent(x))
            return technical_events

    async def get_user_manual_events_count(self, since=None, until=None):
        return await self.get_user_manual_events(limit=None, offset=None, count=True,
                                                 orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_user_manual_events(self, limit=None, offset=None, count=False, orderby=EventOrder.DATETIME_DESC,
                                     min_log_id=None, since=None, until=None):
        url = "/odata/API_UserManualEventLogs"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"User Manual Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            user_manual_events = []
            for x in json_body['value']:
                user_manual_events.append(UserManualEvent(x))
            return user_manual_events

    async def get_extended_union_events_count(self, since=None, until=None):
        return await self.get_extended_union_events(limit=None, offset=None, count=True,
                                                    orderby=EventOrder.DATETIME_DESC, since=since, until=until)

    async def get_extended_union_events(self, limit=None, offset=None, count=False,
                                        orderby=EventOrder.DATETIME_DESC, min_log_id=None, since=None, until=None):
        """
        Retrieve events from the API_ExtendedUnionEvents feed — a single merged view of
        every event log type (access, alarm, audit, comm, general, technical), each entry
        carrying an `eventType` field to identify its source log.
        """
        url = "/odata/API_ExtendedUnionEvents"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url_query_params = EventsAPI._build_url_params(self.site_uid, limit, offset, count, orderby, min_log_id, since, until)

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Extended Union Events Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        if count:
            return json_body['@odata.count']
        else:
            extended_union_events = []
            for x in json_body['value']:
                extended_union_events.append(ExtendedUnionEvent(x))
            return extended_union_events

    async def insert_access_event(self, access_event):
        """
        Write an access event into the GP10 access log (POST ``API_AccessEventLogs``) - e.g. to
        record passes from a third-party reader.

        :param access_event: ``AccessEvent`` or dict. Typical fields: ``dateTime``, ``type``
            (``"AccessGranted"``...), ``readerUID``, ``readerName``, ``cardholderUID``,
            ``cardCode``, ``cardholderFirstName``, ``cardholderLastName``.
        :return: the created ``AccessEvent`` if the server echoes it, else ``True``.
        """
        if hasattr(access_event, 'dict'):
            body = access_event.dict()
        elif isinstance(access_event, dict):
            body = dict(access_event)
        else:
            raise ValueError("access_event must be an AccessEvent or dict")
        # Server assigns these; sending empty/zero values is rejected.
        for k in ('uid', 'logID'):
            if not body.get(k):
                body.pop(k, None)
        body = {k: v for k, v in body.items() if v != ""}
        json_body = await self._gp_call("POST", "/odata/API_AccessEventLogs", body)
        entity = single_entity(json_body) if isinstance(json_body, dict) else None
        return AccessEvent(entity) if entity else True
