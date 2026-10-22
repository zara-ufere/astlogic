samples = ['AAB']
counts = {'A': 2, 'B': 1}
table = {'A': '0', 'B': '10'}


def encode(msg):
    bits = ''
    for letter in msg:
        bits = bits + table[letter]
    return bits


def decode(stream):
    text = ''
    while stream != '':
        for letter, pattern in table.items():
            if stream.startswith(pattern):
                text += letter
                stream = stream[len(pattern):]
    return text


coded = encode('AAB')
plain = decode(coded)
