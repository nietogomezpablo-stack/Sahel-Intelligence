import sqlite3
import spacy

nlp = spacy.load("fr_core_news_lg")

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT content
FROM articles
WHERE id = 4
""")

content = cursor.fetchone()[0]

doc = nlp(content)

for sentence in doc.sents:
    lemmas = {
        token.lemma_.lower()
        for token in sentence
    }

    if "revendiquer" not in lemmas:
        continue

    print()
    print("FRASE:")
    print(sentence.text.strip())
    print()

    print("ENTIDADES:")

    for entity in sentence.ents:
        print(
            entity.text,
            "| TYPE:",
            entity.label_,
            "| ROOT:",
            entity.root.text
        )

    print()
    print("DEPENDENCIAS:")

    for token in sentence:
        print(
            token.text,
            "| LEMMA:",
            token.lemma_,
            "| DEP:",
            token.dep_,
            "| HEAD:",
            token.head.text
        )

connection.close()
