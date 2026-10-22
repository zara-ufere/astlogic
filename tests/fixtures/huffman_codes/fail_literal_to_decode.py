# fails: The result of encode is passed directly to decode
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
    while len(bits) > 0:
        for sym in code.keys():
            if bits.startswith(code[sym]):
                out += sym
                bits = bits[1:]
    return out


packed = encode('AB')
result = decode('01')
