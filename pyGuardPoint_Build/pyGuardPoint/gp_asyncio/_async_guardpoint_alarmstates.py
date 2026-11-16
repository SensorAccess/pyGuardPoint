import validators

from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import AlarmState
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from .._action_helpers import resolve_uid


class AlarmStatesAPI:
    async def get_alarm_state(self, alarm_uid):
        if not validators.uuid(alarm_uid):
            raise ValueError(f"Malformed alarm_uid: {alarm_uid}")

        url = f"/odata/API_AlarmStates({alarm_uid})?$expand=Input"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = await self.gp_json_query("GET", headers=headers, url=url)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Alarm State Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")

        # Single-entity fetches return the entity itself, not wrapped in 'value'
        value = json_body.get('value', json_body)
        if isinstance(value, list):
            value = value[0] if value else None
        if not value:
            return None
        return AlarmState({k: v for k, v in value.items() if not k.startswith('@odata.')})

    async def get_alarm_states(self):
        url = "/odata/API_AlarmStates?$expand=Input"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = await self.gp_json_query("GET", headers=headers, url=url)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Alarm State Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        alarm_states = []
        for x in json_body['value']:
            alarm_states.append(AlarmState(x))
        return alarm_states

    # ------------------------------------------------------------------ alarm actions

    async def acknowledge_alarm(self, alarm_or_uid):
        """
        Acknowledge an alarm (``API_AlarmStates/AcknowledgeAlarm``).

        :param alarm_or_uid: ``AlarmState`` object or its UID.
        :return: ``True`` on success.
        """
        body = {'uid': resolve_uid(alarm_or_uid, "alarm")}
        await self._gp_call("POST", "/odata/API_AlarmStates/AcknowledgeAlarm", body, "Alarm Not Found")
        return True

    async def confirm_alarm(self, alarm_or_uid, description: str = "Confirmed by API"):
        """
        Confirm (close) an alarm (``API_AlarmStates/ConfirmAlarm``), recording ``description``.

        :param alarm_or_uid: ``AlarmState`` object or its UID.
        :return: ``True`` on success.
        """
        body = {'uid': resolve_uid(alarm_or_uid, "alarm"), 'description': description}
        await self._gp_call("POST", "/odata/API_AlarmStates/ConfirmAlarm", body, "Alarm Not Found")
        return True
