import validators

from ..guardpoint_dataclasses import Site
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized
from .._action_helpers import resolve_uid


class SitesAPI:
    async def get_site(self, site_uid):
        if not validators.uuid(site_uid):
            raise ValueError(f"Malformed site_uid: {site_uid}")

        url = f"/odata/API_Sites({site_uid})"
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
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")

        if len(json_body['value']) > 0:
            return Site(json_body['value'][0])
        else:
            return None

    async def get_sites(self):
        url = "/odata/API_Sites"
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
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        sites = []
        for x in json_body['value']:
            sites.append(Site(x))
        return sites

    async def start_site_polling(self, site_or_uid):
        """Start polling every network on a site (``API_Sites/StartAllPolling``). Returns ``True``."""
        body = {'uid': resolve_uid(site_or_uid, "site")}
        await self._gp_call("POST", "/odata/API_Sites/StartAllPolling", body, "Site Not Found")
        return True

    async def stop_site_polling(self, site_or_uid):
        """
        Stop polling every network on a site (``API_Sites/StopAllPolling``). Controllers on the
        site go offline to the server until :meth:`start_site_polling`. Returns ``True``.
        """
        body = {'uid': resolve_uid(site_or_uid, "site")}
        await self._gp_call("POST", "/odata/API_Sites/StopAllPolling", body, "Site Not Found")
        return True
