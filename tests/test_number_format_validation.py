"""Number-format validation (issue #13): unknown tokens must not pass through
verbatim as a formatCode (which renders garbage). They are rejected with a
did-you-mean, while aliases and real formatCodes keep working."""
import warnings

import pandas as pd
import pytest

from ablechart import validate_spec
from ablechart.spec import _normalize_number_format, supported_number_format_tokens


def test_known_aliases_resolve():
    assert _normalize_number_format("percent") == "0%"
    assert _normalize_number_format("times") == '0"x"'
    assert _normalize_number_format("int") == "#,##0"
    assert _normalize_number_format("百分比") == "0%"


def test_raw_format_codes_pass_through():
    for code in ("0", "0.0%", "#,##0", "yyyy-mm-dd", '"¥"0" bn"', '0"%"'):
        assert _normalize_number_format(code) == code


def test_unknown_token_is_rejected_not_passed_through():
    errs = []
    # the bug: "number" used to be returned verbatim -> garbled axis
    assert _normalize_number_format("number", errors=errs) is None
    assert len(errs) == 1
    assert "number" in errs[0]


def test_unknown_token_without_errors_list_warns():
    with pytest.warns(UserWarning, match="无法识别数字格式"):
        assert _normalize_number_format("definitely-not-a-format") is None


def test_did_you_mean_suggests_close_alias():
    errs = []
    _normalize_number_format("percnt", errors=errs)
    assert "percent" in errs[0]


def test_supported_tokens_listed():
    toks = supported_number_format_tokens()
    assert "percent" in toks and "times" in toks and "currency" in toks


def test_validate_spec_flags_garbage_format():
    df = pd.DataFrame({"Metric": ["A", "B"], "Low": [1.0, 2.0], "High": [3.0, 4.0]})
    result = validate_spec(
        {"chart": "range", "low": "Low", "high": "High", "format": "number"}, df
    )
    joined = " ".join(result.get("errors", []))
    assert "format" in joined and "number" in joined
