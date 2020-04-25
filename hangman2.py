from collections import defaultdict, Counter
from datetime import datetime, timedelta
import sys

def in_ms(start: datetime, stop: datetime):
    dt = stop - start
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    return ms


class Word:
    def __init__(self, word):
        self.entry = word
        self.chars = set(char for char in word)
        self.freqs = Counter(word)

    def __contains__(self, char):
        return char in self.chars

    def __len__(self):
        return len(self.entry)

    def iscandidate(self, knowns: [chr], known_chars: set, rejects: set) -> bool:
        if known_chars.issubset(self.chars) == False:
            return False
        if rejects.isdisjoint(self.chars) == False:
            return False
        for i in range(len(knowns)):
            if knowns[i] == '':
                if self.entry[i] in known_chars:
                    return False
                continue
            if knowns[i] != self.entry[i]:
                return False
        return True

class Hangman:
    def __init__(self, answer: str, corpus: [Word]):
        self.corpus = corpus
        self.knowns = ['' for _ in range(len(answer))]
        self.known_chars = set()
        self.rejects = set()
        self.answer = answer
        self.attempts = 0
    
    def suggest(self) -> chr:
        '''suggestions are based on which letter is most common in remaining words'''
        # restrict the corpus to words that fit the new criteria of knowns, positions, and rejects
        self.corpus = [word for word in self.corpus if word.iscandidate(self.knowns, self.known_chars, self.rejects)]
        # calculate character frequencies across all corpus members
        freqs = sum((word.freqs for word in self.corpus), Counter())
        # eliminate characters that already appear in the word from the count
        to_suggest = [(char, freq) for char,freq in dict(freqs).items() if char not in self.known_chars]
        # get the most common remaining character
        suggestion = max(to_suggest, key=lambda f: f[1], default=('', 0))
        return suggestion[0]
    
    def guess(self) -> None:
        self.attempts += 1
        suggestion = self.suggest()
        if suggestion in self.answer:
            for i in range(len(self.answer)):
                if self.answer[i] == suggestion:
                    self.knowns[i] = suggestion
            self.known_chars.add(suggestion)
        else:
            self.rejects.add(suggestion)
        print(f'attempt: {self.attempts}, guess: {suggestion}, knowns: {self.knowns}, rejects: {self.rejects}')
    
    def solved(self) -> bool:
        return '' not in self.knowns
    

def play(word: str, corpus: [Word]):
    start_time = datetime.now()
    game = Hangman(word, corpus)
    while game.solved() is False and game.attempts < 30:
        game.guess()
    end_time = datetime.now()
    print(f'Solved {word} in {in_ms(start_time, end_time)}ms and {game.attempts} attempts, rejects: {game.rejects}')


# load all words into memory and do some preprocessing
start_time = datetime.now()
with open('dictionary.txt', 'r') as dictfile:
    all_words = [Word(word.rstrip()) for word in dictfile.readlines()]
end_time = datetime.now()
print(f'{len(all_words)} Word objects created in {in_ms(start_time, end_time)}ms ({sys.getsizeof(all_words)} bytes)')

start_time = datetime.now()
corpus = defaultdict(list)
for word in all_words:
    corpus[len(word)].append(word)
end_time = datetime.now()
print(f'Separated words by length {in_ms(start_time, end_time)}ms ({sys.getsizeof(corpus)} bytes)')


# to_guess = corpus[4][::1000]
# for word in to_guess:
#     play(word.entry, corpus[len(word)])

play('jazz', corpus[4])