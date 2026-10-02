from streamlit.testing.v1 import AppTest
from lostfound.config import ROOT

def app(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///" + str(tmp_path / "ui.db"))
    monkeypatch.setenv("LLM_API_KEY", "")
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()

def test_keyword_flow(monkeypatch, tmp_path):
    at = app(monkeypatch, tmp_path)
    assert not at.exception
    at.text_area[0].input("black insulated bottle with a silver lid")
    at.button[0].click().run()
    assert not at.exception
    result = at.session_state["result"]
    assert result.mode == "keyword" and result.matches[0].id == "LF-001"

def test_missing_key_and_refusal(monkeypatch, tmp_path):
    at = app(monkeypatch, tmp_path)
    at.radio[0].set_value("AI matching").run()
    at.text_area[0].input("black insulated bottle")
    at.button[0].click().run()
    assert at.session_state["result"].status == "unavailable"
    at.text_area[0].input("Who owns the black bottle?")
    at.button[0].click().run()
    assert at.session_state["result"].status == "refused"
    assert not at.exception

def test_category_filter(monkeypatch, tmp_path):
    at = app(monkeypatch, tmp_path)
    at.text_area[0].input("black insulated bottle")
    at.selectbox[0].select("Umbrella")
    at.button[0].click().run()
    assert all(m.id in {"LF-004","LF-005","LF-006"} for m in at.session_state["result"].matches)
    assert not at.exception
