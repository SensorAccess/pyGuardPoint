from datetime import datetime, timezone

from .guardpoint_dataclasses import CardholderOrderBy

_MIN_ORDER_DATE = datetime.min.replace(tzinfo=timezone.utc)


def _parse_order_date(value):
    """Parse an OData ISO datetime string for client-side ordering.
    Missing/unparseable values sort last on DESC, matching the server's NULLS-LAST behaviour."""
    if not value:
        return _MIN_ORDER_DATE
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return _MIN_ORDER_DATE


def _cardholder_type_name(ch):
    return ch.cardholderType.typeName if ch.cardholderType else None


def _security_group_name(ch):
    return ch.securityGroup.name if ch.securityGroup else None


# CardholderOrderBy -> (OData orderby path, is_date, descending, value_getter)
_ORDER_BY_FIELDS = {
    CardholderOrderBy.fromDateValid_DESC: ('fromDateValid', True, True, lambda ch: getattr(ch, 'fromDateValid', None)),
    CardholderOrderBy.fromDateValid_ASC: ('fromDateValid', True, False, lambda ch: getattr(ch, 'fromDateValid', None)),
    CardholderOrderBy.lastPassDate_DESC: ('lastPassDate', True, True, lambda ch: getattr(ch, 'lastPassDate', None)),
    CardholderOrderBy.firstName_ASC: ('firstName', False, False, lambda ch: getattr(ch, 'firstName', None)),
    CardholderOrderBy.firstName_DESC: ('firstName', False, True, lambda ch: getattr(ch, 'firstName', None)),
    CardholderOrderBy.lastName_ASC: ('lastName', False, False, lambda ch: getattr(ch, 'lastName', None)),
    CardholderOrderBy.lastName_DESC: ('lastName', False, True, lambda ch: getattr(ch, 'lastName', None)),
    CardholderOrderBy.toValidDate_ASC: ('toDateValid', True, False, lambda ch: getattr(ch, 'toDateValid', None)),
    CardholderOrderBy.toValidDate_DESC: ('toDateValid', True, True, lambda ch: getattr(ch, 'toDateValid', None)),
    CardholderOrderBy.Validated_ASC: ('status', False, False, lambda ch: getattr(ch, 'status', None)),
    CardholderOrderBy.Validated_DESC: ('status', False, True, lambda ch: getattr(ch, 'status', None)),
    CardholderOrderBy.CardholderType_ASC: ('cardholderType/typeName', False, False, _cardholder_type_name),
    CardholderOrderBy.CardholderType_DESC: ('cardholderType/typeName', False, True, _cardholder_type_name),
    CardholderOrderBy.SecurityGroup_ASC: ('securityGroup/name', False, False, _security_group_name),
    CardholderOrderBy.SecurityGroup_DESC: ('securityGroup/name', False, True, _security_group_name),
}


def orderby_query_param(cardholder_orderby):
    """Build the `$orderby=...&` OData query fragment for the given CardholderOrderBy."""
    field, _, descending, _ = _ORDER_BY_FIELDS[cardholder_orderby]
    direction = 'desc' if descending else 'asc'
    return f"$orderby={field}%20{direction}&"


def sort_combined(combined, cardholder_orderby):
    """Client-side re-sort used after re-merging per-area result sets (see
    `_split_get_card_holders_query`). Missing/empty order-field values always sort
    last, regardless of direction, matching the server's NULLS-LAST behaviour."""
    _, is_date, descending, get_value = _ORDER_BY_FIELDS[cardholder_orderby]

    if is_date:
        combined.sort(key=lambda ch: (_parse_order_date(get_value(ch)), ch.uid), reverse=descending)
        return combined

    with_value = [ch for ch in combined if get_value(ch)]
    without_value = [ch for ch in combined if not get_value(ch)]
    with_value.sort(key=lambda ch: (get_value(ch).lower(), ch.uid), reverse=descending)
    without_value.sort(key=lambda ch: ch.uid)
    return with_value + without_value
