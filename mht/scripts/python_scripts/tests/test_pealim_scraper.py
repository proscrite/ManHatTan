def test_scrap_verb_link():
    """Test the scrap_verb_link function with a known verb."""
    test_verb = "לדבר"
    url = scrap_verb_link(test_verb)
    assert url is not None, f"Failed to find URL for verb: {test_verb}"
    print(f"URL for '{test_verb}': {url}")
    test_gibberish = 'כדח;פא'
    url = scrap_verb_link(test_gibberish)
    assert url is None, f"Expected no URL for gibberish input: {test_gibberish}"
    test_noverb = 'כן'
    url = scrap_verb_link(test_noverb)
    assert url is None, f"Expected no URL for non-verb input: {test_noverb}"



def test_scrap_conjugation_dict():
    """Test the scrap_conjugation_dict function with a known verb URL."""
    test_verb = "לדבר"
    url = scrap_verb_link(test_verb)
    conj_dict = scrap_conjugation_dict(url)
    assert conj_dict, f"Failed to get conjugation dictionary for verb: {test_verb}"
    assert isinstance(conj_dict, dict), "Conjugation dictionary should be a dictionary"
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in conj_dict.items()), "Keys and values in conjugation dictionary should be strings"
    assert 'PERF-1s' in conj_dict, "Expected key 'PERF-1s' not found in conjugation dictionary"
    print(f"Conjugation dictionary for '{test_verb}': {conj_dict}")

    test_verb = "לטעות"
    url = scrap_verb_link(test_verb)
    conj_dict = scrap_conjugation_dict(url)
    assert conj_dict, f"Failed to get conjugation dictionary for verb: {test_verb}"
    assert isinstance(conj_dict, dict), "Conjugation dictionary should be a dictionary"
    auxiliary_form = conj_dict.get('IMPF-3fp', None)
    assert auxiliary_form == "יטעו", "Expected auxiliary form 'יטעו' not found in conjugation dictionary for 'לטעות'"


def test_sample_random_verb():
    """Test the sample_random_verb function."""
    verb = sample_random_verb(lipstick)
    assert verb is not None, "Failed to sample a random verb from lipstick"
    print(f"Sampled random verb: {verb}")


def test_search_verbs():
    """Test the search_verbs function."""
    verbs_df = search_verbs(lipstick)
    assert not verbs_df.empty, "No verbs found in lipstick DataFrame"
    print(f"Found {len(verbs_df)} verbs in lipstick DataFrame")

# test_scrap_verb_link()
# test_sample_random_verb()
# test_scrap_conjugation_dict()
# test_search_verbs()