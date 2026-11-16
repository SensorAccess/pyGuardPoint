import validators
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import Controller
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from .._action_helpers import uid_or_api_key_body


class ControllersAPI:
    async def get_controllers(self):
        url = "/odata/API_Controllers"
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
                return None
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        controllers = []
        for x in json_body['value']:
            controllers.append(Controller(x))
        return controllers

    async def get_controller(self, controller_uid: str):
        if not validators.uuid(controller_uid):
            raise ValueError(f"Malformed controller_uid: {controller_uid}")

        url = "/odata/API_Controllers"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        url_query_params = f"({controller_uid})"

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
        if len(json_body) < 1:
            return None
        else:
            return Controller(json_body['value'][0])

    async def initialize_controller(self, controller_or_uid=None, api_key: str = None):
        """
        Re-initialise a controller (re-download its tables) - ``API_Controllers/InitializeController``.

        :param controller_or_uid: ``Controller`` object or UID. Mutually exclusive with ``api_key``.
        :param api_key: The controller's API key.
        :return: ``True`` on success.
        """
        body = uid_or_api_key_body(controller_or_uid, api_key, "controller")
        await self._gp_call("POST", "/odata/API_Controllers/InitializeController", body, "Controller Not Found")
        return True
