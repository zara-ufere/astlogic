# fails: At least four levels of nested if-statements
a = input('First? [Y/N]: ').strip().upper()
if a == 'Y':
    b = input('Second? [Y/N]: ').strip().upper()
    if b == 'Y':
        print('yes yes')
    else:
        print('yes no')
else:
    print('no')
