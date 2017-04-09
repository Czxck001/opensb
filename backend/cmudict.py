'''
CMUDict: a phonetic library of English
http://www.speech.cs.cmu.edu/cgi-bin/cmudict
'''


a2kk = {
    'AA': 'ɑ',
    'AE': 'æ',
    'AH1': 'ʌ',
    'AH': 'ə',
    'AO': 'ɔ',
    'AW': 'aʊ',
    'AX': 'ə',
    'AXR': 'ɚ',
    'AY': 'aɪ',
    'B': 'b',
    'CH': 'tʃ',
    'D': 'd',
    'DH': 'ð',
    'DX': 'ɾ',
    'EH': 'ɛ',
    'EL': 'ɫ̩',
    'EM': 'm̩',
    'EN': 'n̩',
    'ENG': 'ŋ̍',
    'ER': 'ɝ',
    'EY': 'e',
    'F': 'f',
    'G': 'ɡ',
    'HH': 'h',
    'IH': 'ɪ',
    'IY': 'i',
    'JH': 'dʒ',
    'K': 'k',
    'L': 'ɫ',
    'M': 'm',
    'N': 'n',
    'NG': 'ŋ',
    'NX': 'ɾ̃',
    'OW': 'oʊ',
    'OY': 'ɔɪ',
    'P': 'p',
    'Q': 'ʔ',
    'R': 'r',
    'S': 's',
    'SH': 'ʃ',
    'T': 't',
    'TH': 'θ',
    'UH': 'ʊ',
    'UW': 'u',
    'V': 'v',
    'W': 'w',
    'Y': 'j',
    'Z': 'z',
    'ZH': 'ʒ'
}


def arpabet_to_kk(apb):
    ''' translate an arpabet phonemic into a kk phonetic
    '''
    if apb[-1].isdigit():
        stress = int(apb[-1])
        apb = apb if apb == 'AH1' else apb[:-1]
    else:
        stress = 0

    kk = a2kk[apb]
    if stress == 0:
        return kk
    elif stress == 1:
        return '**{}**'.format(kk)
    else:  # stress == 2
        return '*{}*'.format(kk)


def read_dict(dict_path):
    phoneme_dict = {}
    with open(dict_path, 'r', encoding='utf-8', errors='replace') as dictfile:
        for line in dictfile:
            if not line.startswith(';;;') and line[0].isupper():
                v = line.split()
                phoneme_dict[v[0]] = ''.join([
                    arpabet_to_kk(phm) for phm in v[1:]
                ])
    print('CMUDict prepared')
    return phoneme_dict


class CMUDict:
    def __init__(self, dict_path):
        self._phoneme_dict = read_dict(dict_path)

    def __getitem__(self, word):
        if word.upper() in self._phoneme_dict:
            return self._phoneme_dict[word.upper()]
        else:
            raise KeyError(word)

    def __contains__(self, word):
        return word.upper() in self._phoneme_dict
