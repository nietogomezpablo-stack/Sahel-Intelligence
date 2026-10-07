from resolve_events import (
    calculate_event_similarity,
    can_merge_events
)


def get_entity_id(cursor, entity_name):
    cursor.execute("""
    SELECT id
    FROM entities
    WHERE LOWER(canonical_name) = LOWER(?)
    LIMIT 1
    """, (entity_name,))

    result = cursor.fetchone()

    if result is None:
        return None

    return result[0]


def get_event_entity_ids(
    cursor,
    event_id,
    relation_type
):
    cursor.execute("""
    SELECT entity_id
    FROM event_entities
    WHERE event_id = ?
    AND relation_type = ?
    """, (
        event_id,
        relation_type
    ))

    return {
        row[0]
        for row in cursor.fetchall()
    }


def claimants_match(
    cursor,
    event_id,
    claimants
):
    if not claimants:
        return False

    candidate_entity_ids = set()

    for claimant in claimants:
        entity_id = get_entity_id(
            cursor,
            claimant
        )

        if entity_id is not None:
            candidate_entity_ids.add(entity_id)

    if not candidate_entity_ids:
        return False

    existing_entity_ids = get_event_entity_ids(
        cursor,
        event_id,
        "claimant"
    )

    return bool(
        candidate_entity_ids.intersection(
            existing_entity_ids
        )
    )


def find_similar_event(
    cursor,
    event_date,
    event_type,
    country,
    location,
    claimants
):
    cursor.execute("""
    SELECT
        id,
        event_date,
        event_type,
        country,
        location
    FROM events
    """)

    existing_events = cursor.fetchall()

    candidate_event = {
        "event_date": event_date,
        "event_type": event_type,
        "country": country,
        "location": location
    }

    best_event_id = None
    best_similarity = 0.0

    for existing_event in existing_events:
        existing_event_data = {
            "event_date": existing_event[1],
            "event_type": existing_event[2],
            "country": existing_event[3],
            "location": existing_event[4]
        }

        if (
            event_type == "claim_responsibility"
            and location == "unknown"
            and existing_event[4] == "unknown"
            and event_date == existing_event[1]
            and country == existing_event[3]
            and claimants_match(
                cursor,
                existing_event[0],
                claimants
            )
        ):
            return existing_event[0], 1.0

        if not can_merge_events(
            candidate_event,
            existing_event_data
        ):
            continue

        similarity = calculate_event_similarity(
            candidate_event,
            existing_event_data
        )

        if similarity > best_similarity:
            best_event_id = existing_event[0]
            best_similarity = similarity

    return best_event_id, best_similarity


def link_event_to_article(
    cursor,
    event_id,
    article_id
):
    cursor.execute("""
    INSERT OR IGNORE INTO event_articles (
        event_id,
        article_id
    )
    VALUES (?, ?)
    """, (
        event_id,
        article_id
    ))


def link_entity_to_event(
    cursor,
    event_id,
    entity_name,
    relation_type
):
    entity_id = get_entity_id(
        cursor,
        entity_name
    )

    if entity_id is None:
        return False

    cursor.execute("""
    INSERT OR IGNORE INTO event_entities (
        event_id,
        entity_id,
        relation_type
    )
    VALUES (?, ?, ?)
    """, (
        event_id,
        entity_id,
        relation_type
    ))

    return True


def store_event(
    cursor,
    article_id,
    title,
    event_date,
    event_type,
    country,
    location,
    description,
    confidence,
    claimants=None,
    attackers=None,
    targets=None
):
    existing_event_id, similarity = find_similar_event(
        cursor,
        event_date,
        event_type,
        country,
        location,
        claimants
    )

    if existing_event_id is not None:
        event_id = existing_event_id
        created = False

    else:
        cursor.execute("""
        INSERT INTO events (
            title,
            event_date,
            event_type,
            country,
            location,
            description,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            event_date,
            event_type,
            country,
            location,
            description,
            confidence
        ))

        event_id = cursor.lastrowid
        created = True

    link_event_to_article(
        cursor,
        event_id,
        article_id
    )

    if claimants:
        for claimant in claimants:
            link_entity_to_event(
                cursor,
                event_id,
                claimant,
                "claimant"
            )

    if attackers:
        for attacker in attackers:
            link_entity_to_event(
                cursor,
                event_id,
                attacker,
                "attacker"
            )

    if targets:
        for target in targets:
            link_entity_to_event(
                cursor,
                event_id,
                target,
                "target"
            )

    return event_id, created
