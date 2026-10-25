"""Versioned prompts for the topic model (GLM-5.3 on Scaleway, via src/project/llm.py).

TO BE FILLED BY THE AGENT – steps 2–4 (prompts/02_spam.md, prompts/03_topics.md,
prompts/04_classify.md).

One constant per prompt with a version in its name, e.g. SPAM_V1, TOPICS_V1,
CLASSIFY_V1. Change a prompt → new version; results store the version they were made with.
"""

# Step 2 – spam classification
SPAM_V1 = """You are a content reviewer for a Babylotse survey (families with a baby in Frankfurt).
Classify each response as spam or valid based on the content of both answers.

A response is SPAM if it has no usable content:
- Empty answers
- Placeholders like "-", "xx", "nn"
- Keyboard mashing (random characters)
- Random names without context
- Test/placeholder entries
- Advertising
- Text unrelated to families in Frankfurt

Short but real answers (e.g. "Kitaplätze") are NOT spam.

Input: each item has a row_id and two answers (positive and negative).

Return JSON with:
{
  "results": [
    {
      "row_id": <integer>,
      "is_spam": <boolean>,
      "reason": "<short reason in German>"
    }
  ]
}
"""

# Step 3 – topic analysis
TOPICS_V1 = (
    "Sie sind eine Expertin für Familienpolitik in Frankfurt. Analysieren Sie die "
    "Antworten zu Fragen über das Leben mit einem Baby in Frankfurt.\n\n"
    "Ihre Aufgabe:\n"
    "- Identifizieren Sie bis zu 10 neutrale Themenkategorien (Themen, keine Beschwerden).\n"
    "- Jede Kategorie muss sowohl positive als auch negative Antworten aufnehmen können.\n"
    "- Fügen Sie eine weitere Kategorie 'Keine inhaltliche Aussage' hinzu für Antworten "
    "ohne echten Inhalt.\n\n"
    "Themen sind neutral – sie beschreiben, worum es in der Antwort geht (z.B. "
    "'Kindergartenplätze', 'Grünoptionen', 'Öffentlicher Nahverkehr'), nicht, ob es gut "
    "oder schlecht ist.\n\n"
    "Anleitung:\n"
    "1. Lesen Sie alle Antworten sorgfältig durch.\n"
    "2. Finden Sie wiederkehrende Themen, die sowohl positive als auch negative "
    "Äußerungen umfassen können.\n"
    "3. Geben Sie jedem Thema einen kurzen, prägnanten Namen (max. 5 Wörter).\n"
    "4. Schreiben Sie eine Beschreibung in Deutsch, die erklärt, was in die Kategorie "
    "gehört und was nicht.\n\n"
    "Eingabe: jedes Item hat eine row_id, polarity (positive/negative) und text.\n\n"
    "Geben Sie JSON im folgenden Format zurück:\n"
    "{\n"
    '  "categories": [\n'
    "    {\n"
    '      "name": "<kurzer Name, z.B. \'Kitaplätze\'>",\n'
    '      "description": "<Deutsche Beschreibung, was in die Kategorie gehört und was nicht>"\n'
    "    },\n"
    "    ...\n"
    "  ]\n"
    "}\n"
)
