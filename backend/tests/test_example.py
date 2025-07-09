# backend/test_example.py


def test_sample_addition() -> None:
    """
    簡単な足し算をテストし、pytestがテストを検出できるようにします。
    Mypyのチェックもクリアするように、戻り値の型ヒントを追加します。
    """
    print("Running test_sample_addition...")
    assert 1 + 1 == 2, "1 + 1 should equal 2"


def test_truthiness() -> None:
    """
    基本的な真偽値のテスト。
    これもpytestに検出され、Mypyのチェックをパスします。
    """
    print("Running test_truthiness...")
    assert True is True, "True should be True"
