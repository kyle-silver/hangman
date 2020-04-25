with open('words.txt', 'r') as wordfile:
    _raw = wordfile.readlines()
    words = [word.rstrip() for word in _raw]
    valid_words = [word.lower() for word in words if word.isalpha()]

with open('dictionary.txt', 'w') as dictfile:
    dictfile.writelines(f'{word}\n' for word in valid_words)

