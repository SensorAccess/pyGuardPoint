from .guardpoint_dataclasses import SecurityGroup
from .guardpoint_error import GuardPointError


class SecurityGroupsAPI:
    def get_security_groups(self):
        url = self.baseurl + "/odata/api_SecurityGroups"
        # url_query_params = "?$select=uid,name&$filter=name%20ne%20'Anytime%20Anywhere'"
        url_query_params = ""
        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
            raise GuardPointError(str(code))

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