# fails: Three globals are defined: one list and two dicts
words = ['AB']
code = {'A': '0', 'B': '1'}


def encode(text):
    out = ''
    for ch in text:
        out += code[ch]
    return out


def decode(bits):
    out = ''
    while len(bits) > 0:
        for sym in code.keys():
            if bits.startswith(code[sym]):
                out += sym
                bits = bits[1:]
    return out


packed = encode('AB')
result = decode(packed)
