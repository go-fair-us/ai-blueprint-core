from serve import extract_output_text, build_narrative_input, SYSTEM_PROMPT


def test_extract_output_text_prefers_output_text_field():
    assert extract_output_text({"output_text": "  Hello.  "}) == "Hello."


def test_extract_output_text_walks_output_array():
    payload = {
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": "DOI is the default."}],
            }
        ]
    }
    assert extract_output_text(payload) == "DOI is the default."


def test_extract_output_text_empty_on_junk():
    assert extract_output_text({}) == ""
    assert extract_output_text({"output": [{"content": []}]}) == ""


def test_build_narrative_input_includes_question_and_passages():
    messages = build_narrative_input(
        "What is a DOI?",
        [{"slug": "persistent-identifiers", "title": "Persistent identifiers", "href": "/topics/persistent-identifiers.html"}],
    )
    assert messages[0]["role"] == "system"
    assert SYSTEM_PROMPT in messages[0]["content"]
    assert "What is a DOI?" in messages[1]["content"]
    assert "persistent-identifiers" in messages[1]["content"]
