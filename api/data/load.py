import sqlite3
# Connect to the database (use the database file or ":memory:" for an in-memory database)
conn = sqlite3.connect('record.db')

# Create a cursor object
cursor = conn.cursor()

# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()
# print(tables)  # Output: [('data',), ...]

cursor.execute('SELECT * FROM data')  # Fetch all columns
rows = cursor.fetchall()  # Fetch all rows

# Display the number of records
print(f'Number of records: {len(rows)}') 

# Close the connection
conn.close()