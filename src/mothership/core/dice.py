import random

class DiceRoller:
    @staticmethod
    def roll(sides=10, count=1):
        """
        Rolls a die with the specified number of sides.
        
        Args:
            sides (int): Number of sides on the die. Default is 10.
            count (int): Number of dice to roll. Default is 1.
            
        Returns:
            int: The total result of the roll.
        """
        total = 0
        for _ in range(count):
            total += random.randint(1, sides)
        return total
