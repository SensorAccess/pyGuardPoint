
from .guardpoint_dataclasses import WeeklyProgram
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class WeeklyProgramsAPI:

    def get_weekly_program(self, weekly_program_uid):
        url = self.baseurl + "/odata/API_WeeklyPrograms"
        url_query_params = f"({weekly_program_uid})"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        code, json_body = self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

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

        return WeeklyProgram(json_body['value'][0])

    def get_weekly_programs(self):
        url = self.baseurl + "/odata/API_WeeklyPrograms"

        code, json_body = self.gp_json_query("GET", url=url)

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"No WeeklyPrograms Found")
            else:
                raise GuardPointError(f"{error_msg}")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")
        if not isinstance(json_body['value'], list):
            raise GuardPointError("Badly formatted response.")

        # Compose list of inputs
        weekly_programs = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                wp = WeeklyProgram(entry)
                weekly_programs.append(wp)
        return weekly_programs
