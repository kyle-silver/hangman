from collections import defaultdict, Counter
from datetime import datetime, timedelta


with open('dictionary.txt', 'r') as dictfile:
    corpus = [word.rstrip() for word in dictfile.readlines()]

# words = {word: set(char for char in word) for word in corpus}

words_by_length = defaultdict(list)
for entry in corpus:
    words_by_length[len(entry)].append(entry)

print('loaded all words')

def get_candidates(knowns: [str], rejects: iter, candidates: [str]) -> list:
    known_chars = set(char for char in knowns if char != '')
    def is_candidate(word: str) -> bool:
        for char in word:
            if char in rejects:
                return False
        for i in range(len(knowns)):
            if knowns[i] == '':
                if word[i] in known_chars:
                    # has a known letter in a palce that doesn't line up with `knowns`
                    # eg knowns are ja__ but word is `java`
                    return False
                else:
                    # no known letter for that spot
                    # move on to next letter
                    continue
            if knowns[i] != word[i]:
                # has a different letter in a certain place
                return False
        # blanks notwithstanding, has the same letters in the same places
        return True

    return [word for word in candidates if is_candidate(word)]

def suggest_next(knowns: [chr], rejects: [chr], candidates: [str]) -> ((chr, int), [str]):
    known_chars = set(char for char in knowns if char != '')
    new_candidates = get_candidates(knowns, rejects, candidates)
    word_freqs = map(lambda word: Counter(word), new_candidates)
    freqs = sum(word_freqs, Counter())
    to_suggest = [(char, freq) for char, freq in dict(freqs).items() if char not in known_chars]
    return max(to_suggest, key=lambda f: f[1], default=[]), new_candidates


# freqs = map(lambda word: Counter(word), get_candidates(['r', '', 'r', '']))
# print(sum(freqs, Counter()))

# joyousness

def guess_word(word):
    knowns = ['' for _ in range(len(word))]
    rejects = []
    attempts = 0
    candidates = words_by_length[len(word)]

    while '' in knowns:
        guess, candidates = suggest_next(knowns, rejects, candidates)
        guess = guess[0]
        if guess in word:
            for i in range(len(word)):
                if word[i] == guess:
                    knowns[i] = guess
        else:
            rejects.append(guess)
        attempts += 1
    print(f'knowns: {knowns}, rejects: {rejects}, attempts: {attempts}')

start_time = datetime.now()
for entry in corpus[50000:50100:10]:
    guess_word(entry)

end_time = datetime.now()
dt = datetime.now() - start_time
ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
print(ms)
        