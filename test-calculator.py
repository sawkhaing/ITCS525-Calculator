# test-calculator.py
from calculator import expand_percent

def test_expand_percent():
    assert expand_percent("5 + 10%") == "5 + ((10/100)*5)", (
        'Failed on 5 + 10%, result: ' + expand_percent("5 + 10%"))
    assert expand_percent("20 - 30%") == "20 - ((30/100)*20)", (
        'Failed on 20 - 30%, result: ' + expand_percent("20 - 30%"))
    assert expand_percent("15 * 25%") == "15 * (25/100)", (
        'Failed on 15 * 25%, result: ' + expand_percent("15 * 25%"))
    assert expand_percent("40 / 50%") == "40 / (50/100)",(
        'Failed on 40 / 50%, result: ' + expand_percent("40 / 50%"))
    assert expand_percent("3 * 4% + 2 / 1%") == "3 * (4/100) + 2 / (1/100)", (
        'Failed on 3 * 4% + 2 / 1%, result: '+expand_percent("3 * 4% + 2 / 1%"))
    assert expand_percent("100%") == "(100/100)", (
        'Failed on 100%, result: ' + expand_percent("100%"))
    assert expand_percent("10% + 20%") == "(10/100) + (20/100)", (
        'Failed on 10% + 20%, result: ' + expand_percent("10% + 20%"))

if __name__ == "__main__":
    test_expand_percent()
    print("All tests passed!")