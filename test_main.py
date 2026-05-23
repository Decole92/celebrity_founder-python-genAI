import pytest   
from main import format_users, get_users
from lib.helperFunction import make_user
from unittest.mock import patch, Mock



def test_returns_list():
    """Return type is always a list."""
    result = format_users([])
    assert isinstance(result, list)


def test_correct_count():
    """Correct number of filtered users."""
    users = [
        make_user("Ada",   "Lovelace", 1815),
        make_user("Gen",   "Zoomer",   2004),
        make_user("Alan",  "Turing",   1912),
        make_user("Alice", "Smith",    2001),
    ]
    assert len(format_users(users)) == 2


def test_name_format():
    """Names are in 'First Last' format."""
    users = [make_user("James", "Bond", 1968)]
    assert format_users(users)[0] == "James Bond"


def test_filters_post_2000():
    """Post-2000 users are excluded."""
    users = [make_user("Alice", "Smith", 2003)]
    assert format_users(users) == []


def test_includes_year_2000_edge_case():
    """Year 2000 births are included (boundary)."""
    users = [make_user("Bob", "Jones", 2000)]
    assert format_users(users) == ["Bob Jones"]


def test_empty_response():
    """Empty results returns empty list."""
    assert format_users([]) == []


def test_all_post_2000():
    """All post-2000 users → empty result."""
    users = [
        make_user("Gen",   "Zoomer",  2001),
        make_user("Alpha", "Gen",     2005),
        make_user("Young", "Person",  2010),
    ]
    assert format_users(users) == []


def test_names_are_strings():
    """All names are non-empty strings."""
    users = [
        make_user("Marie", "Curie",  1867),
        make_user("Alan",  "Turing", 1912),
    ]
    result = format_users(users)
    assert all(isinstance(n, str) and len(n) > 0 for n in result)


def test_missing_results_key():
    """get_users raises KeyError when API response has no 'results' key."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"info": {}}          # no 'results' key

    with patch("lib.helperFunction.requests.get", return_value=mock_response):
        with pytest.raises(KeyError):
            get_users()


# ── integration test ───────────────────────────────────────

def test_full_pipeline():
    """End-to-end: mocked HTTP → get_users → format_users."""
    fake_api_response = {
        "results": [
            make_user("Marie", "Curie",  1867),
            make_user("Gen",   "Zoomer", 2005),
            make_user("Alan",  "Turing", 1912),
        ]
    }
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = fake_api_response

    with patch("lib.helperFunction.requests.get", return_value=mock_response):
        users  = get_users()
        names  = format_users(users)

    assert names == ["Marie Curie", "Alan Turing"]
    assert "Gen Zoomer" not in names