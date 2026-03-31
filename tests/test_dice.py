from mothership.core.dice import DiceRoller

def test_dice_rolls_1_to_10():
    """Verify that DiceRoller.roll(10) always returns a number between 1 and 10."""
    for _ in range(100):
        result = DiceRoller.roll(10)
        assert 1 <= result <= 10
