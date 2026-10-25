"""Step 2 – flag spam and non-answers with plain Python (no LLM).

Input:  data/interim/01_prepared.csv   Output: data/interim/02_spam.csv
"""

from __future__ import annotations

import re

import pandas as pd
from lingua import Language, LanguageDetectorBuilder

from project import paths

# Build language detector for German and English only
# We only care if text IS German or English - everything else is spam
DETECTOR = LanguageDetectorBuilder.from_languages(
    Language.GERMAN,
    Language.ENGLISH,
).build()

# Minimum confidence threshold for language detection
MIN_CONFIDENCE = 0.5

# Minimum words to trigger language check (answers < 3 words are not checked)
MIN_WORDS_FOR_LANGUAGE_CHECK = 3


def has_foreign_language(text: str) -> bool:
    """Check if text is NOT German or English (therefore spam).

    Returns True if the language is detected as foreign or unknown.
    Language detection is unreliable for very short texts (< 3 words), so those pass through.

    Also returns True if the text is punctuation-only or keyboard mashing (no usable language).
    """
    if not text or text.strip() == "":
        return False

    # Count words
    words = text.split()
    if len(words) < MIN_WORDS_FOR_LANGUAGE_CHECK:
        return False

    # Check for non-Latin characters (Cyrillic, Greek, Asian scripts, etc.)
    # These are clearly not German/English
    has_non_latin = any(ord(c) > 127 and not c.isascii() for c in text)
    if has_non_latin:
        # Check if it contains any German/English letters at all
        has_german_letters = any(c in text.lower() for c in "äöüß")
        has_english_letters = any(c in text.lower() for c in "abcdefghijklmnopqrstuvwxyz")

        if not has_german_letters and not has_english_letters:
            # Pure non-Latin text = definitely not German/English
            return True

    # Detect language with confidence scores
    languages = DETECTOR.compute_language_confidence_values(text)

    if not languages:
        return True  # No language detected = likely spam

    # Get best language
    best = languages[0]

    # If both German and English have 0 confidence, it's likely punctuation/keyboard mashing
    german_conf = next((lang.value for lang in languages if lang.language == Language.GERMAN), 0)
    english_conf = next((lang.value for lang in languages if lang.language == Language.ENGLISH), 0)

    if german_conf == 0 and english_conf == 0:
        return True  # No language detected = spam (punctuation/keyboard mashing)

    # If the best language is NOT German or English, it's spam
    if best.language not in (Language.GERMAN, Language.ENGLISH):
        return True

    # Pass through if German or English with sufficient confidence
    if best.value >= MIN_CONFIDENCE:
        # Special case: Danish/Norwegian/Swedish text detected as English
        # Check for Nordic-specific words that aren't English
        danish_nordic_words = [
            "hej",  # Danish/Norwegian/Swedish: hello (not English)
            "jeg",  # Danish/Norwegian: I (not English)
            "du",  # Danish/Norwegian/Swedish: you
            "havde",  # Danish: had
            "har",  # Danish/Norwegian/Swedish: has
            "vil",  # Danish/Norwegian/Swedish: will/want
            "kan",  # Danish/Norwegian/Swedish: can
            "må",  # Danish/Norwegian: may
            "ønskede",  # Danish: wanted
            "pris",  # Danish/Norwegian/Swedish: price (English 'price' is same)
            "kende",  # Danish: know (not English)
            "hvad",  # Danish/Norwegian/Swedish: what
            "hvem",  # Danish/Norwegian: who
            "hvornår",  # Danish: when
            "hvor",  # Danish/Norwegian/Swedish: where
            "hvorfor",  # Danish/Norwegian/Swedish: why
            "hvis",  # Danish/Norwegian/Swedish: if
            "eller",  # Danish/Norwegian/Swedish: or
            "og",  # Danish/Norwegian/Swedish: and
            "men",  # Danish/Norwegian/Swedish: but
            "med",  # Danish/Norwegian/Swedish: with
            "af",  # Danish/Norwegian/Swedish: of
            "for",  # Danish/Norwegian/Swedish: for
            "til",  # Danish/Norwegian/Swedish: to
            "fra",  # Danish/Norwegian: from
            "den",  # Danish/Norwegian/Swedish: the
            "det",  # Danish/Norwegian/Swedish: it
            "der",  # Danish/Norwegian/Swedish: there/who
            "hun",  # Danish/Norwegian: she
            "han",  # Danish/Norwegian: he
            "vi",  # Danish/Norwegian/Swedish: we
            "tak",  # Danish/Norwegian: thanks
        ]
        text_lower = text.lower()
        has_nordic = any(w in text_lower for w in danish_nordic_words)

        # Check for Danish-specific characters (unless the text is pure English)
        has_danish_chars = any(c in text for c in "æøå")

        if has_danish_chars or (has_nordic and len(words) >= 3):
            # Contains Nordic characters or words = not English survey content
            return True
        return False

    # For texts detected as English with low confidence (< 0.5),
    # check if it looks like German survey content
    # If it's English but doesn't contain German words, it might be foreign
    if best.value < 0.5:
        # Check for German words (even in English text, German words are expected)
        german_words = [
            "stadtteil",
            "frankfurt",
            "nord",
            "mitte",
            "ost",
            "west",
            "süd",
            "umland",
            "kitaplatz",
            "kindergarten",
            "kind",
            "baby",
            "parks",
            "grün",
            "wohne",
            "leben",
            "wohnung",
            "haus",
            "straße",
            "platz",
            "gut",
            "schlecht",
            "mag",
            "nicht",
            "gefällt",
        ]
        text_lower = text.lower()
        has_german_word = any(gw in text_lower for gw in german_words)

        if not has_german_word and best.language == Language.ENGLISH:
            # English text without any German words in a German survey context
            # This is suspicious - likely not a real answer
            return True

    # Check for Danish/Norwegian/Swedish specific words that might be detected as English
    # These languages use Latin alphabet but have distinct vocabulary
    danish_norwegian_swedish_words = [
        "hej",  # Danish/Norwegian/Swedish: hello
        "jeg",  # Danish/Norwegian: I
        "du",  # Danish/Norwegian/Swedish: you
        "havde",  # Danish: had
        "har",  # Danish/Norwegian/Swedish: has
        "vil",  # Danish/Norwegian/Swedish: will/want
        "kan",  # Danish/Norwegian/Swedish: can
        "må",  # Danish/Norwegian: may
        "ønskede",  # Danish: wanted
        "pris",  # Danish/Norwegian/Swedish: price
        "kende",  # Danish: know
        "hvad",  # Danish/Norwegian/Swedish: what
        "hvem",  # Danish/Norwegian: who
        "hvornår",  # Danish: when
        "hvor",  # Danish/Norwegian/Swedish: where
        "hvorfor",  # Danish/Norwegian/Swedish: why
        "hvis",  # Danish/Norwegian/Swedish: if
        "eller",  # Danish/Norwegian/Swedish: or
        "og",  # Danish/Norwegian/Swedish: and
        "men",  # Danish/Norwegian/Swedish: but
        "med",  # Danish/Norwegian/Swedish: with
        "af",  # Danish/Norwegian/Swedish: of
        "for",  # Danish/Norwegian/Swedish: for
        "til",  # Danish/Norwegian/Swedish: to
        "fra",  # Danish/Norwegian: from
        "den",  # Danish/Norwegian/Swedish: the
        "det",  # Danish/Norwegian/Swedish: it
        "der",  # Danish/Norwegian/Swedish: there/who
        "hun",  # Danish/Norwegian: she
        "han",  # Danish/Norwegian: he
        "vi",  # Danish/Norwegian/Swedish: we
        "vielleicht",  # German-ish but not standard German
        "tak",  # Danish/Norwegian: thanks
    ]
    text_lower = text.lower()
    has_danish_nordic = any(w in text_lower for w in danish_norwegian_swedish_words)

    if has_danish_nordic and best.language == Language.ENGLISH:
        # Contains Danish/Norwegian/Swedish words but detected as English
        # This is a strong signal of a Nordic language (not German/English survey content)
        return True

    # Low confidence for German/English - suspicious for longer texts
    # But pass short texts through to avoid false positives
    return False


