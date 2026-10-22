# fails: Every if-statement comes after a user input
mode = 'Y'
if mode == 'Y':
    b = input('Second? [Y/N]: ').strip().upper()
    if b == 'Y':
        c = input('Third? [Y/N]: ').strip().upper()
        if c == 'Y':
            d = input('Fourth? [Y/N]: ').strip().upper()
            if d == 'Y':
                print('a')
            else:
                print('b')
        else:
            print('c')
    else:
        print('d')
else:
    print('e')
