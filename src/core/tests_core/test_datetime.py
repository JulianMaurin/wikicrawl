from wikicrawl.core.datetime import format_duration


def test_format_duration():
    assert format_duration(35) == "00:00:35"
    assert format_duration(1500) == "00:25:00"
    assert format_duration(3600) == "01:00:00"
    assert format_duration(433501) == "120:25:01"
