import pickle

FILENAMES = [
    './hi_freq_words',
    './med_freq_words',
    './low_freq_words'
]

with open(f'{FILENAMES[0]}_sg.pkl', 'rb') as f:
    study_guide = pickle.load(f)

with open(f'{FILENAMES[0]}_sg.txt', 'w') as f:
    for k,v in study_guide.items():
        f.write(f'Word: {k}\n')
        f.write(f'Definition: {v['definition'].encode('ascii','ignore').decode()}\n')
        f.write(f'Synonyms: {v['synonyms'][0]}, {v['synonyms'][1]}\n')
        f.write(f'Sentence 1: {v['sentences'][0]}\n')
        f.write(f'Sentence 2: {v['sentences'][1]}\n')
        f.write('\n')
