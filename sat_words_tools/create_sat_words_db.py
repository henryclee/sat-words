import sqlite3
import pickle

FILENAMES = [
    'hi_freq_words',
    'med_freq_words',
    'low_freq_words'
]

conn = sqlite3.connect('../backend/database/sat_words.db')
cursor = conn.cursor()

dictionary = set()

for i, filename in enumerate(FILENAMES):
    with open (f'./{filename}_sg.pkl', 'rb') as sg:
        study_guide = pickle.load(sg)
    
    for word, info in study_guide.items():
        if word in dictionary:
            continue
        dictionary.add(word)
        definition = info['definition']
        synonym1, synonym2 = info['synonyms'][:2]
        sentence1, sentence2 = info['sentences'][:2]

        cursor.execute('''
        INSERT INTO dictionary (word, definition, synonym1, synonym2, sentence1, sentence2, frequency)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (word, definition, synonym1, synonym2, sentence1, sentence2, i))

conn.commit()
conn.close()