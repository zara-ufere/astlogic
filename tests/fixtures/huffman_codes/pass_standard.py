words = ['AB', 'BA']
freq = {'A': 3, 'B': 2}
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
                bits = bits[len(code[sym]):]
    return out


packed = encode('ABBA')
restored = decode(packed)
print(packed, restored)
