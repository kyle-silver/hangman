from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd


def in_ms(start: datetime, stop: datetime):
    dt = stop - start
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    return ms

with open('dictionary.txt', 'r') as dictfile:
    all_words = [word.rstrip() for word in dictfile.readlines()]

corpus = defaultdict(list)
for word in all_words:
    corpus[len(word)].append(word)

def getdf(words, length):
    split = {str(i): [word[i] for word in words] for i in range(length)}
    split['word'] = []
    for word in words:
        split['word'].append(word)
    return pd.DataFrame(split, dtype='string')

t0 = datetime.now()
dataframes = {i: getdf(entries, i) for i, entries in corpus.items()}
t1 = datetime.now()
print(f'created dataframe in {in_ms(t0, t1)}ms')

class Hangman:
    def __init__(self, answer: str, corpus: pd.DataFrame):
        self.df = corpus
        self.knowns = ['' for _ in range(len(answer))]
        self.known_chars = set()
        self.rejects = set()
        self.answer = answer
        self.attempts = 0
    
    def candidate_query(self):
        conditions = None
        for i, char in enumerate(self.knowns):
            col = str(i)
            if char == '':
                cond = ~self.df[col].isin(self.known_chars) & ~self.df[col].isin(self.rejects)
            else:
                cond = self.df[col].eq(char)
            conditions = conditions & cond if conditions is not None else cond
        return conditions
    
    def most_freq_remaining(self):
        # get a dataframe containing only the columns with unknown values
        known_cols = [str(i) for i, char in enumerate(self.knowns) if char != '']
        known_cols.append('word')
        remaining = self.df.drop(columns=known_cols)
        # find the most frequent letter among those columns
        value_counts = remaining.apply(pd.Series.value_counts).sum(axis=1)
        return value_counts.idxmax()
        
    
    def suggest(self) -> chr:
        '''pick the letter that eliminates the fewest options for the next round'''
        # restrict the corpus to words that fit the new criteria of knowns, positions, and rejects
        self.df = self.df[self.candidate_query()]
        # guess the character that appears in the most words in the corpus
        suggestion = self.most_freq_remaining()
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


def play(word: str, corpus: pd.DataFrame):
    start_time = datetime.now()
    game = Hangman(word, corpus)
    while game.solved() is False and game.attempts < 30:
        game.guess()
    end_time = datetime.now()
    print(f'Solved {word} in {in_ms(start_time, end_time)}ms and {game.attempts} attempts, rejects: {game.rejects}')

to_guess = corpus[9][::100]
for word in to_guess:
    play(word, dataframes[len(word)])
