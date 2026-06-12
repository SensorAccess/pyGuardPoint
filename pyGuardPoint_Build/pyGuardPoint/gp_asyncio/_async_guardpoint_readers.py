import validators
from .._odata_filter import _compose_filter
from ..guardpoint_utils import GuardPointResponse
from ..guardpoint_dataclasses import Reader
from ..guardpoint_error import GuardPointError, GuardPointUnauthorized


class ReadersAPI:
    async def get_readers(self, offset: int = 0, limit: int = 500, **reader_kwargs):
        readers = []

        if limit <= 0:
            return readers
        if limit > 50:
            i_offset = offset
            offset = 0
            batch_limit = 40
            while len(readers) == offset:
                if offset + batch_limit > limit:
                    batch_limit = limit - offset
                if batch_limit > 0:
                    readers.extend(await self.get_readers(offset=offset + i_offset, limit=batch_limit, **reader_kwargs))
                if (offset + batch_limit) >= limit:
                    break
                elif len(readers) > offset:
                    offset = len(readers)
                else:
                    break
            return readers
        else:
            url = "/odata/API_Readers"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            match_args = dict()
            for k, v in reader_kwargs.items():
                if hasattr(Reader, k):
                    match_args[k] = v

            if self.site_uid is not None:
                if 'ownerSiteUID' in match_args:
                    match_args['ownerSiteUID'] = self.site_uid

            filter_str = _compose_filter(exact_match=match_args)
            url_query_params = ("?" + filter_str)
            url_query_params += "$top=" + str(limit) + "&$skip=" + str(offset)

            code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

            if code != 200:
                error_msg = GuardPointResponse.extract_error_msg(json_body)

                if code == 401:
                    raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
                elif code == 404:
                    raise GuardPointError(f"Cardholder Not Found")
                else:
                    raise GuardPointError(f"{error_msg}")

            if not isinstance(json_body, dict):
                raise GuardPointError("Badly formatted response.")
            if 'value' not in json_body:
                raise GuardPointError("Badly formatted response.")
            if not isinstance(json_body['value'], list):
                raise GuardPointError("Badly formatted response.")

            readers = []
            for x in json_body['value']:
                readers.append(Reader(x))
            return readers

    async def get_reader(self, reader_uid: str):
        if not validators.uuid(reader_uid):
            raise ValueError(f"Malformed reader_uid: {reader_uid}")

        url = "/odata/API_Readers"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        url_query_params = f"({reader_uid})"

        code, json_body = await self.gp_json_query("GET", headers=headers, url=(url + url_query_params))

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
            else:
                raise GuardPointError(str(code))

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'value' not in json_body:
            raise GuardPointError("Badly formatted response.")

        return Reader(json_body['value'])

