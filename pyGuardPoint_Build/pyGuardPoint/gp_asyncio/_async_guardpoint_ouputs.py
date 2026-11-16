import validators

from ..guardpoint_dataclasses import Relay
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from .._action_helpers import json_headers, resolve_uid, uids_or_api_keys_body, value_list, parse_output_result, output_error_msg
from ..guardpoint_dataclasses import Reader
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized

class OutputsAPI:

    async def get_relay(self, relay_uid):
        url = "/odata/API_Outputs"
        url_query_params = f"({relay_uid})"
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

        return Relay(json_body['value'][0])


    async def get_relays(self):
        url = "/odata/API_Outputs"

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
        relays = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                relay = Relay(entry)
                relays.append(relay)
        return relays

    async def activate_relay(self, relay: Relay, period: int = 0):
        return await self.activate_relay_by_uid(relay.uid, period)

    async def activate_relay_by_uid(self, relay_uid: str, period: int = 0):

        url = "/odata/API_Outputs/Activate"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        if not validators.uuid(relay_uid):
            raise ValueError("Malformed Relay UID")

        body = dict()
        body["uids"] = [relay_uid]
        body["period"] = period

        code, json_body = await self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)
            if isinstance(json_body, dict):
                if len(json_body) == 1:
                    r_uid = list(json_body.keys())[0]
                    if validators.uuid(r_uid):
                        if 'item1' in json_body[r_uid]:
                            error_msg = GuardPointResponse.extract_error_msg(json_body[r_uid]['item1'])

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Relay Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        return True

    # ------------------------------------------------------------------ relay / door actions
    # The output actions return a per-relay map (Dictionary<Guid,String>). Methods return it
    # as ``{relay_uid: message}`` - empty means no per-relay detail was reported.

    async def _output_action(self, action: str, body=None):
        code, json_body = await self.gp_json_query("POST", url=f"/odata/API_Outputs/{action}",
                                             json_body=body or '', headers=json_headers() if body else None)
        if code != 200:
            error_msg = output_error_msg(json_body)
            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:
                raise GuardPointError(error_msg or "Relay Not Found")
            raise GuardPointError(error_msg or f"HTTP {code}")
        return parse_output_result(json_body)

    async def activate_relays(self, relays=None, api_keys=None, period: int = 0):
        """
        Activate one or more relays, identified by object/UID and/or API key.

        :param relays: ``Relay``, UID, or a list of either.
        :param api_keys: API key or list of API keys.
        :param period: Seconds to hold the relay active. ``0`` = constantly on (until
            :meth:`return_relays_to_normal` / :meth:`deactivate_relays`).
        :return: per-relay result dict ``{relay_uid: message}``.
        """
        body = uids_or_api_keys_body(relays, api_keys, "relay")
        body['period'] = int(period)
        return await self._output_action("Activate", body)

    async def activate_relay_by_api_key(self, api_key: str, period: int = 0):
        """Activate a single relay by API key. ``period`` 0 = constantly on."""
        return await self.activate_relays(api_keys=[api_key], period=period)

    async def deactivate_relays(self, relays=None, api_keys=None):
        """Force one or more relays off (overrides their weekly programme)."""
        return await self._output_action("Deactivate", uids_or_api_keys_body(relays, api_keys, "relay"))

    async def return_relays_to_normal(self, relays=None, api_keys=None):
        """Return one or more relays to normal (weekly-programme) operation."""
        return await self._output_action("ReturnToNormal", uids_or_api_keys_body(relays, api_keys, "relay"))

    async def activate_all_readers(self):
        """Activate the door relay of every reader (``ActivateAllReaders``)."""
        return await self._output_action("ActivateAllReaders")

    async def deactivate_all_readers(self):
        """Deactivate the door relay of every reader (``DeactivateAllReaders``)."""
        return await self._output_action("DeactivateAllReaders")

    async def return_to_normal_all_readers(self):
        """Return every reader's door relay to normal (``ReturnToNormalAllReaders``)."""
        return await self._output_action("ReturnToNormalAllReaders")

    async def open_all_door_relays(self, period: int = None):
        """
        Broadcast OPEN to every door relay.

        :param period: If given, open for this many seconds (``OpenAllDoorRelaysWithPeriod``);
            otherwise doors stay open until :meth:`return_to_normal_all_door_relays`.
        """
        if period is None:
            return await self._output_action("OpenAllDoorRelays")
        return await self._output_action("OpenAllDoorRelaysWithPeriod", {'period': int(period)})

    async def close_all_door_relays(self):
        """Broadcast CLOSE to every door relay (``CloseAllDoorRelays``)."""
        return await self._output_action("CloseAllDoorRelays")

    async def return_to_normal_all_door_relays(self):
        """Broadcast return-to-normal to every door relay (``ReturnToNormalAllDoorRelays``)."""
        return await self._output_action("ReturnToNormalAllDoorRelays")

    async def get_relay_readers(self, relay_or_uid):
        """Readers driven by a relay (``API_Outputs({uid})/Readers``). Returns ``list[Reader]``."""
        uid = resolve_uid(relay_or_uid, "relay")
        json_body = await self._gp_call("GET", f"/odata/API_Outputs({uid})/Readers", not_found_msg="Relay Not Found")
        return [Reader(r) for r in value_list(json_body)]
