import validators

from ._odata_filter import _compose_filter
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import Department
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class DepartmentsAPI:
    def get_department(self, department_uid):
        if not validators.uuid(department_uid):
            raise ValueError(f"Malformed department_uid: {department_uid}")

        url = f"/odata/API_Departments({department_uid})"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        code, json_body = self.gp_json_query("GET", headers=headers, url=url)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"Department Not Found")
            else:
                raise GuardPointError(f"{error_msg}")

        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")

        value = json_body['value']
        if isinstance(value, list):
            return Department(value[0]) if value else None
        return Department(value)

    def get_departments(self, offset: int = 0, limit: int = 500, **dept_kwargs):
        departments = []

        if limit <= 0:
            return departments
        if limit > 50:
            i_offset = offset
            offset = 0
            batch_limit = 40
            while len(departments) == offset:
                if offset + batch_limit > limit:
                    batch_limit = limit - offset
                if batch_limit > 0:
                    departments.extend(self.get_departments(offset=offset + i_offset, limit=batch_limit, **dept_kwargs))
                if (offset + batch_limit) >= limit:
                    break
                elif len(departments) > offset:
                    offset = len(departments)
                else:
                    break
            return departments
        else:
            url = "/odata/API_Departments"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            match_args = dict()
            for k, v in dept_kwargs.items():
                if hasattr(Department, k):
                    match_args[k] = v

            if self.site_uid is not None:
                match_args['ownerSiteUID'] = self.site_uid

            filter_str = _compose_filter(exact_match=match_args)
            url_query_params = "?" + filter_str
            url_query_params += "$top=" + str(limit) + "&$skip=" + str(offset)

            code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

            if code != 200:
                error_msg = GuardPointResponse.extract_error_msg(json_body)

                if code == 401:
                    raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
                elif code == 404:  # Not Found
                    raise GuardPointError(f"Departments Not Found")
                else:
                    raise GuardPointError(f"{error_msg}")

            if not isinstance(json_body, dict):
                raise GuardPointError("Badly formatted response.")
            if 'value' not in json_body:
                raise GuardPointError("Badly formatted response.")
            if not isinstance(json_body['value'], list):
                raise GuardPointError("Badly formatted response.")

            departments = []
            for x in json_body['value']:
                departments.append(Department(x))
            return departments
