import json
from json import JSONDecodeError

import validators

from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from .._action_helpers import parse_options, parse_string_list


class GenericInfoAPI:
    async def get_info(self, info_uid):

        if not validators.uuid(info_uid):
            raise ValueError(f"Malformed site_uid: {info_uid}")

        url = f"/odata/API_GenericInformations({info_uid})"
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
                raise GuardPointError(f"Site Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'serializedData' not in json_body:
            raise GuardPointError("Badly formatted response.")

        if len(json_body['serializedData']) > 0:
            try:
                return json.loads(json_body['serializedData'])
            except JSONDecodeError as e:
                return json_body['serializedData']
        else:
            return None

    async def get_infos(self):

        url = "/odata/API_GenericInformations"
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
                raise GuardPointError(f"Site Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")

        return json_body

    async def is_sigr_enabled(self):
        info = await self.get_info('00000000-0000-0000-0000-000000000003')
        return info['CommunicationSettings']['PassEventsToApi']['Value']

    async def gp_version(self):
        info = await self.get_info('00000000-0000-0000-0000-000000000011')
        return info

    async def get_options_by_keys(self, keys):
        """
        Read named server options (``GetOptionsByKeys``).

        :param keys: option key or list of keys, e.g. ``["UniqueCardholderNumberRequired"]``.
        :return: ``{key: value}`` - unknown keys come back as ``None``.
        """
        if isinstance(keys, str):
            keys = [keys]
        return parse_options(await self._gp_call("POST", "/odata/GetOptionsByKeys", {'keys': list(keys)}))

    async def get_lite_options(self):
        """The reduced option set the GP10 web client uses (``GetLiteOptions``). Returns a dict."""
        return parse_options(await self._gp_call("GET", "/odata/GetLiteOptions"))

    async def get_non_editable_properties(self, entity_set: str = "API_Cards"):
        """
        Property names the server will not let you write on an entity set
        (``{entity_set}/GetNonEditableProperties``), e.g. ``"API_Cards"``, ``"API_Cardholders"``.

        :return: ``list[str]`` (empty if the server reports none).
        """
        if not entity_set.startswith("API_"):
            entity_set = "API_" + entity_set
        return parse_string_list(await self._gp_call("GET", f"/odata/{entity_set}/GetNonEditableProperties"))
