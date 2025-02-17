from collections import defaultdict, Counter
from datetime import datetime, timedelta
import sys

def in_ms(start: datetime, stop: datetime):
    dt = stop - start
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    return ms

ALPHABET = set('abcdefghijklmnopqrstuvwxyz')

class Word:
    def __init__(self, word):
        self.entry = word
        self.chars = set(char for char in word)
        # self.complement = ALPHABET - self.chars

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
        '''pick the letter that eliminates the fewest options for the next round'''
        # t0 = datetime.now()
        # restrict the corpus to words that fit the new criteria of knowns, positions, and rejects
        self.corpus = [word for word in self.corpus if word.iscandidate(self.knowns, self.known_chars, self.rejects)]
        # t1 = datetime.now()
        # print(f'executed query in {in_ms(t0, t1)}')
        # letters that remain to be guessed
        remaining = ALPHABET - self.rejects - self.known_chars
        # find the number of words in the corpus that contain each remaining character
        candidates = {char: sum(1 for word in self.corpus if char in word.entry) for char in remaining}
        # guess the character that appears in the most words in the corpus
        suggestion = max(candidates, key=candidates.get, default='')
        return suggestion
    
    def update(self, guess: chr) -> None:
        if guess in self.answer:
            # update knowns with the new letter
            for i in range(len(self.answer)):
                if self.answer[i] == guess:
                    self.knowns[i] = guess
            self.known_chars.add(guess)
        else:
            self.rejects.add(guess)
    
    def guess(self) -> None:
        self.attempts += 1
        suggestion = self.suggest()
        self.update(suggestion)
        # print(f'attempt: {self.attempts}, guess: {suggestion}, knowns: {self.knowns}, rejects: {self.rejects}')
    
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


to_guess = corpus[8][::100]
for word in to_guess:
    play(word.entry, corpus[len(word)])

play('jazz', corpus[4])
