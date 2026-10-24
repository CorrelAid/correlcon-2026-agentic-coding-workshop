import pandas as pd

from project.districts import stadtteil_mapping_func, stadtteil_region_mapping
from project.prepare import clean_text, mask_contacts, prepare


def test_district_mapping_from_2024_pipeline():
    assert stadtteil_mapping_func("Nordend-West") == "Nordend"
    assert stadtteil_mapping_func(" riedberg ") == "Kalbach-Riedberg"
    assert stadtteil_mapping_func("Masonemash") == "SPAM"
    assert stadtteil_region_mapping("Nordend") == "Mitte"


def test_clean_text_decodes_entities():
    assert clean_text("H&ouml;chst ") == "Höchst"
    assert clean_text(None) == ""


def test_mask_contacts_hard_cases():
    text = "Ruf an: +371) 29 66 79 38 oder +371 25 927 529, mail a@b.de, www.x.de"
    masked = mask_contacts(text)
    for secret in ("29 66", "927 529", "a@b.de", "www.x.de"):
        assert secret not in masked


def test_prepare_columns():
    raw = pd.DataFrame(
        {
            "ID": [1],
            "Date Created": ["2024-04-18 09:56:01"],
            "Title": ["x"],
            "Ich wohne im Stadtteil": ["Bornheim"],
            "Das gefällt mir gut mit Baby in Frankfurt": ["Parks"],
            "Das gefällt mir nicht gut mit Baby in Frankfurt": ["Kita&shy;pl&auml;tze"],
        }
    )
    df = prepare(raw)
    assert list(df.columns) == [
        "row_id",
        "month",
        "district",
        "region",
        "district_known",
        "positive",
        "negative",
    ]
    assert df.loc[0, "region"] == "Ost" and df.loc[0, "month"] == "2024-04"
