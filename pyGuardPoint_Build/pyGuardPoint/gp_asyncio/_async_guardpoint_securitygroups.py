from .._odata_filter import _compose_filter
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import SecurityGroup
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized


class SecurityGroupsAPI:
    async def get_security_groups(self, offset: int = 0, limit: int = 500, **sg_kwargs):
        security_groups = []

        if limit <= 0:
            return security_groups
        if limit > 50:
            i_offset = offset
            offset = 0
            batch_limit = 40
            while len(security_groups) == offset:
                if offset + batch_limit > limit:
                    batch_limit = limit - offset
                if batch_limit > 0:
                    security_groups.extend(await self.get_security_groups(offset=offset + i_offset, limit=batch_limit, **sg_kwargs))
                if (offset + batch_limit) >= limit:
                    break
                elif len(security_groups) > offset:
                    offset = len(security_groups)
                else:
                    break
            return security_groups
        else:
            url = "/odata/api_SecurityGroups"

            match_args = dict()
            for k, v in sg_kwargs.items():
                if hasattr(SecurityGroup, k):
                    match_args[k] = v

            if self.site_uid is not None:
                match_args['ownerSiteUID'] = self.site_uid

            filter_str = _compose_filter(exact_match=match_args)
            url_query_params = "?" + filter_str
            url_query_params += "$top=" + str(limit) + "&$skip=" + str(offset)

            code, json_body = await self.gp_json_query("GET", url=(url + url_query_params))

            if code != 200:
                error_msg = GuardPointResponse.extract_error_msg(json_body)

                if code == 401:
                    raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
                elif code == 404:  # Not Found
                    raise GuardPointError(f"Security Group Not Found")
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
            security_groups = []
            for entry in json_body['value']:
                if isinstance(entry, dict):
                    sg = SecurityGroup(entry)
                    security_groups.append(sg)
            return security_groups
