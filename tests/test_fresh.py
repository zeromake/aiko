from aiko.utils import fresh, HEADER_TYPE


def test_not_non_conditional() -> None:
    req: HEADER_TYPE = {}
    res: HEADER_TYPE = {}
    assert not fresh(req, res)


def test_etags_match() -> None:
    req: HEADER_TYPE = {"if-none-match": '"foo"'}
    res: HEADER_TYPE = {"ETag": '"foo"'}
    assert fresh(req, res)


def test_etags_mismatch() -> None:
    req: HEADER_TYPE = {"if-none-match": '"bar"'}
    res: HEADER_TYPE = {"etag": '"foo"'}
    assert not fresh(req, res)


def test_etag_least_one_matches() -> None:
    req: HEADER_TYPE = {"if-none-match": '"bar" , "foo"'}
    res: HEADER_TYPE = {"ETag": '"foo"'}
    assert fresh(req, res)


def test_etag_is_missing() -> None:
    req: HEADER_TYPE = {"if-none-match": '"bar" , "foo"'}
    res: HEADER_TYPE = {}
    assert not fresh(req, res)


def test_etag_exact() -> None:
    req: HEADER_TYPE = {"if-none-match": 'W/"foo"'}
    res: HEADER_TYPE = {"etag": 'W/"foo"'}
    assert fresh(req, res)


def test_etag_strong() -> None:
    req: HEADER_TYPE = {"if-none-match": 'W/"foo"'}
    res: HEADER_TYPE = {"etag": '"foo"'}
    assert fresh(req, res)


def test_etag_re_strong() -> None:
    req: HEADER_TYPE = {"if-none-match": '"foo"'}
    res: HEADER_TYPE = {"etag": 'W/"foo"'}
    assert fresh(req, res)


def test_none_match_not_macth() -> None:
    req: HEADER_TYPE = {"if-none-match": '*'}
    res: HEADER_TYPE = {"etag": '"bor"'}
    assert fresh(req, res)

    req = {"if-none-match": '* , "foo"'}
    res = {"etag": '"bor"'}
    assert not fresh(req, res)


def test_if_modified_since() -> None:
    # modified since the date
    req: HEADER_TYPE = {"if-modified-since": 'Sat, 01 Jan 2000 00:00:00 GMT'}
    res: HEADER_TYPE = {"last-modified": 'Sat, 01 Jan 2000 01:00:00 GMT'}
    assert not fresh(req, res)
    # unmodified since the date
    req = {"if-modified-since": 'Sat, 01 Jan 2000 01:00:00 GMT'}
    res = {"Last-Modified": 'Sat, 01 Jan 2000 00:00:00 GMT'}
    assert fresh(req, res)
    # Last-Modified is missing
    req = {"if-modified-since": 'Sat, 01 Jan 2000 00:00:00 GMT'}
    res = {}
    assert not fresh(req, res)
    # invalid If-Modified-Since date
    req = {'if-modified-since': 'foo'}
    res = {'last-modified': 'Sat, 01 Jan 2000 00:00:00 GMT'}
    assert not fresh(req, res)
    # invalid Last-Modified date
    req = {'if-modified-since': 'Sat, 01 Jan 2000 00:00:00 GMT'}
    res = {'last-modified': 'foo'}
    assert not fresh(req, res)


def test_modified_and_if_none_match() -> None:
    # both match
    req: HEADER_TYPE = {
        'if-none-match': '"foo"',
        'if-modified-since': 'Sat, 01 Jan 2000 01:00:00 GMT',
    }
    res: HEADER_TYPE = {
        'etag': '"foo"',
        'last-modified': 'Sat, 01 Jan 2000 00:00:00 GMT',
    }
    assert fresh(req, res)
    # only ETag matches
    req = {
        'if-none-match': '"foo"',
        'if-modified-since': 'Sat, 01 Jan 2000 00:00:00 GMT',
    }
    res = {
        'etag': '"foo"',
        'last-modified': 'Sat, 01 Jan 2000 01:00:00 GMT',
    }
    assert not fresh(req, res)
    # only Last-Modified matches
    req = {
        'if-none-match': '"foo"',
        'if-modified-since': 'Sat, 01 Jan 2000 01:00:00 GMT',
    }
    res = {
        'etag': '"bar"',
        'last-modified': 'Sat, 01 Jan 2000 00:00:00 GMT',
    }
    assert not fresh(req, res)
    # none match
    req = {
        'if-none-match': '"foo"',
        'if-modified-since': 'Sat, 01 Jan 2000 01:00:00 GMT',
    }
    res = {
        'etag': '"bar"',
        'last-modified': 'Sat, 01 Jan 2000 00:00:00 GMT',
    }
    assert not fresh(req, res)


def test_no_cache() -> None:
    req: HEADER_TYPE = {'cache-control': ' no-cache'}
    res: HEADER_TYPE = {}
    assert not fresh(req, res)
    # ETags match
    req = {'cache-control': ' no-cache', 'if-none-match': '"foo"'}
    res = {'etag': '"foo"'}
    assert not fresh(req, res)
    # more cache-control'
    req = {'cache-control': [' no-cache', 'test'], 'if-none-match': '"foo"'}
    res = {'etag': '"foo"'}
    assert not fresh(req, res)
    # unmodified since the date
    req = {
        'cache-control': ' no-cache',
        'if-modified-since': 'Sat, 01 Jan 2000 01:00:00 GMT',
    }
    res = {
        'last-modified': 'Sat, 01 Jan 2000 00:00:00 GMT',
    }
    assert not fresh(req, res)
