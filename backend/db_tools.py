import sqlite3
from constants import *
from datetime import date
import random
from collections import defaultdict

# Returns a dict containing the word info of word_id from dictionary
def get_word_info(word_id: int) -> dict:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM dictionary WHERE word_id = ?''', (word_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    else:
        return dict(row)

# Inserts a new username into users table, fails if username is not unique
def create_user(username: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (username) VALUES (?)''', (username,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_affected == 1:
        return True
    else:
        return False
    
# Given a username, return the userid
def get_user_id(username: str) -> int:

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE username = ?''', (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return -1
    else:
        return row['user_id']

# Queries the database for the next word for review. Returns dict containing word info
def choose_review_word(username: str) -> dict:

    today  = str(date.today())
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT d.word_id, up.due_date
        FROM dictionary d
        JOIN user_progress up ON d.word_id = up.word_id AND up.due_date <= ?
    ''',(today,))

    rows = cursor.fetchall()
    conn.close()

    due_words = defaultdict(list)
    due_dates = set()
    for row in rows:
        due_dates.add(row['due_date'])
        due_words[row['due_date']].append(row['word_id'])
    
    due_dates = list(due_dates)
    due_dates.sort()

    chosen_word_id = random.choice(due_words[due_dates[0]])   

    return get_word_info(chosen_word_id)

# Queries the database for k new words to add to queue for user, returns the word_ids of chosen words in a list
# Chooses words from hi, then med, then low freq
def choose_new_words(user_id: int, k: int) -> list:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT d.word_id, d.frequency
        FROM dictionary d
        LEFT JOIN user_progress up ON d.word_id = up.word_id AND up.user_id = ?
        WHERE up.word_id IS NULL
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()

    unseen_words = {
        0: [], 1: [], 2: []
    }

    for row in rows:
        freq = row['frequency']
        unseen_words[freq].append(row['word_id'])
    
    hi_freq = min(len(unseen_words[0]), k)
    med_freq = min(len(unseen_words[1]), k - hi_freq)
    low_freq = min(len(unseen_words[2]), k - hi_freq - med_freq)

    chosen_words = random.sample(unseen_words[0], hi_freq) + random.sample(unseen_words[1], med_freq) + random.sample(unseen_words[2], low_freq)

    return chosen_words

# Inserts new words into user_progress, with due_date set to today
def insert_user_progress_words(user_id: int, new_words : list) :

    today  = str(date.today())
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for word_id in new_words:
        cursor.execute('''
            INSERT INTO user_progress (user_id, word_id, n, interval, EF, due_date) 
            VALUES (?, ?, ?, ?, ?, ?) 
        ''', (user_id, word_id, 0, 0, 2.5, today,))
    conn.commit()    
    conn.close()

def update_user_progress(user_id: int, word_id: int, n: int, interval: int, EF: float, due_date: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_progress 
        SET n = ?, interval = ?, EF = ?, due_date = ?
        WHERE user_id = ? AND word_id = ?
    ''', (n, interval, EF, due_date, user_id, word_id,))
    conn.commit()    
    conn.close()


# Fills the word queue for user to MAX_NEW_WORDS, returns the number of words added
def fill_word_queue(user_id: int) -> int:

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM user_progress WHERE n = -1 ''')

    unseen_words = cursor.rowcount()
    conn.close()

    k = max(0, MAX_NEW_WORDS - unseen_words)
    new_words = choose_new_words(user_id, k)
    insert_user_progress_words(user_id, new_words)

    return k


# Returns the number of unseen words in user_progress
def unseen_words(user_id: int) -> int:

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM user_progress WHERE n = -1 ''')

    unseen_words = cursor.rowcount()
    conn.close()

    return unseen_words
