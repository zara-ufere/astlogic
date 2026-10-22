# fails: The other function has an if-statement for the base and recursive cases | The recursive function calls itself and uses no loop
def first(n):
    total = 0
    for k in range(n, 0, -1):
        total += k
    return total


def second(n):
    total = 0
    k = n
    while k > 0:
        total += k
        k -= 1
    return total
