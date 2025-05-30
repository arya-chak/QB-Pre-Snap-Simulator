"""
Play Simulator
Author: Arya Chakraborty

NOT BEING USED ANYMORE!
Simulates offensive plays against defensive scenarios, determining success rates and outcomes based on play appropriateness and defensive matchups.
Has a mixed success rate + risk modifier system.
"""

import random
import json

class PlaySimulator:
    def __init__(self):
        """Initialize the Play Simulator with risk modifiers and outcome templates"""
        
        # Risk modifiers based on play appropriateness
        self.risk_modifiers = {
            "Perfect": {
                "base_success_modifier": 0,
                "interception_risk": 2,
                "sack_risk": 5,
                "big_play_bonus": 5,
                "fumble_risk": 1
            },
            "Good": {
                "base_success_modifier": -5,
                "interception_risk": 5,
                "sack_risk": 8,
                "big_play_bonus": 3,
                "fumble_risk": 2
            },
            "Average": {
                "base_success_modifier": -15,
                "interception_risk": 8,
                "sack_risk": 12,
                "big_play_bonus": 0,
                "fumble_risk": 3
            },
            "Poor": {
                "base_success_modifier": -25,
                "interception_risk": 12,
                "sack_risk": 18,
                "big_play_bonus": -5,
                "fumble_risk": 5
            },
            "Terrible": {
                "base_success_modifier": -40,
                "interception_risk": 20,
                "sack_risk": 25,
                "big_play_bonus": -10,
                "fumble_risk": 8
            },
            "Overkill": {
                "base_success_modifier": -10,  # Slight penalty for complexity
                "interception_risk": 15,        # Higher risk for unnecessary deep throws
                "sack_risk": 12,               # Longer developing plays
                "big_play_bonus": 25,          # But big reward potential
                "fumble_risk": 3
            }
        }
        
        # Base success rates for play types
        self.base_success_rates = {
            "Perfect": 92,
            "Good": 78,
            "Average": 55,
            "Poor": 28,
            "Terrible": 15,
            "Overkill": 75  # Still decent because play exploits defense
        }
    
    def generate_minimum_yards(self):
        """Generate random minimum yards needed (1-15 yards)"""
        return random.randint(1, 15)
    
    def determine_yard_range_category(self, minimum_yards):
        """Determine yard range category"""
        if minimum_yards <= 3:
            return "short"
        elif minimum_yards <= 8:
            return "medium"
        else:
            return "long"
    
    def get_play_appropriateness(self, offensive_play, defensive_scenario, yard_range):
        """
        Determine play appropriateness based on offensive play vs defensive scenario for yard range
        This would normally be populated from our JSON analysis, but for now using examples
        """
        
        # This is a simplified example - in full implementation, this would be
        # a comprehensive lookup table based on our JSON data
        
        play_name = offensive_play.get("name", "").lower()
        defense_coverage = defensive_scenario.get("coverage_name", "").lower()
        
        # Example logic for demonstration
        if "four_verticals" in play_name:
            if "cover_2" in defense_coverage:
                if yard_range == "short":
                    return "Overkill"  # Works but unnecessary
                elif yard_range == "long":
                    return "Perfect"   # Exploits Cover 2 hole
                else:
                    return "Good"      # Still works
            elif "cover_4" in defense_coverage:
                return "Terrible"      # Quarters coverage shuts it down
        
        elif "slant" in play_name or "quick" in play_name:
            if yard_range == "short":
                return "Perfect"       # Ideal for short yardage
            elif yard_range == "long":
                return "Poor"          # Not enough for long yardage
        
        elif "power" in play_name or "iso" in play_name:
            if "nickel" in defense_coverage or "dime" in defense_coverage:
                if yard_range == "short":
                    return "Perfect"   # Great vs light box
                else:
                    return "Good"      # Still solid
            elif "46" in defense_coverage:
                return "Terrible"      # Terrible vs stacked box
        
        # Default to average if no specific matchup
        return "Average"
    
    def calculate_final_success_rate(self, base_category, offensive_play, defensive_scenario):
        """Calculate final success rate with all modifiers"""
        base_rate = self.base_success_rates[base_category]
        modifiers = self.risk_modifiers[base_category]
        
        # Apply base modifier
        final_rate = base_rate + modifiers["base_success_modifier"]
        
        # Additional modifiers based on play/defense matchup could go here
        # For example, RPO vs disciplined defense, play action vs run-focused LBs
        
        # Ensure rate stays within bounds
        final_rate = max(5, min(95, final_rate))
        
        return final_rate
    
    def determine_outcome_type(self, success_rate, category, play_type):
        """Determine what type of outcome occurs"""
        roll = random.randint(1, 100)
        modifiers = self.risk_modifiers[category]
        
        # Check for turnovers first (most dramatic outcomes)
        if play_type == "pass":
            int_chance = modifiers["interception_risk"]
            if roll <= int_chance:
                return "interception"
        
        if play_type == "run":
            fumble_chance = modifiers["fumble_risk"]
            if roll <= fumble_chance:
                return "fumble"
        
        # Check for sacks (pass plays only)
        if play_type == "pass":
            sack_chance = modifiers["sack_risk"]
            if roll <= sack_chance + int_chance:  # Cumulative probability
                return "sack"
        
        # Check for basic success
        total_failure_chance = (modifiers["interception_risk"] + modifiers["sack_risk"] + 
                               modifiers["fumble_risk"] + (100 - success_rate))
        
        if roll <= 100 - total_failure_chance:
            # Determine if it's a big play
            big_play_chance = 15 + modifiers["big_play_bonus"]  # Base 15% for big plays
            if random.randint(1, 100) <= big_play_chance:
                return "big_play_success"
            else:
                return "success"
        
        # Default to failure
        return "failure"
    
    def calculate_yards_gained(self, outcome_type, minimum_yards, target_yards, category):
        """Calculate yards gained based on outcome"""
        if outcome_type == "interception":
            return random.randint(-15, -5)  # Interception return yards
        
        elif outcome_type == "fumble":
            return random.randint(-8, 0)    # Fumble lost
        
        elif outcome_type == "sack":
            return random.randint(-12, -3)  # Sack yardage
        
        elif outcome_type == "big_play_success":
            if category == "Overkill":
                return random.randint(target_yards + 5, target_yards + 25)  # Big overkill gain
            else:
                return random.randint(target_yards + 3, target_yards + 15)  # Normal big play
        
        elif outcome_type == "success":
            if category == "Perfect":
                return random.randint(minimum_yards, minimum_yards + 5)     # Appropriate gain
            elif category == "Overkill":
                return random.randint(minimum_yards + 3, minimum_yards + 12) # More than needed
            else:
                return random.randint(minimum_yards - 1, minimum_yards + 3)  # Close to target
        
        else:  # failure
            return random.randint(0, minimum_yards - 1)  # Didn't get enough
    
    def generate_result_description(self, outcome_type, yards_gained, minimum_yards, 
                                  offensive_play, category):
        """Generate descriptive text for the play result"""
        play_name = offensive_play.get("name", "Selected play")
        play_type = offensive_play.get("type", "play")
        
        if outcome_type == "interception":
            return f"INTERCEPTION! {play_name} was picked off and returned for {abs(yards_gained)} yards. The defense read the route perfectly."
        
        elif outcome_type == "fumble":
            return f"FUMBLE! {play_name} resulted in a fumble. Lost {abs(yards_gained)} yards."
        
        elif outcome_type == "sack":
            return f"SACK! Quarterback was brought down for a {abs(yards_gained)}-yard loss. {play_name} took too long to develop."
        
        elif outcome_type == "big_play_success":
            if category == "Overkill":
                return f"BIG PLAY! {play_name} succeeded for {yards_gained} yards. You only needed {minimum_yards} yards - overkill but it worked!"
            else:
                return f"BIG PLAY! {play_name} was successful for {yards_gained} yards. Great execution!"
        
        elif outcome_type == "success":
            if yards_gained >= minimum_yards:
                if category == "Overkill":
                    return f"SUCCESS! {play_name} gained {yards_gained} yards. You needed {minimum_yards} - overkill but effective."
                else:
                    return f"SUCCESS! {play_name} gained {yards_gained} yards. You needed {minimum_yards} yards - good call!"
            else:
                return f"CLOSE! {play_name} gained {yards_gained} yards, just short of the {minimum_yards} yards needed."
        
        else:  # failure
            return f"FAILURE! {play_name} was unsuccessful, gaining only {yards_gained} yards. You needed {minimum_yards} yards."
    
    def simulate_play(self, defensive_scenario, offensive_play, minimum_yards=None):
        """
        Main simulation function - takes defensive scenario and offensive play,
        returns detailed result
        """
        
        if minimum_yards is None:
            minimum_yards = self.generate_minimum_yards()
        
        yard_range = self.determine_yard_range_category(minimum_yards)
        category = self.get_play_appropriateness(offensive_play, defensive_scenario, yard_range)
        
        success_rate = self.calculate_final_success_rate(category, offensive_play, defensive_scenario)
        
        play_type = offensive_play.get("type", "play")
        outcome_type = self.determine_outcome_type(success_rate, category, play_type)
        
        # Get target yards from play data if available
        target_yards = offensive_play.get("target_yards", minimum_yards + 3)
        
        yards_gained = self.calculate_yards_gained(outcome_type, minimum_yards, target_yards, category)
        
        description = self.generate_result_description(outcome_type, yards_gained, minimum_yards, 
                                                     offensive_play, category)
        
        # Determine overall success
        overall_success = yards_gained >= minimum_yards and outcome_type not in ["interception", "fumble"]
        
        return {
            "minimum_yards_needed": minimum_yards,
            "yards_gained": yards_gained,
            "overall_success": overall_success,
            "outcome_type": outcome_type,
            "appropriateness_category": category,
            "success_rate_used": success_rate,
            "description": description,
            "yard_range": yard_range
        }

