"""独立编写的部分算法变式参考；完整思路见仓库根目录的10-算法与手撕.md。"""
from copy import deepcopy


def merge_json(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = deepcopy(a)
        for k, value in b.items():
            out[k] = merge_json(a[k], value) if k in a else deepcopy(value)
        return out
    if isinstance(a, bool) and isinstance(b, bool):
        return a or b
    if type(a) in (int, float) and type(b) in (int, float):
        return a + b
    if isinstance(a, list) and isinstance(b, list):
        return deepcopy(a) + deepcopy(b)
    if isinstance(a, str) and isinstance(b, str):
        return a + b
    return deepcopy(b)


def max_less(n, digits):
    """数字可重复；无前导零；0可表示为'0'；无解返回None。"""
    if n < 0 or any(type(x) is not int or not 0 <= x <= 9 for x in digits):
        raise ValueError('invalid input')
    choices = sorted(set(digits), reverse=True)
    bound = str(n)

    def search(pos, tight, smaller, length):
        if pos == length:
            return '' if smaller else None
        limit = int(bound[pos]) if tight else 9
        for x in choices:
            if x > limit or (pos == 0 and length > 1 and x == 0):
                continue
            less = smaller or (tight and x < limit)
            # 一旦较小，余位直接取最大可用数字。
            if less:
                return str(x) + str(choices[0]) * (length - pos - 1)
            suffix = search(pos + 1, tight, smaller, length)
            if suffix is not None:
                return str(x) + suffix
        return None

    if not choices:
        return None
    for length in range(len(bound), 0, -1):
        if length < len(bound):
            leading = next((x for x in choices if x != 0 or length == 1), None)
            if leading is not None:
                return str(leading) + str(choices[0]) * (length - 1)
        else:
            answer = search(0, True, False, length)
            if answer is not None:
                return answer
    return None


def rand7_from5(draw):
    while True:
        x = 5 * draw() + draw()
        if x < 21:
            return x % 7


def multiply_hex(a, b):
    if not a or not b or any(c not in '0123456789abcdefABCDEF' for c in a + b):
        raise ValueError('unsigned hexadecimal digits required')
    out = [0] * (len(a) + len(b))
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            value = out[i + j + 1] + int(a[i], 16) * int(b[j], 16)
            out[i + j + 1] = value % 16
            out[i + j] += value // 16
    return ''.join('0123456789ABCDEF'[x] for x in out).lstrip('0') or '0'


def count_three_sum_less(values, target):
    a = sorted(values)
    count = 0
    for i in range(len(a) - 2):
        left, right = i + 1, len(a) - 1
        while left < right:
            if a[i] + a[left] + a[right] < target:
                count += right - left
                left += 1
            else:
                right -= 1
    return count


def min_unique_subsequence(s):
    from collections import Counter
    remaining = Counter(s)
    stack, used = [], set()
    for c in s:
        remaining[c] -= 1
        if c in used:
            continue
        while stack and stack[-1] > c and remaining[stack[-1]]:
            used.remove(stack.pop())
        stack.append(c)
        used.add(c)
    return ''.join(stack)
