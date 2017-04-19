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

Group
Words is taken by user in groups. Each group consists several words. After
each group's recognition, the user will get a chance to review the words. At
the same time, the core logic should update the progress of task into the
memory.
'''
from collections import OrderedDict
from time import time


class ProgressStatus:
    UNKNOWN = 0
    GOOD = 1
    BAD = 2
    WANTING = 3


class CoreLogicConfig:
    max_bad = 14
    group_size = 7
    task_size = 100
    num_new_word = 50
    max_prof = 3


class CoreLogic:

    know_trans = {
        ProgressStatus.UNKNOWN: ProgressStatus.GOOD,
        ProgressStatus.BAD: ProgressStatus.WANTING,
        ProgressStatus.WANTING: ProgressStatus.GOOD,
    }

    def __init__(self,
                 wordbook,
                 mdb,
                 cmudict=None,
                 config=None):

        self._wordbook = wordbook
        self._mdb = mdb
        self._cmudict = cmudict or {}
        self._config = config or CoreLogicConfig()

        memory = self._mdb.get_memory()
        # only consider memory of words in wordbook
        self._memory = {word: prof for word, prof in memory.items()
                        if word in self._wordbook}

        # take new words in wordbook into memory if they aren't in there
        for word in self._wordbook:
            if word not in self._memory:
                self._memory[word] = 0

        # empty progress
        self._progress = OrderedDict()
        self._progress_updated = set()  # has been marked as GOOD today

    def make_task(self,
                  max_prof=None,
                  num_new_word=None,
                  task_size=None):
        # if not specified, use default value in _config
        max_prof = max_prof or self._config.max_prof
        num_new_word = num_new_word or self._config.num_new_word
        task_size = task_size or self._config.task_size

        from random import shuffle
        old_words = [word for word, prof in self._memory.items()
                     if 0 < prof < max_prof]
        new_words = [word for word, prof in self._memory.items()
                     if 0 == prof]
        shuffle(old_words)
        shuffle(new_words)

        new_words = new_words[:num_new_word]
        old_words = old_words[:(task_size-len(new_words))]
        task_words = new_words + old_words
        shuffle(task_words)

        self._progress = OrderedDict(
            (word, ProgressStatus.UNKNOWN) for word in task_words
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

    @property
    def config(self):
        return self._config

    def _update_memory(self):
        ''' Update the memory according to current progress of task, and then
            sync with mdb
            progress -> memory -> mdb
        '''
        for word, status in self.progress.items():
            if status == ProgressStatus.GOOD \
                    and word not in self._progress_updated:
                self._memory[word] += 1
                self._progress_updated.add(word)

        self._mdb.update_memory(self._memory)

    def _i_know(self, word):
        assert self.progress[word] != ProgressStatus.GOOD
        self.progress[word] = self.know_trans[self.progress[word]]
        self._mdb.log_word(word, True)

    def _i_dont_know(self, word):
        self.progress[word] = ProgressStatus.BAD
        self._mdb.log_word(word, False)

    def count_memory(self):
        ''' Count and stat the memory
        '''
        from collections import Counter
        return dict(Counter(v for _, v in self._memory.items()))

    def count_progress(self):
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

    def update_group(self, know_status):
        ''' Get the know-status from the frontend, make action, then save the
            status.
        '''
        for word, know in know_status.items():
            if know:
                self._i_know(word)
            else:
                self._i_dont_know(word)

        # update memory
        self._update_memory()

    def next_group(self):
        ''' return: [(word, test), (word, test), ... ]
        '''
        pc = self.count_progress()  # progress counter
        if pc['bad'] == pc['wanting'] == pc['unknown'] == 0:
            return [], pc

        # if there is too many bad words, focus on the bad words
        elif pc['bad'] > self._config.max_bad \
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
            if k == self._config.group_size:
                break
            kk = self._cmudict[word] if word in self._cmudict else ''
            group.append({'word': word,
                          'text': self.wordbook[word],
                          'kk': kk})  # Kenyon & Knott phonetic
        return group, pc