def main():
    """Test the Play Simulator"""
    simulator = PlaySimulator()
    
    # Example test scenarios
    test_scenarios = [
        {
            "offensive_play": {
                "name": "Four Verticals",
                "type": "pass",
                "target_yards": 18
            },
            "defensive_scenario": {
                "coverage_name": "cover_2_zone"
            }
        },
        {
            "offensive_play": {
                "name": "Quick Slant",
                "type": "pass", 
                "target_yards": 6
            },
            "defensive_scenario": {
                "coverage_name": "cover_0_blitz"
            }
        },
        {
            "offensive_play": {
                "name": "Power Run",
                "type": "run",
                "target_yards": 4
            },
            "defensive_scenario": {
                "coverage_name": "nickel_defense"
            }
        }
    ]
    
    print("="*60)
    print("PLAY SIMULATOR TEST")
    print("="*60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nTest Scenario {i}:")
        print(f"Play: {scenario['offensive_play']['name']}")
        print(f"vs {scenario['defensive_scenario']['coverage_name'].replace('_', ' ').title()}")
        
        # Run simulation multiple times to show variety
        for j in range(3):
            result = simulator.simulate_play(
                scenario["defensive_scenario"], 
                scenario["offensive_play"]
            )
            
            print(f"\n  Attempt {j+1}:")
            print(f"    Needed: {result['minimum_yards_needed']} yards")
            print(f"    Category: {result['appropriateness_category']}")
            print(f"    Success Rate: {result['success_rate_used']}%")
            print(f"    Result: {result['description']}")
            print(f"    Overall Success: {'✓' if result['overall_success'] else '✗'}")

if __name__ == "__main__":
    main()