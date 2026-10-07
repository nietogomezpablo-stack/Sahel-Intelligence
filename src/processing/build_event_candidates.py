import sqlite3
import re
import spacy
from datetime import datetime, timedelta
from store_event_candidates import store_event

nlp = spacy.load("fr_core_news_lg")

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, date, title, content
FROM articles
WHERE content IS NOT NULL
AND language = 'French'
""")

articles = cursor.fetchall()

months = {
    "janvier": 1,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12
}

weekdays = {
    "lundi": 0,
    "mardi": 1,
    "mercredi": 2,
    "jeudi": 3,
    "vendredi": 4,
    "samedi": 5,
    "dimanche": 6
}

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

target_verbs = {
    "viser",
    "attaquer",
    "frapper"
}

attacker_verbs = {
    "mener",
    "attaquer"
}

location_containers = {
    "zone",
    "région",
    "village",
    "axe",
    "abord"
}

generic_directions = {
    "nord",
    "sud",
    "est",
    "ouest"
}

explicit_date_pattern = r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b"

relative_weekday_pattern = r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b"


def build_attacker_phrase(token):
    tokens = [token]

    for child in token.children:
        if child.dep_ == "amod":
            tokens.append(child)

    tokens = sorted(tokens, key=lambda item: item.i)

    return " ".join(item.text for item in tokens)


def build_target_phrase(token):
    tokens = [token]

    for child in token.children:
        if child.dep_ in {"amod", "nmod"}:
            tokens.append(child)

            for grandchild in child.children:
                if grandchild.dep_ == "amod":
                    tokens.append(grandchild)

    tokens = sorted(tokens, key=lambda item: item.i)

    return " ".join(item.text for item in tokens)


def preceding_case_markers(token):
    markers = set()

    for child in token.children:
        if child.dep_ == "case":
            markers.add(child.lemma_.lower())

    return markers


def has_near_marker(token):
    for nearby in token.doc[
        max(token.i - 3, token.sent.start):
        token.i
    ]:
        if nearby.lemma_.lower() == "près":
            return True

    return False


def is_specific_event_location(entity):
    token = entity.root

    if entity.text.lower() in generic_directions:
        return False

    if entity.text == "État":
        return False

    if has_near_marker(token):
        return False

    markers = preceding_case_markers(token)

    if "vers" in markers:
        return False

    if "à" in markers:
        return True

    current = token
    distance = 0

    while distance < 4:
        head = current.head

        if head == current:
            break

        if head.lemma_.lower() in location_containers:
            container_markers = preceding_case_markers(head)

            if "près" in container_markers or "vers" in container_markers:
                return False

            return True

        current = head
        distance += 1

    return False


def extract_claimants(sentence_doc):
    claimants = set()

    for token in sentence_doc:
        if token.lemma_.lower() != "revendiquer":
            continue

        agents = [
            child
            for child in token.children
            if child.dep_ == "obl:agent"
        ]

        for agent in agents:
            for entity in sentence_doc.ents:
                if entity.label_ != "ORG":
                    continue

                current = entity.root
                distance = 0

                while distance < 4:
                    if current == agent:
                        claimants.add(entity.text)
                        break

                    if current.head == current:
                        break

                    current = current.head
                    distance += 1

    return claimants


events_created = 0
events_existing = 0

for article_id, publication_date, article_title, content in articles:
    publication_datetime = datetime.strptime(
        publication_date,
        "%Y-%m-%d %H:%M:%S"
    )

    doc = nlp(content)

    event_candidates = {}

    for sentence_doc in doc.sents:
        sentence = sentence_doc.text.strip()
        sentence_lower = sentence.lower()

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

        event_date = None

        explicit_match = re.search(
            explicit_date_pattern,
            sentence_lower
        )

        if explicit_match:
            weekday_name, day, month_name = explicit_match.groups()

            event_date = datetime(
                publication_datetime.year,
                months[month_name],
                int(day)
            )

            if event_date > publication_datetime:
                event_date = event_date.replace(
                    year=publication_datetime.year - 1
                )

        else:
            relative_match = re.search(
                relative_weekday_pattern,
                sentence_lower
            )

            if relative_match:
                weekday_name = relative_match.group(1)

                target_weekday = weekdays[weekday_name]
                publication_weekday = publication_datetime.weekday()

                days_back = (
                    publication_weekday - target_weekday
                ) % 7

                if days_back != 0:
                    event_date = publication_datetime - timedelta(
                        days=days_back
                    )

        if event_date is None:
            continue

        date_key = event_date.strftime("%Y-%m-%d")
        candidate_key = (action_type, date_key)

        if candidate_key not in event_candidates:
            event_candidates[candidate_key] = {
                "type": action_type,
                "country": "Niger",
                "locations": set(),
                "organizations": set(),
                "persons": set(),
                "targets": set(),
                "attackers": set(),
                "claimants": set(),
                "evidence": []
            }

        candidate = event_candidates[candidate_key]

        for entity in sentence_doc.ents:
            if entity.label_ == "PER":
                candidate["persons"].add(entity.text)

            elif entity.label_ == "ORG":
                candidate["organizations"].add(entity.text)

            elif entity.label_ == "LOC":
                if entity.text == candidate["country"]:
                    continue

                if is_specific_event_location(entity):
                    candidate["locations"].add(entity.text)

        if action_type == "armed_attack":
            for token in sentence_doc:
                if token.lemma_.lower() in target_verbs:
                    for child in token.children:
                        if child.dep_ == "obj":
                            candidate["targets"].add(
                                build_target_phrase(child)
                            )

                for child in token.children:
                    if child.lemma_.lower() == "contre":
                        candidate["targets"].add(
                            build_target_phrase(token)
                        )

                if token.lemma_.lower() in attacker_verbs:
                    for child in token.children:
                        if child.dep_ == "obl:agent":
                            candidate["attackers"].add(
                                build_attacker_phrase(child)
                            )

        if action_type == "claim_responsibility":
            candidate["claimants"].update(
                extract_claimants(sentence_doc)
            )

        candidate["evidence"].append(sentence)

    for candidate_key, candidate in event_candidates.items():
        action_type, event_date = candidate_key

        locations = sorted(candidate["locations"])

        if locations:
            location = locations[0]
        else:
            location = "unknown"

        if action_type == "armed_attack":
            title = f"Ataque en {location}"

        elif action_type == "claim_responsibility":
            if candidate["claimants"]:
                claimant = sorted(candidate["claimants"])[0]
                title = f"Reivindicación de ataque por {claimant}"
            else:
                title = "Reivindicación de ataque"

        else:
            title = article_title

        description = " ".join(candidate["evidence"])

        event_id, created = store_event(
            cursor=cursor,
            article_id=article_id,
            title=title,
            event_date=event_date,
            event_type=action_type,
            country=candidate["country"],
            location=location,
            description=description,
            confidence=0.7,
            claimants=candidate["claimants"],
            attackers=candidate["attackers"],
            targets=candidate["targets"]
        )

        if created:
            events_created += 1
            status = "CREATED"
        else:
            events_existing += 1
            status = "EXISTING"

        print()
        print("ARTICLE:", article_id)
        print("EVENT ID:", event_id)
        print("STATUS:", status)
        print("EVENT TYPE:", action_type)
        print("EVENT DATE:", event_date)
        print("COUNTRY:", candidate["country"])
        print("LOCATION:", location)
        print(
            "ATTACKERS:",
            sorted(candidate["attackers"])
            if candidate["attackers"]
            else ["unknown"]
        )
        print(
            "TARGETS:",
            sorted(candidate["targets"])
            if candidate["targets"]
            else ["unknown"]
        )
        print(
            "CLAIMANTS:",
            sorted(candidate["claimants"])
            if candidate["claimants"]
            else ["unknown"]
        )
        print("-" * 80)

connection.commit()
connection.close()

print()
print("Persistencia terminada.")
print("Eventos nuevos:", events_created)
print("Eventos ya existentes:", events_existing)

