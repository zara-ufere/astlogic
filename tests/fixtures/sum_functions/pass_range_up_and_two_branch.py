def add_up(limit):
    result = 0
    for step in range(1, limit + 1):
        result = result + step
    return result


def add_down(limit):
    if limit < 1:
        return 0
    else:
        return limit + add_down(limit - 1)


if __name__ == "__main__":
    print(add_up(5), add_down(5))
