import sqlite3

# Connect to your existing database
conn = sqlite3.connect('database/sat_words.db')
cursor = conn.cursor()

# Check the schema of the 'dictionary' table
cursor.execute("PRAGMA table_info(dictionary);")
columns = cursor.fetchall()
for column in columns:
    print(column)

# View all words in the dictionary table
# cursor.execute("SELECT * FROM dictionary;")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# Close the connection
conn.close()
