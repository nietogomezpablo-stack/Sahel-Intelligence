import sqlite3

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT * FROM articles
""")

articles = cursor.fetchall()

for article in articles:
    print(article)

connection.close()

print("Total de artículos:", len(articles))
