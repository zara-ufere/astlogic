# fails: One function loops from N to 1 using its parameter as the bound
def total_loop(n):
    total = 0
    for k in range(10, 0, -1):
        total += k
    return total


def total_rec(n):
    if n < 1:
        return 0
    return n + total_rec(n - 1)
