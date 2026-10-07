import sqlite3
import spacy

nlp = spacy.load("fr_core_news_lg")

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, content
FROM articles
WHERE content IS NOT NULL
AND language = 'French'
""")

articles = cursor.fetchall()

attack_nouns = {
    "attaque",
    "affrontement",
    "assaut",
    "combat"
}

attack_action_verbs = {
    "attaquer",
    "viser",
    "mener",
    "tuer",
    "frapper",
    "survenir"
}

claim_verbs = {
    "revendiquer"
}

for article_id, content in articles:
    doc = nlp(content)

    for sentence_doc in doc.sents:
        sentence = sentence_doc.text.strip()

        lemmas = {
            token.lemma_.lower()
            for token in sentence_doc
        }

        action_type = None

        if lemmas.intersection(claim_verbs):
            action_type = "claim_responsibility"

        elif (
            lemmas.intersection(attack_nouns)
            and lemmas.intersection(attack_action_verbs)
        ):
            action_type = "armed_attack"

        if action_type is None:
            continue

        print()
        print("ARTICLE:", article_id)
        print("ACTION TYPE:", action_type)
        print("TEXT:", sentence)
        print("-" * 80)

connection.close()
