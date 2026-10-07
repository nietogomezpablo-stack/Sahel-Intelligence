import sqlite3
import spacy

nlp = spacy.load("fr_core_news_lg")

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, content
FROM articles
WHERE id IN (4, 9)
""")

articles = cursor.fetchall()

attack_lemmas = {
    "attaque",
    "attaquer",
    "viser",
    "mener",
    "frapper",
    "tuer"
}

for article_id, content in articles:
    doc = nlp(content)

    print()
    print("ARTICLE:", article_id)

    for sentence in doc.sents:
        sentence_attack_tokens = [
            token
            for token in sentence
            if token.lemma_.lower() in attack_lemmas
        ]

        if not sentence_attack_tokens:
            continue

        event_locations = set()

        for entity in sentence.ents:
            if entity.label_ != "LOC":
                continue

            location_token = entity.root

            current = location_token
            distance = 0
            related_to_attack = False

            while current.head != current and distance < 5:
                current = current.head
                distance += 1

                if current in sentence_attack_tokens:
                    related_to_attack = True
                    break

                if current.lemma_.lower() in {
                    "force",
                    "position",
                    "poste",
                    "détachement",
                    "zone",
                    "village"
                }:
                    related_to_attack = True
                    break

            if related_to_attack:
                event_locations.add(entity.text)

        if event_locations:
            print()
            print("TEXT:", sentence.text.strip())
            print("EVENT LOCATIONS:", sorted(event_locations))

connection.close()
