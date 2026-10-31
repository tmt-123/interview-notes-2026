"""有限穷举/对照验证，不依赖第三方库；不会调用外部服务。"""
from algorithms import (merge_json, max_less, rand7_from5, multiply_hex,
                        count_three_sum_less, min_unique_subsequence)
from itertools import combinations, product
from collections import Counter
from copy import deepcopy

checks = 0


def verify(condition):
    global checks
    if not condition:
        raise AssertionError(f'check {checks + 1} failed')
    checks += 1


pool = [0, 1, 2, 4, 9]
for mask in range(1 << len(pool)):
    digits = {pool[i] for i in range(len(pool)) if mask >> i & 1}
    for n in range(201):
        valid = [x for x in range(n) if all(int(c) in digits for c in str(x))]
        expected = str(max(valid)) if valid else None
        verify(max_less(n, digits) == expected)
verify(max_less(23121, {2, 4, 9}) == '22999')
verify(Counter((5*a+b) % 7 for a in range(5) for b in range(5) if 5*a+b < 21)
       == Counter({i: 3 for i in range(7)}))
stream = iter([4, 4, 0, 0])
verify(rand7_from5(lambda: next(stream)) == 0)
for a in range(128):
    for b in range(64):
        verify(multiply_hex(hex(a)[2:], hex(b)[2:]) == format(a*b, 'X'))
verify(multiply_hex('0'+'F'*150, 'aBc') == format(int('F'*150, 16)*0xABC, 'X'))
a = {'obj': {'v': 1}, 'items': [{'x': 1}], 'flag': False, 's': 'a'}
b = {'obj': {'v': 2, 'new': None}, 'items': [{'x': 2}], 'flag': True, 's': 'b'}
before_a, before_b = deepcopy(a), deepcopy(b)
out = merge_json(a, b)
verify(out == {'obj': {'v': 3, 'new': None}, 'items': [{'x': 1}, {'x': 2}],
               'flag': True, 's': 'ab'})
out['items'][0]['x'] = 9
out['obj']['new'] = 10
verify(a == before_a and b == before_b)
verify(merge_json(True, 2) == 2 and type(merge_json(True, False)) is bool)
for length in range(6):
    for values in product([-1, 0, 2], repeat=length):
        for target in [-2, 0, 3]:
            expected = sum(sum(c) < target for c in combinations(values, 3))
            verify(count_three_sum_less(values, target) == expected)
for length in range(7):
    for chars in product('abc', repeat=length):
        s = ''.join(chars)
        candidates = (''.join(s[i] for i in idx) for idx in combinations(range(len(s)), len(set(s))))
        expected = min(x for x in candidates if len(set(x)) == len(set(s)))
        verify(min_unique_subsequence(s) == expected)
print(f'PASS: {checks} deterministic algorithm checks')
