''' Core logits
'''


class MemoryStatus:
    UNKNOWN = 0
    GOOD = 1
    BAD = 2
    WANTING = 3


class Config:
    max_bad = 14
    group_size = 7


class CoreLogit:
    @property
    def wordlist(self):
        ''' wordlist: {word: text}
        '''
        return self._wordlist

    @property
    def memory(self):
        ''' memory: {word: proficiency}
        '''
        if not hasattr(self, '_memory'):
            self._memory = dict((word, 0) for word in self.wordlist)
        return self._memory

    @property
    def progress(self):
        ''' progress: {word: status}
        '''
        from collections import OrderedDict
        if not hasattr(self, '_progress'):
            self._progress = OrderedDict(
                (word, MemoryStatus.UNKNOWN) for word in self.wordlist
            )
        return self._progress

    def update_memory(self):
        if not hasattr(self, '_updated'):
            self._updated = set()
        for word, status in self.progress.items():
            if status == MemoryStatus.GOOD and word not in self._updated:
                self.memory[word] += 1
                self._updated.add(word)

    def i_know(self, word):
        assert self.progress[word] != MemoryStatus.GOOD
        if self.progress[word] == MemoryStatus.UNKNOWN:
            self.progress[word] = MemoryStatus.GOOD
        elif self.progress[word] == MemoryStatus.BAD:
            self.progress[word] = MemoryStatus.WANTING
        elif self.progress[word] == MemoryStatus.WANTING:
            self.progress[word] = MemoryStatus.GOOD

    def i_dont_know(self, word):
        self.progress[word] = MemoryStatus.BAD

    def count_progress(self):
        ''' Count the number of words in each status
        '''
        from collections import Counter
        counter = Counter(v for _, v in self.progress.items())
        return {
            'unknown': counter[MemoryStatus.UNKNOWN],
            'good': counter[MemoryStatus.GOOD],
            'bad': counter[MemoryStatus.BAD],
            'wanting': counter[MemoryStatus.WANTING],
        }

    def next_group(self):
        ''' return: [(word, test), (word, test), ... ]
        '''
        pc = self.count_progress()
        if pc['bad'] == pc['wanting'] == pc['unknown'] == 0:
            return []

        # if there is too many bad words, focus on the bad words
        elif pc['bad'] > self.config.max_bad or \
                pc['wanting'] == pc['unknown'] == 0:
            words = (word for word, status in self.progress
                     if status == MemoryStatus.BAD)
        else:
            words = (word for word, status in self.progress
                     if status in {MemoryStatus.UNKNOWN, MemoryStatus.WANTING})

        group = []
        for k, word in enumerate(words):
            if k == self.config.group_size:
                break
            group.append((word, self.wordlist[word]))
        return group
