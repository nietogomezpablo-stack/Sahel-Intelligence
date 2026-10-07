import spacy

nlp = spacy.load("xx_ent_wiki_sm")

text = """
Le président Abdourahamane Tiani a rencontré des représentants
du Burkina Faso à Niamey, au Niger.
"""

doc = nlp(text)

for entity in doc.ents:
    print(entity.text, "→", entity.label_)
