import pickle

FILENAMES = [
    'hi_freq_words',
    'med_freq_words',
    'low_freq_words'
]

for filename in FILENAMES:

    with open(f'./{filename}_sg.pkl', 'rb') as f:
        study_guide = pickle.load(f)

    with open(f'./study_guide/{filename}_sg.txt', 'w') as f:
        for k,v in study_guide.items():
            try:
                f.write(f'Word: {k}\n')
                f.write(f'Definition: {v['definition']}\n')
                f.write(f'Synonyms: {v['synonyms'][0]}, {v['synonyms'][1]}\n')
                f.write(f'Sentence 1: {v['sentences'][0]}\n')
                f.write(f'Sentence 2: {v['sentences'][1]}\n')
                f.write('\n')
            except:
                print(f'failed on file: {f}, word: {k}')
                print(f'Definition: {v['definition']}')
                print(f'Synonyms: {v['synonyms'][0]}, {v['synonyms'][1]}')
                print(f'Sentence 1: {v['sentences'][0]}')
                print(f'Sentence 2: {v['sentences'][1]}')
                break
