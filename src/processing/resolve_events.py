import sqlite3
from datetime import datetime
from difflib import SequenceMatcher


def text_similarity(text_a, text_b):
    return SequenceMatcher(
        None,
        text_a.lower(),
        text_b.lower()
    ).ratio()


def get_days_difference(event_a, event_b):
    date_a = datetime.strptime(
        event_a["event_date"],
        "%Y-%m-%d"
    )

    date_b = datetime.strptime(
        event_b["event_date"],
        "%Y-%m-%d"
    )

    return abs((date_a - date_b).days)


def get_location_similarity(event_a, event_b):
    location_a = event_a["location"]
    location_b = event_b["location"]

    if (
        location_a == "unknown"
        or location_b == "unknown"
    ):
        return 0.0

    return text_similarity(
        location_a,
        location_b
    )


def calculate_event_similarity(event_a, event_b):
    score = 0.0

    if event_a["event_type"] == event_b["event_type"]:
        score += 0.30

    if event_a["country"] == event_b["country"]:
        score += 0.20

    days_difference = get_days_difference(
        event_a,
        event_b
    )

    if days_difference == 0:
        score += 0.30
    elif days_difference == 1:
        score += 0.20
    elif days_difference <= 3:
        score += 0.10

    location_similarity = get_location_similarity(
        event_a,
        event_b
    )

    if location_similarity >= 0.80:
        score += 0.20

    return round(score, 2)


def can_merge_events(event_a, event_b):
    if event_a["event_type"] != event_b["event_type"]:
        return False

    if event_a["country"] != event_b["country"]:
        return False

    days_difference = get_days_difference(
        event_a,
        event_b
    )

    if days_difference > 1:
        return False

    location_similarity = get_location_similarity(
        event_a,
        event_b
    )

    if location_similarity < 0.80:
        return False

    return True


def find_possible_duplicates():
    connection = sqlite3.connect(
        "data/intelligence.db"
    )

    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        id,
        title,
        event_date,
        event_type,
        country,
        location
    FROM events
    ORDER BY event_date
    """)

    events = cursor.fetchall()

    print("Eventos encontrados:", len(events))
    print()

    possible_duplicates = 0

    for index_a in range(len(events)):
        for index_b in range(
            index_a + 1,
            len(events)
        ):
            event_a = events[index_a]
            event_b = events[index_b]

            similarity = calculate_event_similarity(
                event_a,
                event_b
            )

            merge = can_merge_events(
                event_a,
                event_b
            )

            if merge:
                possible_duplicates += 1

                print("POSIBLE MISMO EVENTO")
                print(
                    "EVENTO A:",
                    event_a["id"],
                    "-",
                    event_a["title"]
                )
                print(
                    "EVENTO B:",
                    event_b["id"],
                    "-",
                    event_b["title"]
                )
                print(
                    "SIMILITUD:",
                    similarity
                )
                print("-" * 80)

    connection.close()

    print()
    print(
        "Posibles duplicados encontrados:",
        possible_duplicates
    )


if __name__ == "__main__":
    find_possible_duplicates()

