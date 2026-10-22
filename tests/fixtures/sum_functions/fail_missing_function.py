# fails: Two functions are defined | The other function has an if-statement for the base and recursive cases | The recursive function calls itself and uses no loop
def only_one(n):
    total = 0
    for k in range(n, 0, -1):
        total += k
    return total
