from wikicrawl.core.utils import chunks


def test_chunks():
    assert list(chunks(["A", "B", "C"], 1)) == [["A"], ["B"], ["C"]]
    assert list(chunks(["A", "B", "C"], 2)) == [["A", "B"], ["C"]]
    assert list(chunks(["A", "B", "C"], 5)) == [["A", "B", "C"]]
