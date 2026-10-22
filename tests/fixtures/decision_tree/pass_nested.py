a = input('Heavy use? [Y/N]: ').strip().upper()
if a == 'Y':
    b = input('Outdoors? [Y/N]: ').strip().upper()
    if b == 'Y':
        c = input('Wet? [Y/N]: ').strip().upper()
        if c == 'Y':
            d = input('Salt water? [Y/N]: ').strip().upper()
            if d == 'Y':
                print('Marine grade')
            else:
                print('Sealed')
        else:
            print('Weatherproof')
    else:
        print('Indoor')
else:
    print('Light duty')
