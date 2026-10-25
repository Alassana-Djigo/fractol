import numpy as np

from explorer.cache import ByteLRU
from explorer.encoding import INTERIOR, NU_SCALE, quantize


def test_quantize_marks_interior_and_scales_the_rest():
    out = quantize(np.array([-1.0, 0.0, 3.5, 1.25], dtype=np.float32))
    assert out.dtype == np.dtype("<u2")
    assert out.tolist() == [INTERIOR, 0, 224, 80]


def test_quantize_keeps_large_values_below_the_reserved_one():
    out = quantize(np.array([500.0, 1e9], dtype=np.float32))
    assert out[0] == 500 * NU_SCALE
    assert out[1] == INTERIOR - 1


def test_lru_evicts_the_least_recently_used_over_the_byte_limit():
    cache = ByteLRU(max_bytes=10)
    cache.put("a", b"1234")
    cache.put("b", b"1234")
    assert cache.get("a") == b"1234"  # "a" passa a ser a mais recente
    cache.put("c", b"1234")  # 12 bytes > 10: sai a menos recente ("b")
    assert cache.get("b") is None
    assert cache.get("a") == b"1234"
    assert cache.get("c") == b"1234"
    assert cache.size <= 10


def test_lru_replacing_a_key_does_not_double_count_its_size():
    cache = ByteLRU(max_bytes=10)
    cache.put("a", b"123456")
    cache.put("a", b"12")
    assert cache.size == 2
    assert len(cache) == 1


def test_lru_ignores_items_bigger_than_the_whole_cache():
    cache = ByteLRU(max_bytes=4)
    cache.put("big", b"123456")
    assert cache.get("big") is None
    assert cache.size == 0
