# encoding: utf-8
''' Core logics to arrange the word flashcards

Wordbook
A wordbook contains words with their explanations.

Memory
The memory refers to the user's proficiency of words. It records the number of
times the user had recognize each word.

Progress (of task)
Every time the user starts server (more precisely, initialize the core logic),
a task is arranged. The task contains a subset of words in the wordbook.
When the task is ongoing by the user, progress is made. The progress is
depicted by assigning a ProgressStatus for each word. When a word is either
recognized or not recognized by the user, its ProgressStatus will transfer.

Group:
Words is taken by user in groups. Each group consists several words. After
each group's recognition, the user will get a chance to review the words. At
the same time, the core logic should update the progress of task into the
memory.
'''
from collections import OrderedDict


class ProgressStatus:
    UNKNOWN = 0
    GOOD = 1
    BAD = 2
    WANTING = 3


class CoreLogicConfig:
    max_bad = 14
    group_size = 7
    day_cap = 100
    day_new = 50
    max_mem = 3


class CoreLogic:

    know_trans = {
        ProgressStatus.UNKNOWN: ProgressStatus.GOOD,
        ProgressStatus.BAD: ProgressStatus.WANTING,
        ProgressStatus.WANTING: ProgressStatus.GOOD,
    }

    def __init__(self, wordbook, memory=None, config=None):
        self._wordbook = wordbook

        self.config = config or CoreLogicConfig()
        self._memory = memory or {}

        # take new words in wordbook into memory if they aren't in there
        for word in self._wordbook:
            if word not in self._memory:
                self._memory[word] = 0

        # make daily task
        from random import shuffle
        old_words = [word for word, prof in self._memory.items()
                     if 0 < prof < self.config.max_mem]
        new_words = [word for word, prof in self._memory.items()
                     if 0 == prof]
        shuffle(old_words)
        shuffle(new_words)

        day_new_words = new_words[:self.config.day_new]
        day_old_words = old_words[:(self.config.day_cap-len(day_new_words))]
        day_words = day_new_words + day_old_words
        shuffle(day_words)

        self._progress = OrderedDict(
            (word, ProgressStatus.UNKNOWN) for word in day_words
        )
        self._progress_updated = set()  # has been marked as GOOD today

    @property
    def wordbook(self):
        ''' wordbook = {word: text}
        '''
        return self._wordbook

    @property
    def memory(self):
        ''' memory = {word: proficiency}
            proficiency is number of times the word reaching GOOD
        '''
        return self._memory

    @property
    def progress(self):
        ''' progress = {word: status}
            status in ProgressStatus
        '''
        return self._progress

    def update_memory(self):
        ''' Update the memory according to current progress of task
        '''
        for word, status in self.progress.items():
            if status == ProgressStatus.GOOD \
                    and word not in self._progress_updated:
                self._memory[word] += 1
                self._progress_updated.add(word)

    def i_know(self, word):
        assert self.progress[word] != ProgressStatus.GOOD
        self.progress[word] = self.know_trans[self.progress[word]]

    def i_dont_know(self, word):
        self.progress[word] = ProgressStatus.BAD

    def _count_progress(self):
        ''' Count the number of words in each status
        '''
        from collections import Counter
        counter = Counter(v for _, v in self.progress.items())
        return {
            'unknown': counter[ProgressStatus.UNKNOWN],
            'good': counter[ProgressStatus.GOOD],
            'bad': counter[ProgressStatus.BAD],
            'wanting': counter[ProgressStatus.WANTING],
        }

    def next_group(self):
        ''' return: [(word, test), (word, test), ... ]
        '''
        pc = self._count_progress()  # progress counter
        if pc['bad'] == pc['wanting'] == pc['unknown'] == 0:
            return [], pc

        # if there is too many bad words, focus on the bad words
        elif pc['bad'] > self.config.max_bad \
                or pc['wanting'] == pc['unknown'] == 0:
            words = [word for word, status in self.progress.items()
                     if status == ProgressStatus.BAD]
        else:
            words = [word for word, status in self.progress.items()
                     if status
                     in {ProgressStatus.UNKNOWN, ProgressStatus.WANTING}]

        from random import shuffle
        shuffle(words)

        group = []
        for k, word in enumerate(words):
            if k == self.config.group_size:
                break
            group.append({'word': word, 'text': self.wordbook[word]})
        return group, pc
