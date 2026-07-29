import xxhash


def test_xxh3_128_is_available():
    first = xxhash.xxh3_128(b"leoclaw").digest()
    second = xxhash.xxh3_128(b"leoclaw").digest()

    assert first == second
    assert len(first) == 16
