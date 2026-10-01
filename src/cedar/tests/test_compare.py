from defs.compare import compare_records, format_table
from defs.models import DatasetRecord, Term


def test_compare_marks_match_and_differ():
    gold = DatasetRecord(
        name="ACTT-4",
        funder=[Term(label="NIAID")],
        grant=["UM1AI148684"],
    )
    pred = DatasetRecord(
        name="ACTT-4",
        funder=[Term(label="NIAID")],
        citation=["https://example.org/paper"],
    )
    rows = {row.field: row for row in compare_records(gold, pred)}
    assert rows["name"].status == "match"
    assert rows["grant"].status == "gold_only"
    assert rows["citation"].status == "pred_only"
    table = format_table(list(rows.values()))
    assert "grant" in table
    assert "gold_only" in table
