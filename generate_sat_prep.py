import gemini_tools as gem
import pickle
import os
import time

FILENAMES = [
    './hi_freq_words',
    './med_freq_words',
    './low_freq_words'
]

def parse_txt(filename):
    parsed = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            if '...' in line:
                word = line.split('...')[0]
                try:
                    definition = line[line.index(';')+1:].strip()
                except:
                    print(filename, line)
                parsed.append([word, definition])
            line = f.readline()
    return parsed

def generate_pkl():
    for filename in FILENAMES:
        parsed = parse_txt(f'{filename}.txt')
        with open(f'{filename}.pkl', 'wb') as f:
            pickle.dump(parsed, f)

def generate_study_guide():
    if not os.path.exists('./bookmark.pkl'):
        bookmark = [0,0]
        with open('./bookmark.pkl', 'wb') as f:
            pickle.dump(bookmark, f)
    with open('./bookmark.pkl', 'rb') as f:
        file_bookmark, word_bookmark = pickle.load(f)

    file_idx = file_bookmark

    while file_idx < len(FILENAMES):
        filename = FILENAMES[file_idx]
        study_guide = {}

        if os.path.exists(f'{filename}_sg.pkl'):
            with open(f'{filename}_sg.pkl', 'rb') as f:
                study_guide = pickle.load(f)
        
        word_idx = 0
        if filename == FILENAMES[file_bookmark]:
            word_idx = word_bookmark
        with open (f'{filename}.pkl', 'rb') as f:
            word_list = pickle.load(f)

        retries = 1
        while word_idx < len(word_list):
            word, definition = word_list[word_idx]
            gemini_answer = gem.get_word_info(word=word, definition=definition)
            if not gemini_answer:
                if retries % 5 == 0:
                    with open(f'{filename}_sg.pkl', 'wb') as f:
                        pickle.dump(study_guide, f)
                print(f"Gemini failed on file: {file_idx}, word: {word_idx}, retries: {retries}")

                bookmark = [file_idx, word_idx]
                with open('./bookmark.pkl', 'wb') as f:
                    pickle.dump(bookmark, f)

                retries += 1
                time.sleep(5)
                continue
                # else:
                #     print(f"Gemini failed on file: {file_idx}, word: {word_idx}")
                #     break
            # study_guide.append([word, gemini_answer.definition, gemini_answer.synonyms, gemini_answer.sentences])
            study_guide[word] = {
                'definition' : gemini_answer.definition,
                'synonyms' : gemini_answer.synonyms,
                'sentences' : gemini_answer.sentences
            }
            print(word, study_guide[word])
            word_idx += 1
            time.sleep(4)

        with open(f'{filename}_sg.pkl', 'wb') as f:
            pickle.dump(study_guide, f)

        if word_idx < len(word_list):
            break
        file_idx += 1

    if file_idx < len(FILENAMES):
        bookmark = [file_idx, word_idx]
    else:
        bookmark = [len(FILENAMES), 0]
    with open('./bookmark.pkl', 'wb') as f:
            pickle.dump(bookmark, f)

if __name__ == '__main__':
    generate_study_guide()
