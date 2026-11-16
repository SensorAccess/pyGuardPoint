"""Unit tests for the OData $filter query builder (_odata_filter.py).

These exercise pure string-building logic against `_compose_filter` directly
and do not require a live GuardPoint server.
"""

from pyGuardPoint_Build.pyGuardPoint._odata_filter import _compose_filter
from pyGuardPoint_Build.pyGuardPoint.guardpoint_dataclasses import Area


def _decode(filter_str):
    """Undo the %20 escaping used throughout _compose_filter, for readability."""
    return filter_str.replace('%20', ' ')


class TestSearchMatchAllDefault:
    """search_match_all=False (the default) - any word matching any field is enough."""

    def test_no_and_between_words(self):
        decoded = _decode(_compose_filter(search_words="John Smith"))
        assert " and " not in decoded

    def test_every_word_field_combination_present(self):
        decoded = _decode(_compose_filter(search_words="John Smith"))
        for field in ("firstName", "lastName",
                      "CardholderPersonalDetail/company", "CardholderPersonalDetail/email"):
            for word in ("John", "Smith"):
                assert f"contains({field},'{word}')" in decoded


class TestSearchMatchAllEnabled:
    """search_match_all=True - every word must match somewhere (any field)."""

    def test_words_are_anded_together(self):
        decoded = _decode(_compose_filter(search_words="John Smith", search_match_all=True))
        # One AND joining the "John in any field" group to the "Smith in any field" group
        assert decoded.count(" and ") == 1

    def test_fields_within_a_word_group_are_ored(self):
        decoded = _decode(_compose_filter(search_words="John Smith", search_match_all=True))
        for field in ("firstName", "lastName",
                      "CardholderPersonalDetail/company", "CardholderPersonalDetail/email"):
            assert f"contains({field},'John')" in decoded
            assert f"contains({field},'Smith')" in decoded

    def test_single_word_has_no_and(self):
        decoded = _decode(_compose_filter(search_words="John", search_match_all=True))
        assert " and " not in decoded
        assert "contains(firstName,'John')" in decoded

    def test_respects_five_word_cap(self):
        decoded = _decode(_compose_filter(search_words="a b c d e f g", search_match_all=True))
        # Only the first 5 words become AND-groups: 4 ANDs joining 5 groups
        assert decoded.count(" and ") == 4
        assert "'f'" not in decoded
        assert "'g'" not in decoded

    def test_escapes_single_quotes(self):
        filter_str = _compose_filter(search_words="O'Brien", search_match_all=True)
        assert "O''Brien" in filter_str

    def test_no_search_words_produces_no_filter(self):
        assert _compose_filter(search_words=None, search_match_all=True) == ""

    def test_combines_with_other_filter_clauses(self):
        area = Area({'uid': '00000000-0000-0000-0000-100000000001', 'area': 'Offsite'})
        decoded = _decode(_compose_filter(search_words="John Smith", search_match_all=True, areas=area))
        assert "insideAreaUID eq 00000000-0000-0000-0000-100000000001" in decoded
        # 1 AND inside the search clause (John and Smith) + 1 AND joining search to areas
        assert decoded.count(" and ") == 2
