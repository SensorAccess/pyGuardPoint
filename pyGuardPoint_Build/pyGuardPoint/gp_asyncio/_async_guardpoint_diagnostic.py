import validators
from ..guardpoint_utils import GuardPointResponse

from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from .._action_helpers import resolve_uid


class DiagnosticAPI:
    '''
    {
        "controllersUIDs" :[
            "B3C0976A-3F8C-4B52-AE65-CB6F88FFD813"
        ],
        "command": "7901000000000A28"
    }
    '''
    async def simulate_access_event(self, controller_uid: str, reader_num: int, card_code: str):
        if not validators.uuid(controller_uid):
            raise ValueError(f"Malformed controller_uid: {controller_uid}")
        if len(card_code) < 8:
            raise ValueError(f"card_code too short (8 character minimum): {card_code}")
        if reader_num > 255:
            raise ValueError(f"Reader num too great (Max 255) {reader_num}")

        url = "/api/Diagnostic"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        controllers_uids = []
        controllers_uids.append(controller_uid)
        body = dict()
        body['controllersUIDs'] = controllers_uids
        body['command'] = "79{0:0>2X}{1:0>12s}".format(reader_num, card_code)

        code, json_body = await self.gp_json_query("POST", headers=headers, url=url, json_body=body)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Cardholder Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'success' in json_body:
            if json_body['success']:
                return True

        return False

    async def send_free_command(self, controllers, command: str):
        """
        Send a raw hex command to one or more controllers (``api/Diagnostic`` SendFreeCommand).

        This is the general form of :meth:`simulate_access_event`. Commands go straight to the
        controller firmware - only use documented command strings.

        :param controllers: ``Controller``, UID, or a list of either.
        :param command: hex command string, e.g. ``"7901000000000A28"``.
        :return: the server's response body (may be ``None``).
        """
        if not isinstance(controllers, (list, tuple, set)):
            controllers = [controllers]
        if not isinstance(command, str) or not command or any(c not in "0123456789abcdefABCDEF" for c in command):
            raise ValueError("command must be a non-empty hex string")
        body = {'controllersUIDs': [resolve_uid(c, "controller") for c in controllers], 'command': command}
        return await self._gp_call("POST", "/api/Diagnostic", body)
