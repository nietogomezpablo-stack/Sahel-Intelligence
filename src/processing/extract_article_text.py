import sqlite3
import trafilatura
import time

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, url
FROM articles
WHERE content IS NULL
""")

articles = cursor.fetchall()

print("Artículos pendientes de extracción:", len(articles))

extraidos = 0
fallidos = 0

for article_id, url in articles:
    print("Procesando:", url)

    try:
        downloaded = trafilatura.fetch_url(url)

        if downloaded:
            content = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False
            )

            if content:
                cursor.execute(
                    """
                    UPDATE articles
                    SET content = ?
                    WHERE id = ?
                    """,
                    (content, article_id)
                )

                connection.commit()
                extraidos += 1
                print("Texto extraído correctamente.")
            else:
                fallidos += 1
                print("No se pudo extraer contenido.")
        else:
            fallidos += 1
            print("No se pudo descargar la página.")

    except Exception as error:
        fallidos += 1
        print("Error:", error)

    time.sleep(2)

connection.close()

print()
print("Extracción terminada.")
print("Textos extraídos:", extraidos)
print("Fallidos:", fallidos)
