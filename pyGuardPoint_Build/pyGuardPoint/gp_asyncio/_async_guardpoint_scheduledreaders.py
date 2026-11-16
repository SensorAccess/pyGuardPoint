from ..guardpoint_dataclasses import ScheduledAdditionalReader
from .._action_helpers import resolve_uid, raise_for_error, value_list, single_entity


class ScheduledAdditionalReadersAPI:
    """
    ``API_ScheduledAdditionalReaders`` - per-cardholder extra readers, valid on a weekly
    programme between two dates (on top of what their security group grants).
    """

    async def get_scheduled_additional_readers(self, cardholder=None, offset: int = 0, limit: int = 40):
        """
        List scheduled additional readers, optionally for one cardholder.

        :param cardholder: ``Cardholder`` or UID to filter by.
        :return: ``list[ScheduledAdditionalReader]``
        """
        url = f"/odata/API_ScheduledAdditionalReaders?$top={int(limit)}&$skip={int(offset)}"
        if cardholder is not None:
            url += f"&$filter=cardholderUID%20eq%20{resolve_uid(cardholder, 'cardholder')}"
        return [ScheduledAdditionalReader(x) for x in value_list(await self._gp_call("GET", url))]

    async def get_scheduled_additional_reader(self, scheduled_reader_uid):
        """Fetch one. Returns ``ScheduledAdditionalReader`` or ``None`` if not found."""
        uid = resolve_uid(scheduled_reader_uid, "scheduled additional reader")
        code, json_body = await self.gp_json_query("GET", url=f"/odata/API_ScheduledAdditionalReaders({uid})")
        if code == 404:
            return None
        raise_for_error(code, json_body)
        entity = single_entity(json_body)
        return ScheduledAdditionalReader(entity) if entity else None

    async def add_scheduled_additional_reader(self, scheduled_reader: ScheduledAdditionalReader):
        """
        Create one. Needs ``cardholderUID``, a reader (``readerUID`` or ``reader_APIKey``), a
        weekly programme (``wpuid`` or ``wP_APIKey``) and ``fromDateValid`` / ``toDateValid``.

        :return: the new record's UID.
        """
        json_body = await self._gp_call("POST", "/odata/API_ScheduledAdditionalReaders",
                                  scheduled_reader.dict(editable_only=True))
        entity = single_entity(json_body) if isinstance(json_body, dict) else None
        return entity.get('uid') if entity else None

    async def update_scheduled_additional_reader(self, scheduled_reader: ScheduledAdditionalReader):
        """
        PATCH the date window and weekly programme of a scheduled additional reader.
        Returns ``True``.

        Only ``fromDateValid``, ``toDateValid`` and ``wpuid`` are sent. The reader and cardholder
        can't be changed: including ``readerUID``/``cardholderUID`` makes the server treat the
        PATCH as a new, overlapping schedule (``Error_ScheduleAdditionalReaderOverlapOlderOne``).
        ``wP_APIKey`` is rejected on PATCH, so it is only sent when ``wpuid`` is empty.
        Delete and re-add to move a schedule to a different reader.
        """
        uid = resolve_uid(scheduled_reader, "scheduled additional reader")
        body = {k: getattr(scheduled_reader, k) for k in ('fromDateValid', 'toDateValid', 'wpuid')
                if getattr(scheduled_reader, k) not in ("", None)}
        if 'wpuid' not in body and scheduled_reader.wP_APIKey:
            body['wP_APIKey'] = scheduled_reader.wP_APIKey
        if not body:
            raise ValueError("Nothing to update - set fromDateValid, toDateValid or wpuid")
        await self._gp_call("PATCH", f"/odata/API_ScheduledAdditionalReaders({uid})", body,
                      "Scheduled Additional Reader Not Found")
        return True

    async def delete_scheduled_additional_reader(self, scheduled_reader_or_uid):
        """
        Delete a scheduled additional reader. Returns ``True``.

        The delete is queued for the controllers: a GET straight afterwards still returns the
        record, with ``status == "AskToDelete"``, until the controller confirms.
        """
        uid = resolve_uid(scheduled_reader_or_uid, "scheduled additional reader")
        await self._gp_call("DELETE", f"/odata/API_ScheduledAdditionalReaders({uid})",
                      not_found_msg="Scheduled Additional Reader Not Found")
        return True