def only_punctuation_or_placeholders(text: str) -> bool:
    """Check if text contains only punctuation, placeholders, or whitespace."""
    if not text or text.strip() == "":
        return True

    # Remove all punctuation, whitespace, and common placeholders
    cleaned = text.strip()

    # Remove [URL] placeholders
    cleaned = re.sub(r"\[URL\]", "", cleaned)

    # Remove all punctuation and whitespace
    cleaned = re.sub(
        r"[\s\.\,\!\?\-\_\:\;\'\"\(\)\[\]\{\}\|\\\/\@\#\$\%\^\&\*\+\=\<\>\(\)\-\_\=\+\[\]\{\}\|\;\'\:\"]",
        "",
        cleaned,
    )

    return cleaned.strip() == ""


def has_url_with_sales_language(text: str) -> bool:
    """Check if text contains URL with sales language or has obvious sales content.

    This catches:
    - Text with [URL] or URL followed by sales language
    - Text with sales language even without explicit URL (like 'TruePills', 'PillsBix')
    """
    if not text:
        return False

    text_lower = text.lower()

    # Check for URL patterns
    has_url = "url" in text_lower or "[url]" in text_lower or "http" in text_lower

    # Sales indicators - broad set including brand names and common spam patterns
    sales_indicators = [
        # German
        r"kostenlos",  # free
        r"gewinnspiel",  # contest
        r"gewinnen",  # win
        r"sofort",  # immediately
        r"jetzt",  # now
        r"aktion",  # promotion
        r"günstig",  # cheap
        r"bestellen",  # order
        r"kaufen",  # buy
        r"angebot",  # offer
        r"top angebot",  # great offer
        r"exklusiv",  # exclusive
        r"verfügbar",  # available
        r"discreet",  # discreet (German spelling)
        # English
        r"limited",  # limited
        r"free",  # free
        r"offer",  # offer
        r"special",  # special
        r"buy",  # buy
        r"order",  # order
        r"discreet",  # discreet
        r"online",  # online (often used in spam)
        r"available",  # available
        # Brand names commonly in spam
        r"truepills",  # brand name
        r"pillsbix",  # brand name
        r"pills",  # pills (generic but often spam)
        r"medication",  # medication
        r"pharmacy",  # pharmacy
        r"prescription",  # prescription
        # Common spam phrases
        r"win ",  # win (with space)
        r"giveaway",  # giveaway
        r"prize",  # prize
        r"lottery",  # lottery
        r"sms",  # sms (often in spam)
        r"sms gewinnen",  # sms win
        r"iphone",  # iPhone giveaway
        r"gewinn",  # win (German)
    ]

    # Check for sales language OR URL with any sales keyword
    for indicator in sales_indicators:
        if re.search(indicator, text_lower):
            # If we have URL pattern OR it's a strong spam indicator
            if has_url or indicator in ["truepills", "pillsbix", "pills", "iphone", "gewinn"]:
                return True

    return False


