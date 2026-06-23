"""Test anonymization functions."""

from scripts.anonymize_data import anonymize_text, hash_user_id


def test_anonymize_phone():
    """Test phone number anonymization"""
    text = "联系我：13800138000"
    result = anonymize_text(text)
    assert "[电话]" in result
    assert "13800138000" not in result


def test_anonymize_student_id():
    """Test student ID anonymization"""
    text = "学号：20210001"
    result = anonymize_text(text)
    assert "[学号]" in result
    assert "20210001" not in result


def test_anonymize_dorm():
    """Test dormitory number anonymization"""
    text = "我住在A栋301室"
    result = anonymize_text(text)
    assert "[宿舍号]" in result
    assert "301" not in result


def test_hash_user_id():
    """Test user ID hashing"""
    user_id = "user_12345"
    hashed = hash_user_id(user_id)
    assert hashed.startswith("U_")
    assert len(hashed) == 8  # U_ + 6 hex chars
    # Same input should produce same hash
    assert hash_user_id(user_id) == hashed
