"""
Transport-independent helpers shared by the sync (``_guardpoint_*.py``) and async
(``gp_asyncio/_async_guardpoint_*.py``) API mixins.

Nothing in here performs I/O, so both clients can build request bodies and interpret
responses identically - only the ``gp_json_query`` call differs between them.
"""
import json
from datetime import datetime, timezone
from typing import Optional

import validators

from .guardpoint_utils import GuardPointResponse
from .guardpoint_error import GuardPointError, GuardPointUnauthorized

JSON_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}


def json_headers():
    """Fresh copy - ``_query`` mutates the dict it is given (adds Authorization)."""
    return dict(JSON_HEADERS)


def resolve_uid(obj_or_uid, what: str = "object") -> Optional[str]:
    """Accept a dataclass with a ``uid`` attribute, a uid string, or None."""
    if obj_or_uid is None:
        return None
    uid = getattr(obj_or_uid, 'uid', obj_or_uid)
    if not isinstance(uid, str) or not validators.uuid(uid):
        raise ValueError(f"Malformed {what} UID: {uid}")
    return uid


def uid_or_api_key_body(obj_or_uid=None, api_key: Optional[str] = None, what: str = "object") -> dict:
    """Body for the GP10 actions that identify a target by either ``uid`` or ``apiKey``."""
    uid = resolve_uid(obj_or_uid, what)
    if (uid is None) == (api_key is None):
        raise ValueError(f"Specify exactly one of a {what} (or its UID) or api_key")
    return {'uid': uid} if uid is not None else {'apiKey': api_key}


def uids_or_api_keys_body(objs_or_uids=None, api_keys=None, what: str = "relay") -> dict:
    """Body for the multi-target output actions (``uids`` and/or ``apiKeys`` lists)."""
    body = {}
    if objs_or_uids is not None:
        if not isinstance(objs_or_uids, (list, tuple, set)):
            objs_or_uids = [objs_or_uids]
        body['uids'] = [resolve_uid(o, what) for o in objs_or_uids]
    if api_keys is not None:
        if isinstance(api_keys, str):
            api_keys = [api_keys]
        body['apiKeys'] = list(api_keys)
    if not body.get('uids') and not body.get('apiKeys'):
        raise ValueError(f"Specify at least one {what} (or UID) or api_key")
    return body


def raise_for_error(code: int, json_body, not_found_msg: str = "Not Found", ok_codes=(200, 201, 204)):
    """
    Raise the library's standard exceptions for a failed response.

    Besides the HTTP status, GP10 action endpoints sometimes answer 200 with an
    ``ACS.API.ResponseObject`` whose ``success`` is false - that is treated as a failure too.
    """
    if code in ok_codes:
        if isinstance(json_body, dict) and json_body.get('success') is False:
            raise GuardPointError(GuardPointResponse.extract_error_msg(json_body) or "Request failed")
        return

    error_msg = GuardPointResponse.extract_error_msg(json_body)
    if isinstance(error_msg, dict):
        # Some actions answer {"error": {"code": "400", "message": "..."}}
        error_msg = error_msg.get('message') or str(error_msg)
    if code == 401:
        raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
    if code == 404:
        raise GuardPointError(not_found_msg if not error_msg or error_msg == "NotFound" else error_msg)
    raise GuardPointError(error_msg or f"HTTP {code}")


def value_list(json_body) -> list:
    """Return the OData ``value`` list, raising if the response isn't shaped that way."""
    if not isinstance(json_body, dict) or not isinstance(json_body.get('value'), list):
        raise GuardPointError("Badly formatted response.")
    return [v for v in json_body['value'] if isinstance(v, dict)]


def single_entity(json_body) -> Optional[dict]:
    """
    Single-entity GETs come back either wrapped (``{"value": [ {...} ]}``) or bare
    (``{"@odata.context": ..., "uid": ...}``) depending on the entity set. Accept both.
    """
    if not isinstance(json_body, dict):
        raise GuardPointError("Badly formatted response.")
    if 'value' in json_body:
        value = json_body['value']
        if isinstance(value, list):
            return value[0] if value else None
        if isinstance(value, dict):
            return value
        raise GuardPointError("Badly formatted response.")
    return {k: v for k, v in json_body.items() if not k.startswith('@odata')}


def parse_options(json_body) -> dict:
    """
    ``GetOptionsByKeys`` / ``GetLiteOptions`` are declared as returning a dictionary, but the
    server actually returns ``{"value": "<JSON text>"}``. Handle that and a real dict.
    """
    if not isinstance(json_body, dict):
        raise GuardPointError("Badly formatted response.")
    value = json_body.get('value', json_body)
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            raise GuardPointError("Badly formatted response.")
    if not isinstance(value, dict):
        raise GuardPointError("Badly formatted response.")
    return {k: v for k, v in value.items() if not k.startswith('@odata')}


def parse_string_list(json_body) -> list:
    """``List_1OfString`` results - the server returns ``{"stringValues": [...]}``."""
    if json_body is None:
        return []
    if isinstance(json_body, list):
        return json_body
    if isinstance(json_body, dict):
        for key in ('stringValues', 'value'):
            if isinstance(json_body.get(key), list):
                return json_body[key]
    raise GuardPointError("Badly formatted response.")


def parse_output_result(json_body) -> dict:
    """
    The output actions return ``Dictionary_2OfGuid_String`` - a per-relay status map.
    Normalise to ``{relay_uid: message}``; an empty dict means every relay succeeded
    (or the server sent no detail).
    """
    if not isinstance(json_body, dict):
        return {}
    keys, values = json_body.get('keys'), json_body.get('values')
    if isinstance(keys, list):
        values = values if isinstance(values, list) else [None] * len(keys)
        return dict(zip(keys, values))
    result = {}
    for k, v in json_body.items():
        if k.startswith('@odata'):
            continue
        if isinstance(v, dict) and 'item1' in v:
            v = GuardPointResponse.extract_error_msg(v['item1']) or v.get('item2')
        result[k] = v
    return result


def output_error_msg(json_body) -> str:
    """Pull a readable error out of a failed output action (per-relay errors are nested)."""
    msgs = []
    if isinstance(json_body, dict):
        for k, v in json_body.items():
            if validators.uuid(k) and isinstance(v, dict) and 'item1' in v:
                msg = GuardPointResponse.extract_error_msg(v['item1'])
                if msg:
                    msgs.append(f"{k}: {msg}")
    return "; ".join(msgs) or GuardPointResponse.extract_error_msg(json_body)


def odata_datetime(value) -> str:
    """
    Format a ``datetime`` (or ISO-8601 string) as an OData ``DateTimeOffset`` literal for use
    in a URL ``$filter``. Naive datetimes are treated as UTC. ``+`` is percent-encoded.
    """
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Not an ISO-8601 date/time: {value}")
    if not isinstance(value, datetime):
        raise ValueError(f"Expected datetime or ISO-8601 string, got {type(value).__name__}")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    if value.utcoffset().total_seconds() == 0:
        text = value.strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        text = value.isoformat(timespec='seconds')
    return text.replace('+', '%2B')


def date_range_phrases(since=None, until=None, field: str = 'dateTime') -> list:
    """OData filter phrases for an inclusive ``since`` / exclusive ``until`` window."""
    phrases = []
    if since is not None:
        phrases.append(f"({field}%20ge%20{odata_datetime(since)})")
    if until is not None:
        phrases.append(f"({field}%20lt%20{odata_datetime(until)})")
    return phrases