def is_short_real_answer(text: str) -> bool:
    """Check if text is a short real answer (NOT spam).

    Real short answers like "Kitaplätze", "nichts", "Parks" should NOT be flagged.
    These are typically German or English words that are actual answers to the survey.
    """
    if not text or text.strip() == "":
        return False

    words = text.split()
    if len(words) > 2:  # Very short - max 2 words
        return False

    # Check if it's a real word (contains letters, not just punctuation/numbers)
    # Remove punctuation and check if any alphabetic content remains
    cleaned = re.sub(r"[^\w]", "", text)

    # Must be alpha characters only (no numbers mixed in)
    if not cleaned.isalpha():
        return False

    # Length check - must be at least 3 chars
    if len(cleaned) < 3:
        return False

    # Brand names and obvious non-answers
    # Common spam indicators that look like short answers
    spam_indicators = [
        "pills",
        "pillsbix",
        "truepills",
        "david",
        "daviddax",
        "davidemash",  # Brand/person names
        "jason",
        "jasonmus",  # Brand/person names
        "robert",
        "robertemash",  # Brand/person names
        "mason",
        "masonemash",  # Brand/person names
        "cyharles",
        "cyharlespax",  # Brand/person names
        "jerald",
        "jeraldfew",  # Brand/person names
        "albert",
        "albertdreni",  # Brand/person names
        "bit",
        "bot",
        "box",
        "hub",
        "link",
        "site",
        "web",  # Generic spam words
        "click",
        "now",
        "free",
        "win",
        "give",
        "take",  # Spam verbs
    ]

    text_lower = cleaned.lower()
    for indicator in spam_indicators:
        if indicator in text_lower:
            return False

    return True


