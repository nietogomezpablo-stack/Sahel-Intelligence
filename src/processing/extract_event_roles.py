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

attack_verbs = {
    "viser",
    "attaquer",
    "frapper"
}

action_verbs = {
    "mener"
}

for article_id, content in articles:
    doc = nlp(content)

    targets = set()
    attackers = set()

    for token in doc:
        if token.lemma_.lower() in attack_verbs:
            for child in token.children:
                if child.dep_ == "obj":
                    target_tokens = [child]

                    for target_child in child.children:
                        if target_child.dep_ == "amod":
                            target_tokens.append(target_child)

                    target_tokens = sorted(
                        target_tokens,
                        key=lambda item: item.i
                    )

                    target = " ".join(
                        item.text
                        for item in target_tokens
                    )

                    targets.add(target)

        if token.lemma_.lower() in action_verbs:
            for child in token.children:
                if child.dep_ == "obl:agent":
                    attacker_tokens = [child]

                    for attacker_child in child.children:
                        if attacker_child.dep_ == "amod":
                            attacker_tokens.append(attacker_child)

                    attacker_tokens = sorted(
                        attacker_tokens,
                        key=lambda item: item.i
                    )

                    attacker = " ".join(
                        item.text
                        for item in attacker_tokens
                    )

                    attackers.add(attacker)

    if targets or attackers:
        print()
        print("ARTICLE:", article_id)
        print(
            "TARGETS:",
            sorted(targets) if targets else ["unknown"]
        )
        print(
            "ATTACKERS:",
            sorted(attackers) if attackers else ["unknown"]
        )
        print("-" * 80)

connection.close()
