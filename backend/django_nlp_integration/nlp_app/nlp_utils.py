# nlp_utils.py
import spacy

nlp = spacy.load('en_core_web_sm')

def explain_record(record):
    doc = nlp(record)
    explanations = []
    for ent in doc.ents:
        explanations.append((ent.text, ent.label_))
    return explanations
