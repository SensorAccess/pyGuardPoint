import validators

from ..guardpoint_utils import GuardPointResponse, reader_zone_uid
from ..guardpoint_dataclasses import (AlarmZone, AlarmZoneOption, AlarmZoneArmType, ArmBypassMode,
                                      AlarmZoneDisarmType, ArmAlarmZoneResult)
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized


class AlarmZonesAPI:

    async def arm_alarm_zone(self, alarm_zone: AlarmZone, option=AlarmZoneOption.ReturnAlarmZoneToWeeklyProgram,
                              arm_type: AlarmZoneArmType = AlarmZoneArmType.ArmUntilNextIntervalInWP,
                              period: int = 0, is_minute: bool = True,
                              bypass_mode: ArmBypassMode = None):
        """Arm an AlarmZone, or return it to its Weekly Program.

        Returns an ArmAlarmZoneResult, which is truthy on success and carries
        result.triggered_inputs - the inputs that were in alarm when the request
        was made. Servers older than the ArmAlarmZoneResponse release, and the
        ReturnAlarmZoneToWeeklyProgram option, report an empty list.
        """
        body = dict()
        body['uid'] = alarm_zone.uid

        if option == AlarmZoneOption.ReturnAlarmZoneToWeeklyProgram:
            url = "/odata/API_AlarmZones/ReturnAlarmZoneToWeeklyProgram"
        elif option == AlarmZoneOption.Arm:
            url = "/odata/API_AlarmZones/ArmAlarmZone"
            body['armType'] = arm_type.name
            body['period'] = period
            body['isMinute'] = is_minute
            if bypass_mode is not None:
                body['armBypassMode'] = bypass_mode.name
        else:
            raise GuardPointError(f"Unsupported Arming Option")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        code, json_body = await self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"AlarmZone Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")

        return ArmAlarmZoneResult(json_body)

    async def disarm_alarm_zone(self, alarm_zone: AlarmZone,
                                 disarm_type: AlarmZoneDisarmType = AlarmZoneDisarmType.DisarmUntilNextIntervalInWP,
                                 period: int = 1, is_minute: bool = True):
        url = self.baseurl + "/odata/API_AlarmZones/DisarmAlarmZone"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        body = dict()
        body["uid"] = alarm_zone.uid
        body["disarmType"] = disarm_type.name
        body["period"] = period
        body["isMinute"] = is_minute

        code, json_body = await self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"AlarmZone Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")

        return bool(json_body.get('success', False))

    async def get_alarm_zone(self, zone_uid):
        url = self.baseurl + "/odata/API_AlarmZones"
        url_query_params = f"({zone_uid})"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

        return AlarmZone(json_body['value'][0])

    async def get_reader_alarm_zone(self, reader, inputs=None, alarm_zones=None):
        """Return the AlarmZone a Reader's door belongs to, or None.

        GuardPoint10 exposes no direct Reader-to-AlarmZone relationship, so this
        follows the only chain that exists:

            Reader.doorAlarmInputUID -> Input.uid, Input.inputGroupUID -> AlarmZone.uid

        falling back through the reader's other door-input fields. Returns None when
        none of the reader's inputs are assigned to a zone - common, since inputs
        default to no zone.

        Pass pre-fetched `inputs` / `alarm_zones` when calling this in a loop,
        otherwise every call re-fetches both collections.

        :param reader: a Reader, or a reader uid to look up via get_reader().
        :param inputs: optional list of Input, defaults to get_inputs().
        :param alarm_zones: optional list of AlarmZone, defaults to get_alarm_zones().
        :raises ValueError: if a malformed reader uid is passed.
        :raises GuardPointError: if a reader uid is passed and no such reader exists.
        :return: the AlarmZone, or None.
        """
        if isinstance(reader, str):
            reader = await self.get_reader(reader)

        inputs = await self.get_inputs() if inputs is None else inputs
        alarm_zones = await self.get_alarm_zones() if alarm_zones is None else alarm_zones

        zone_uid = reader_zone_uid(reader, {i.uid: i for i in inputs})
        if zone_uid is None:
            return None

        for alarm_zone in alarm_zones:
            if alarm_zone.uid == zone_uid:
                return alarm_zone
        return None

    async def get_alarm_zone_readers(self, alarm_zone, readers=None, inputs=None):
        """Return the Readers whose doors belong to an AlarmZone.

        The reverse of get_reader_alarm_zone() - see there for how the join works
        and why a reader may belong to no zone at all.

        :param alarm_zone: an AlarmZone, or an alarm zone uid.
        :param readers: optional list of Reader, defaults to get_readers().
        :param inputs: optional list of Input, defaults to get_inputs().
        :return: list of Reader, empty if the zone owns no reader's door inputs.
        """
        zone_uid = alarm_zone if isinstance(alarm_zone, str) else alarm_zone.uid

        readers = await self.get_readers() if readers is None else readers
        inputs = await self.get_inputs() if inputs is None else inputs
        inputs_by_uid = {i.uid: i for i in inputs}

        return [reader for reader in readers
                if reader_zone_uid(reader, inputs_by_uid) == zone_uid]

    async def get_alarm_zones(self):
        url = self.baseurl + "/odata/API_AlarmZones"

        code, json_body = await self.gp_json_query("GET", url=url)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"No Outputs Found")
            else:
                raise GuardPointError(f"{error_msg}")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        # Compose list of security groups
        alarm_zones = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                relay = AlarmZone(entry)
                alarm_zones.append(relay)
        return alarm_zones