def detect_spam(positive: str, negative: str, district_known: bool, district: str) -> list[str]:
    """Return the reasons why a response is spam – an empty list means: not spam.

    A response is spam only if it has NO usable content at all.
    Short real answers ("Kitaplätze", "nichts") are NOT spam.

    district="SPAM" is a STRONG signal - most responses from SPAM district are spam.
    """
    reasons = []

    # Check if both answers look like valid survey content
    # A valid answer should be in German or English and contain survey-relevant content
    def is_valid_survey_answer(text: str) -> bool:
        """Check if text is a valid German/English survey answer."""
        if not text or text.strip() == "":
            return False

        # Check for punctuation-only
        if only_punctuation_or_placeholders(text):
            return False

        # Check for sales language - sales content is never valid
        if has_url_with_sales_language(text):
            return False

        words = text.split()

        # Very short text (< 3 words) - check if it's a valid short answer
        if len(words) < MIN_WORDS_FOR_LANGUAGE_CHECK:
            cleaned = re.sub(r"[^\w]", "", text)
            if len(cleaned) > 1 and cleaned.isalpha():
                # Check if it's a brand name/ spam indicator
                if is_short_real_answer(text):
                    return True
                return False
            return False

        # For longer texts, check if it's German or English
        if has_foreign_language(text):
            return False

        return True

    # A response is spam if BOTH answers are NOT valid survey content
    pos_valid = is_valid_survey_answer(positive)
    neg_valid = is_valid_survey_answer(negative)

    # Special case: SPAM district - if both answers are clearly NOT valid survey content,
    # it's definitely spam
    is_spam_district = district == "SPAM"

    if is_spam_district and not pos_valid and not neg_valid:
        # Both answers are clearly spam - flag as spam
        # Determine which rules fired
        if not pos_valid:
            if has_foreign_language(positive) if positive.strip() else False:
                reasons.append("foreign_language_or_mashing")
            elif only_punctuation_or_placeholders(positive):
                reasons.append("only_punctuation")

        if not neg_valid:
            if has_foreign_language(negative) if negative.strip() else False:
                reasons.append("foreign_language_or_mashing")
            elif only_punctuation_or_placeholders(negative):
                reasons.append("only_punctuation")

        # Also check for sales URL
        if has_url_with_sales_language(positive) or has_url_with_sales_language(negative):
            reasons.append("sales_url")

    elif not pos_valid and not neg_valid:
        # Both answers are problematic (non-SPAM district)
        if has_foreign_language(positive) if positive.strip() else False:
            reasons.append("foreign_language_or_mashing")
        elif only_punctuation_or_placeholders(positive):
            reasons.append("only_punctuation")

        if has_foreign_language(negative) if negative.strip() else False:
            reasons.append("foreign_language_or_mashing")
        elif only_punctuation_or_placeholders(negative):
            reasons.append("only_punctuation")

    # Rule 3: [URL] with sales language (applies regardless of district)
    if has_url_with_sales_language(positive) or has_url_with_sales_language(negative):
        if "sales_url" not in reasons:
            reasons.append("sales_url")

    return reasons


def run(limit: int | None = None) -> pd.DataFrame:
    """Read 01_prepared.csv, add is_spam / spam_reason, write 02_spam.csv, print counts."""
    df = pd.read_csv(paths.PREPARED)

    if limit is not None:
        df = df.iloc[:limit].copy()

    # Initialize columns
    df["is_spam"] = False
    df["spam_reason"] = ""

    # Counters for each reason
    reason_counts: dict[str, int] = {}

    # Process each row
    for idx, row in df.iterrows():
        reasons = detect_spam(
            positive=str(row["positive"]),
            negative=str(row["negative"]),
            district_known=bool(row["district_known"]),
            district=str(row["district"]),
        )

        if reasons:
            df.loc[idx, "is_spam"] = True
            df.loc[idx, "spam_reason"] = ";".join(reasons)

            for reason in reasons:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1

    # Write output
    paths.SPAM.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(paths.SPAM, index=False)

    # Print summary (never comment text, only counts)
    print(f"Processed {len(df)} rows")
    print(f"Total spam flagged: {int(df['is_spam'].sum())}")
    print("\nReasons:")
    for reason, count in sorted(reason_counts.items()):
        print(f"  {reason}: {count}")

    return df
