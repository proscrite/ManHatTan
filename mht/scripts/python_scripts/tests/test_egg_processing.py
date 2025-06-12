def test_get_random_nid():
    """Test the get_random_nid function."""
    random_nid = get_random_nid(lipstick)
    assert isinstance(random_nid, np.int64), "Random n_id should be an integer."
    assert random_nid not in lipstick['n_id'].values, "Random n_id should not be in the lipstick DataFrame."

def test_init_hatched_egg():
    """Test the init_hatched_egg function."""
    word_ul = 'cat'
    egg_entry = init_hatched_egg(egg, word_ul, lipstick=lipstick, flag_lexeme=True)
    
    assert egg_entry['word_ul'] == word_ul, "Word_ul should match the input word."
    assert 'n_id' in egg_entry, "Egg entry should contain n_id."
    assert 'session_seen' in egg_entry, "Egg entry should contain session_seen."
    assert 'session_correct' in egg_entry, "Egg entry should contain session_correct."
    assert 'p_pred' in egg_entry, "Egg entry should contain p_pred."
    assert 'rebag' in egg_entry, "Egg entry should contain rebag."
    assert 'lexeme_string' in egg_entry, "Egg entry should contain lexeme_string."
    assert isinstance(egg_entry['lexeme_string'], str), "Lexeme string should be a string."

def test_add_egg_to_lipstick():
    """Test the add_egg_to_lipstick function."""
    egg_entry = init_hatched_egg(egg, 'cat', lipstick=lipstick, flag_lexeme=True)
    new_lipstick = add_egg_to_lipstick(egg_entry, lipstick)
    
    assert 'cat' in new_lipstick['word_ul'].values, "New word should be added to lipstick DataFrame."
    assert new_lipstick.shape[0] == lipstick.shape[0] + 1, "New lipstick DataFrame should have one more row than the original."
    assert new_lipstick.loc[new_lipstick['word_ul'] == 'cat', 'n_id'].values[0] == egg_entry['n_id'], "n_id should match the egg entry."

def test_get_single_lexeme():
    """Test the get_single_lexeme function."""
    lip_entry = lipstick.iloc[0]  # Get the first entry in the lipstick DataFrame
    lexeme_string = get_single_lexeme(lip_entry)
    
    assert isinstance(lexeme_string, str), "Lexeme string should be a string."
    assert len(lexeme_string) > 0, "Lexeme string should not be empty."
    print(f"Lexeme string for {lip_entry['word_ll']}: {get_display(lexeme_string)}")

def run_tests():
    """Run all tests."""
    test_get_random_nid()
    test_init_hatched_egg()
    test_add_egg_to_lipstick()
    print("All tests passed!")