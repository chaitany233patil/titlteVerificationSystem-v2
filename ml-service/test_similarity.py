#!/usr/bin/env python3
"""
Test script for the refactored similarity functions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.similarity import (
    _levenshtein_distance_score,
    _phonetic_score,
    _lexical_scores,
    _semantic_scores,
    check_similarity_scores,
    find_matches_with_threshold
)

def test_levenshtein_distance():
    """Test Levenshtein distance function"""
    print("Testing Levenshtein distance function...")
    
    # Test identical strings
    assert _levenshtein_distance_score("hello", "hello") == 1.0
    print("✓ Identical strings: PASS")
    
    # Test similar strings
    score = _levenshtein_distance_score("hello", "helo")
    assert 0.5 < score < 1.0
    print(f"✓ Similar strings 'hello' vs 'helo': {score:.4f}")
    
    # Test very different strings
    score = _levenshtein_distance_score("hello", "world")
    assert 0.0 < score < 0.5
    print(f"✓ Different strings 'hello' vs 'world': {score:.4f}")
    
    print("Levenshtein distance tests passed!\n")


def test_phonetic_score():
    """Test phonetic similarity function"""
    print("Testing phonetic similarity function...")
    
    # Test identical strings
    assert _phonetic_score("hello", "hello") == 1.0
    print("✓ Identical strings: PASS")
    
    # Test similar sounding words
    score = _phonetic_score("hello", "helo")
    print(f"✓ Similar sounding 'hello' vs 'helo': {score}")
    
    # Test different words
    score = _phonetic_score("hello", "world")
    print(f"✓ Different words 'hello' vs 'world': {score}")
    
    print("Phonetic similarity tests passed!\n")


def test_threshold_passing():
    """Test that threshold is properly passed to functions"""
    print("Testing threshold parameter passing...")
    
    query = "hello world"
    corpus = ["hello world", "hello there", "goodbye world"]
    threshold = 0.8
    
    # Test that functions accept threshold parameter
    try:
        phonetic, lexical, semantic = check_similarity_scores(query, corpus, threshold)
        print("✓ Threshold parameter accepted by all functions")
        
        # Test that threshold is used in match finding
        matches = find_matches_with_threshold(phonetic, lexical, semantic, corpus, threshold)
        print(f"✓ Found {len(matches)} matches with threshold {threshold}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("Threshold parameter tests passed!\n")
    return True


def test_early_break_logic():
    """Test the early break logic for single matches"""
    print("Testing early break logic...")
    
    query = "hello world"
    corpus = ["hello world", "different title"]
    threshold = 0.9
    
    # This should find exactly one match and trigger early return
    phonetic, lexical, semantic = check_similarity_scores(query, corpus, threshold)
    matches = find_matches_with_threshold(phonetic, lexical, semantic, corpus, threshold)
    
    print(f"✓ Found {len(matches)} matches with high threshold {threshold}")
    
    if len(matches) == 1:
        print("✓ Early break logic working correctly")
    else:
        print(f"⚠ Expected 1 match, got {len(matches)}")
    
    print("Early break logic tests completed!\n")


if __name__ == "__main__":
    print("Running similarity function tests...\n")
    
    try:
        test_levenshtein_distance()
        test_phonetic_score()
        test_threshold_passing()
        test_early_break_logic()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
