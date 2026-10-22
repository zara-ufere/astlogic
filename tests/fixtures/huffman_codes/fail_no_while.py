# fails: decode nests while > for > if
words = ['AB']
freq = {'A': 1, 'B': 1}
code = {'A': '0', 'B': '1'}


def encode(text):
    out = ''
    for ch in text:
        out += code[ch]
    return out


def decode(bits):
    out = ''
    for b in bits:
        for sym in code.keys():
            if code[sym] == b:
                out += sym
    return out


packed = encode('AB')
result = decode(packed)
