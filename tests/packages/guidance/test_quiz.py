import json
import pytest

from packages.guidance.quiz import _parse_quiz_json

def test_parse_quiz_json_valid_pure_json():
    # Valid JSON with questions
    data = {
        "questions": [
            {"type": "short_answer", "question": "What is Python?", "answer": "varies", "explanation": "It's a programming language."}
        ]
    }
    json_str = json.dumps(data)
    result = _parse_quiz_json(json_str)
    assert result == data

def test_parse_quiz_json_missing_questions_key():
    # Valid JSON but missing questions key
    data = {
        "topic": "Python"
    }
    json_str = json.dumps(data)
    result = _parse_quiz_json(json_str)
    assert result is None

def test_parse_quiz_json_empty_questions_list():
    # Valid JSON with empty questions list
    data = {
        "questions": []
    }
    json_str = json.dumps(data)
    result = _parse_quiz_json(json_str)
    assert result is None

def test_parse_quiz_json_invalid_json():
    # Invalid JSON string
    json_str = "{ 'questions': ["
    result = _parse_quiz_json(json_str)
    assert result is None

def test_parse_quiz_json_markdown_fenced_json():
    # JSON in markdown block with 'json' tag
    data = {
        "questions": [
            {"type": "multiple_choice", "question": "A?", "options": ["A", "B"], "answer": "A"}
        ]
    }
    json_str = f"```json\n{json.dumps(data)}\n```"
    result = _parse_quiz_json(json_str)
    assert result == data

def test_parse_quiz_json_markdown_fenced_untagged():
    # JSON in untagged markdown block
    data = {
        "questions": [
            {"type": "multiple_choice", "question": "A?", "options": ["A", "B"], "answer": "A"}
        ]
    }
    json_str = f"```\n{json.dumps(data)}\n```"
    result = _parse_quiz_json(json_str)
    assert result == data

def test_parse_quiz_json_markdown_with_whitespace():
    # JSON in markdown block with leading/trailing whitespaces
    data = {
        "questions": [
            {"type": "multiple_choice", "question": "A?", "options": ["A", "B"], "answer": "A"}
        ]
    }
    json_str = f"   \n```json\n{json.dumps(data)}\n```\n   "
    result = _parse_quiz_json(json_str)
    assert result == data

def test_parse_quiz_json_text_before_and_after_markdown():
    # Current implementation only handles markdown formatting if the entire block is the response
    data = {
        "questions": [
            {"type": "multiple_choice", "question": "A?", "options": ["A", "B"], "answer": "A"}
        ]
    }
    json_str = f"Here is your quiz:\n```json\n{json.dumps(data)}\n```\nGood luck!"
    result = _parse_quiz_json(json_str)
    assert result is None
