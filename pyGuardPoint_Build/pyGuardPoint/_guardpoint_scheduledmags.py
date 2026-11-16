import validators
from .guardpoint_utils import GuardPointResponse
from .guardpoint_dataclasses import ScheduledMag, Cardholder
from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from ._action_helpers import resolve_uid, raise_for_error, single_entity


class ScheduledMagsAPI:

    def get_scheduled_mags(self, cardholder: Cardholder = None):
        url = self.baseurl + "/odata/API_ScheduledMags"
        if cardholder:
            if not validators.uuid(cardholder.uid):
                raise ValueError(f'Malformed Cardholder UID {cardholder.uid}')
            url_query_params = f"?$filter=cardholderUid%20eq%20'{cardholder.uid}'"
        else:
            url_query_params = ""

        code, json_body = self.gp_json_query("GET", url=(url + url_query_params))

        if code != 200:
            error_msg = GuardPointResponse.extract_error_msg(json_body)

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            elif code == 404:  # Not Found
                raise GuardPointError(f"MAG Not Found")
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
        scheduled_mags = []
        for entry in json_body['value']:
            if isinstance(entry, dict):
                sm = ScheduledMag(entry)
                scheduled_mags.append(sm)
        return scheduled_mags

    def add_scheduled_mag(self, scheduled_mag: ScheduledMag):
        """
        Schedule a security group for a cardholder over a date window.

        Needs ``cardholderUID``, ``fromDateValid``, ``toDateValid`` and the group as either
        ``securityGroupAPIKey`` or ``scheduledSecurityGroupUID``.

        :return: the new scheduled MAG's UID.
        :raises GuardPointError: if the server rejects it.
        """
        json_body = self._gp_call("POST", "/odata/API_ScheduledMags", scheduled_mag.dict(editable_only=True),
                                  "Cardholder Not Found")
        entity = single_entity(json_body) if isinstance(json_body, dict) else None
        if not entity or not entity.get('uid'):
            raise GuardPointError("Badly formatted response.")
        return entity['uid']

    def get_scheduled_mag(self, scheduled_mag_uid):
        """Fetch one scheduled security group. Returns ``ScheduledMag`` or ``None`` if not found."""
        uid = resolve_uid(scheduled_mag_uid, "scheduled MAG")
        code, json_body = self.gp_json_query("GET", url=f"/odata/API_ScheduledMags({uid})")
        if code == 404:
            return None
        raise_for_error(code, json_body)
        entity = single_entity(json_body)
        return ScheduledMag(entity) if entity else None

    def update_scheduled_mag(self, scheduled_mag: ScheduledMag):
        """
        PATCH a scheduled security group. Only fields changed since it was fetched are sent
        (typically ``fromDateValid`` / ``toDateValid``). ``cardholderUID`` is always included,
        as the server requires it. Returns ``True``.
        """
        uid = resolve_uid(scheduled_mag, "scheduled MAG")
        body = scheduled_mag.dict(editable_only=True, changed_only=True)
        if scheduled_mag.cardholderUID:
            body['cardholderUID'] = scheduled_mag.cardholderUID
        self._gp_call("PATCH", f"/odata/API_ScheduledMags({uid})", body, "Scheduled MAG Not Found")
        return True

    def delete_scheduled_mag(self, scheduled_mag_or_uid):
        """
        Delete a scheduled security group. Returns ``True``.

        The delete is queued for the controllers: a GET straight afterwards still returns the
        record, with ``status == "AskToDelete"``, until the controller confirms.
        """
        uid = resolve_uid(scheduled_mag_or_uid, "scheduled MAG")
        self._gp_call("DELETE", f"/odata/API_ScheduledMags({uid})", not_found_msg="Scheduled MAG Not Found")
        return True
