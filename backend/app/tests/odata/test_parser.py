from app.odata.filter_parser import parse_odata_filter
from functools import partial


def base_test(inp, out):
    assert parse_odata_filter(inp) == out


test_equals = partial(base_test, "name eq 'Antti'", "name = 'Antti'")

test_number = partial(base_test, "age eq 10", "age = 10")

test_eq_null = partial(base_test, "age eq null", "age is null")
test_not_eq = partial(base_test, "not (name eq 'Antti')", "not name = 'Antti'")

test_lt = partial(base_test, "age lt 50", "age < 50")
test_le = partial(base_test, "age le 50", "age <= 50")
test_gt = partial(base_test, "age gt 50", "age > 50")
test_ge = partial(base_test, "age ge 50", "age >= 50")

test_startswith = partial(base_test, "name startswith 'Ant'", "name ilike 'Ant%'")
test_endswith = partial(base_test, "name endswith 'Ant'", "name ilike '%Ant'")
test_contains = partial(base_test, "name contains 'Ant'", "name ilike '%Ant%'")

test_empty = partial(base_test, "", "")
