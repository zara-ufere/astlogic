def total_loop(n):
    if n < 1:
        return 0
    total = 0
    for k in range(n, 0, -1):
        total += k
    return total


def total_rec(n):
    if n < 1:
        return 0
    return n + total_rec(n - 1)
