
from .guardpoint_dataclasses import Input
from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized


class InputsAPI:

    def get_input(self, relay_uid):
        url = self.baseurl + "/odata/API_Inputs"
        url_query_params = f"({relay_uid})"
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

        return Input(json_body['value'][0])

    def get_inputs(self, offset: int = 0, limit: int = 500):
        """Retrieve Inputs, paginating like get_readers().

        The server silently truncates an unpaginated OData query at 50 rows, so the
        defaults page through in batches rather than issuing one bare request.
        """
        if limit <= 0:
            return []
        if limit > 50:
            inputs = []
            i_offset = offset
            offset = 0
            batch_limit = 40
            while len(inputs) == offset:
                if offset + batch_limit > limit:
                    batch_limit = limit - offset
                if batch_limit > 0:
                    inputs.extend(self.get_inputs(offset=offset + i_offset, limit=batch_limit))
                if (offset + batch_limit) >= limit:
                    break
                elif len(inputs) > offset:
                    offset = len(inputs)
                else:
                    break
            return inputs

        url = self.baseurl + "/odata/API_Inputs"
        url_query_params = "?$top=" + str(limit) + "&$skip=" + str(offset)

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"No Inputs Found")
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
        inputs = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                input = Input(entry)
                inputs.append(input)
        return inputs
