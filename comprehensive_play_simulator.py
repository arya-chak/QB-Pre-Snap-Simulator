"""
Camprehensive Play Simulator
Author: Arya Chakraborty

Simulates offensive plays against defensive scenarios, determining success rates and outcomes based on play appropriateness and defensive matchups.
Has a mixed success rate + risk modifier system. Has full keyword matching system.
"""

import random
import json
import re

class ComprehensivePlaySimulator:
    def __init__(self):
        """Initialize the comprehensive play simulator with keyword matching"""
        
        # Yard range definitions
        self.yard_ranges = {
            "short": (1, 3),    # Short yardage
            "medium": (4, 6),   # Medium yardage  
            "long": (7, 15)     # Long yardage
        }
        
        # Keyword mapping for matching offensive plays to defensive scenarios
        self.keyword_mapping = {
            # Formation matching
            "formations": {
                "4-3": ["4-3", "four_three", "base"],
                "3-4": ["3-4", "three_four"],
                "5-2": ["5-2", "five_two"],
                "4-4": ["4-4", "four_four"], 
                "46": ["46", "forty_six", "stacked", "eight_in_box"],
                "nickel": ["nickel", "five_db", "light_box"],
                "dime": ["dime", "six_db", "six_dbs", "pass_coverage"]
            },
            
            # Coverage matching
            "coverages": {
                "cover_0": ["cover_0", "man_no_help", "all_out", "aggressive_coverage"],
                "cover_1": ["cover_1", "man_coverage", "single_high", "tight_coverage"],
                "cover_2": ["cover_2", "zone", "deep_split", "underneath_soft", "linebacker_holes", "deep_middle_hole"],
                "cover_3": ["cover_3", "single_safety", "zone_underneath", "seam_routes", "crossing_routes"],
                "cover_4": ["cover_4", "quarters", "deep_help", "deep_coverage"],
                "man": ["man_coverage", "tight_defenders", "individual", "bump", "press"],
                "zone": ["zone_coverage", "soft", "underneath", "windows", "holes"]
            },
            
            # Pressure/Blitz matching
            "pressure": {
                "blitz": ["blitz", "pressure", "rush", "aggressive", "all_out"],
                "spy": ["spy", "linebacker_on_qb", "qb_contain"],
                "robber": ["robber", "robber_coverage"],
                "no_pressure": ["base", "standard", "four_man", "three_man"]
            },
            
            # Personnel/Box matching
            "personnel": {
                "heavy_box": ["heavy_box", "stacked", "goal_line", "eight_in_box"],
                "light_box": ["light_box", "spread_out", "pass_focused", "six_dbs"],
                "run_support": ["run_support", "run_focused", "aggressive_safeties"]
            },
            
            # Situational matching  
            "situations": {
                "short_yardage": ["goal_line", "short_yardage", "sneak"],
                "obvious_passing": ["obvious_passing", "prevent", "two_minute"],
                "red_zone": ["red_zone", "compressed", "goal_line"],
                "trips_concepts": ["trips", "overload", "flood", "bunch"]
            }
        }
        
        # Risk modifiers (same as before but enhanced)
        self.risk_modifiers = {
            "Perfect": {
                "base_success_modifier": 5,
                "interception_risk": 2,
                "sack_risk": 3,
                "big_play_bonus": 8,
                "fumble_risk": 1
            },
            "Good": {
                "base_success_modifier": 0,
                "interception_risk": 4,
                "sack_risk": 6,
                "big_play_bonus": 5,
                "fumble_risk": 2
            },
            "Average": {
                "base_success_modifier": -10,
                "interception_risk": 8,
                "sack_risk": 10,
                "big_play_bonus": 2,
                "fumble_risk": 3
            },
            "Poor": {
                "base_success_modifier": -20,
                "interception_risk": 15,
                "sack_risk": 18,
                "big_play_bonus": -3,
                "fumble_risk": 6
            },
            "Terrible": {
                "base_success_modifier": -35,
                "interception_risk": 25,
                "sack_risk": 25,
                "big_play_bonus": -8,
                "fumble_risk": 10
            },
            "Overkill": {
                "base_success_modifier": -5,
                "interception_risk": 12,
                "sack_risk": 8,
                "big_play_bonus": 20,
                "fumble_risk": 3
            }
        }
        
        # Base success rates
        self.base_success_rates = {
            "Perfect": 90,
            "Good": 75,
            "Average": 55,
            "Poor": 30,
            "Terrible": 15,
            "Overkill": 70
        }
    
    def generate_minimum_yards(self):
        """Generate random minimum yards needed (1-15 yards)"""
        return random.randint(1, 15)
    
    def determine_yard_range_category(self, minimum_yards):
        """Determine yard range category"""
        if minimum_yards <= 3:
            return "short"
        elif minimum_yards <= 6:
            return "medium"
        else:
            return "long"
    
    def extract_keywords_from_text(self, text):
        """Extract keywords from text string for matching"""
        # Convert to lowercase and split on common separators
        text = text.lower().replace('-', '_')
        words = re.split(r'[_\s]+', text)
        return words
    
    def calculate_keyword_matches(self, play_terms, defensive_scenario):
        """Calculate how well play terms match the defensive scenario"""
        # Extract defensive characteristics
        formation_name = defensive_scenario.get("formation_name", "").lower()
        coverage_name = defensive_scenario.get("coverage_name", "").lower()
        coverage_type = defensive_scenario.get("coverage_data", {}).get("coverage_type", "").lower()
        blitz_name = defensive_scenario.get("blitz_name", "").lower()
        
        # Combine all defensive characteristics
        defensive_text = f"{formation_name} {coverage_name} {coverage_type} {blitz_name}"
        defensive_keywords = self.extract_keywords_from_text(defensive_text)
        
        match_score = 0
        total_terms = len(play_terms)
        
        if total_terms == 0:
            return 0
        
        # Check each play term against defensive scenario
        for term in play_terms:
            term_keywords = self.extract_keywords_from_text(term)
            
            # Direct keyword matching
            for keyword in term_keywords:
                if keyword in defensive_keywords:
                    match_score += 2  # Direct match bonus
                
                # Check against our keyword mapping
                for category, mappings in self.keyword_mapping.items():
                    for mapping_key, synonyms in mappings.items():
                        if keyword in synonyms:
                            # Check if the mapping matches defensive scenario
                            if any(syn in defensive_keywords for syn in synonyms):
                                match_score += 1  # Semantic match bonus
        
        # Normalize score (0-100 scale)
        normalized_score = min(100, (match_score / total_terms) * 25)
        return normalized_score
    
    def get_play_appropriateness_comprehensive(self, offensive_play, defensive_scenario, yard_range):
        """
        Comprehensive play appropriateness system using keyword matching
        """
        
        # Get play characteristics from the full play data
        play_best_against = offensive_play.get("best_against", [])
        play_worst_against = offensive_play.get("worst_against", [])
        play_strengths = offensive_play.get("strengths", [])
        play_weaknesses = offensive_play.get("weaknesses", [])
        
        # Calculate match scores
        best_match_score = self.calculate_keyword_matches(play_best_against, defensive_scenario)
        worst_match_score = self.calculate_keyword_matches(play_worst_against, defensive_scenario)
        
        # Start with neutral score
        appropriateness_score = 50
        
        # Adjust based on best_against matches
        appropriateness_score += best_match_score * 0.8
        
        # Penalize for worst_against matches
        appropriateness_score -= worst_match_score * 0.8
        
        # Yard range adjustments based on play type
        play_name = offensive_play.get("name", "").lower()
        play_concept = offensive_play.get("concept", "").lower()
        play_type = offensive_play.get("type", "run")
        
        # Yard range specific adjustments
        if yard_range == "short":
            # Short yardage favors power concepts
            if any(keyword in play_name or keyword in play_concept 
                   for keyword in ["power", "dive", "sneak", "iso", "wedge"]):
                appropriateness_score += 15
            # Penalize overkill deep concepts
            if any(keyword in play_name or keyword in play_concept 
                   for keyword in ["vertical", "deep", "seam", "four_verticals"]):
                appropriateness_score -= 10
                
        elif yard_range == "medium":
            # Medium yardage is balanced
            if any(keyword in play_name or keyword in play_concept 
                   for keyword in ["stick", "out", "slant", "zone"]):
                appropriateness_score += 8
                
        elif yard_range == "long":
            # Long yardage favors passing and big play concepts
            if play_type == "pass" and any(keyword in play_name or keyword in play_concept 
                                         for keyword in ["vertical", "deep", "seam", "crossing"]):
                appropriateness_score += 20
            # Penalize short concepts
            if any(keyword in play_name or keyword in play_concept 
                   for keyword in ["dive", "sneak", "power", "draw"]):
                appropriateness_score -= 15
        
        # Special case detection for overkill
        is_overkill = False
        if yard_range == "short" and play_type == "pass":
            if any(keyword in play_name or keyword in play_concept 
                   for keyword in ["vertical", "deep", "seam"]):
                is_overkill = True
        
        # Ensure score stays within bounds
        appropriateness_score = max(0, min(100, appropriateness_score))
        
        # Convert score to category
        if is_overkill:
            return "Overkill"
        elif appropriateness_score >= 85:
            return "Perfect"
        elif appropriateness_score >= 70:
            return "Good"
        elif appropriateness_score >= 40:
            return "Average"
        elif appropriateness_score >= 20:
            return "Poor"
        else:
            return "Terrible"
    
    def calculate_final_success_rate(self, base_category, offensive_play, defensive_scenario):
        """Calculate final success rate with all modifiers"""
        base_rate = self.base_success_rates[base_category]
        modifiers = self.risk_modifiers[base_category]
        
        # Apply base modifier
        final_rate = base_rate + modifiers["base_success_modifier"]
        
        # Additional contextual modifiers
        play_type = offensive_play.get("type", "play")
        
        # RPO plays get bonus vs certain defenses
        if "rpo" in offensive_play.get("name", "").lower():
            if "aggressive" in str(defensive_scenario.get("blitz_data", {})):
                final_rate += 5
        
        # Quick game gets bonus vs pressure
        if "quick" in offensive_play.get("name", "").lower():
            if "blitz" in defensive_scenario.get("blitz_name", ""):
                final_rate += 8
        
        # Ensure rate stays within bounds
        final_rate = max(5, min(95, final_rate))
        
        return final_rate
    
    def determine_outcome_type(self, success_rate, category, play_type):
        """Determine what type of outcome occurs"""
        roll = random.randint(1, 100)
        modifiers = self.risk_modifiers[category]
        
        # Check for turnovers first
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
            if roll <= sack_chance + int_chance:
                return "sack"
        
        # Check for success
        if roll <= success_rate:
            # Determine if it's a big play
            big_play_chance = 15 + modifiers["big_play_bonus"]
            if random.randint(1, 100) <= big_play_chance:
                return "big_play_success"
            else:
                return "success"
        
        # Default to failure
        return "failure"
    
    def calculate_yards_gained(self, outcome_type, minimum_yards, target_yards, category):
        """Calculate yards gained based on outcome"""
        if outcome_type == "interception":
            return random.randint(-15, -5)
        elif outcome_type == "fumble":
            return random.randint(-8, 0)
        elif outcome_type == "sack":
            return random.randint(-12, -3)
        elif outcome_type == "big_play_success":
            if category == "Overkill":
                return random.randint(target_yards + 8, target_yards + 25)
            else:
                return random.randint(target_yards + 5, target_yards + 15)
        elif outcome_type == "success":
            if category == "Perfect":
                return random.randint(minimum_yards, minimum_yards + 5)
            elif category == "Overkill":
                return random.randint(minimum_yards + 5, minimum_yards + 15)
            else:
                return random.randint(minimum_yards - 1, minimum_yards + 4)
        else:  # failure
            return random.randint(0, minimum_yards - 1)
    
    def generate_result_description(self, outcome_type, yards_gained, minimum_yards, 
                                  offensive_play, category, defensive_scenario):
        """Generate descriptive text for the play result"""
        play_name = offensive_play.get("name", "Selected play")
        play_type = offensive_play.get("type", "play")
        
        # Get some defensive context
        defense_name = defensive_scenario.get("formation_data", {}).get("formation_name", "Defense")
        coverage_name = defensive_scenario.get("coverage_data", {}).get("name", "coverage")
        
        if outcome_type == "interception":
            return f"INTERCEPTION! {play_name} was picked off by the {defense_name} {coverage_name}. The defense read the route perfectly and returned it for {abs(yards_gained)} yards."
        
        elif outcome_type == "fumble":
            return f"FUMBLE! {play_name} resulted in a fumble against the {defense_name}. Lost {abs(yards_gained)} yards."
        
        elif outcome_type == "sack":
            return f"SACK! Quarterback was brought down for a {abs(yards_gained)}-yard loss. The {defense_name} pass rush got home before {play_name} could develop."
        
        elif outcome_type == "big_play_success":
            if category == "Overkill":
                return f"BIG PLAY! {play_name} succeeded for {yards_gained} yards against {coverage_name}. You only needed {minimum_yards} yards - overkill but it worked spectacularly!"
            else:
                return f"BIG PLAY! {play_name} was perfectly executed for {yards_gained} yards. Great call against the {coverage_name}!"
        
        elif outcome_type == "success":
            if yards_gained >= minimum_yards:
                if category == "Overkill":
                    return f"SUCCESS! {play_name} gained {yards_gained} yards against {coverage_name}. You needed {minimum_yards} yards - overkill but effective."
                elif category == "Perfect":
                    return f"SUCCESS! {play_name} gained {yards_gained} yards. Perfect call against the {coverage_name} - you needed {minimum_yards} yards."
                else:
                    return f"SUCCESS! {play_name} gained {yards_gained} yards against the {defense_name}. You needed {minimum_yards} yards - good execution!"
            else:
                return f"CLOSE! {play_name} gained {yards_gained} yards, just short of the {minimum_yards} yards needed against the {coverage_name}."
        
        else:  # failure
            return f"FAILURE! {play_name} was unsuccessful against the {coverage_name}, gaining only {yards_gained} yards. You needed {minimum_yards} yards."
    
    def simulate_play(self, defensive_scenario, offensive_play, minimum_yards=None):
        """
        Main simulation function using comprehensive matching system
        """
        
        if minimum_yards is None:
            minimum_yards = self.generate_minimum_yards()
        
        yard_range = self.determine_yard_range_category(minimum_yards)
        category = self.get_play_appropriateness_comprehensive(offensive_play, defensive_scenario, yard_range)
        
        success_rate = self.calculate_final_success_rate(category, offensive_play, defensive_scenario)
        
        play_type = offensive_play.get("type", "play")
        outcome_type = self.determine_outcome_type(success_rate, category, play_type)
        
        # Get target yards from play data if available
        target_yards = offensive_play.get("target_yards", minimum_yards + 3)
        
        yards_gained = self.calculate_yards_gained(outcome_type, minimum_yards, target_yards, category)
        
        description = self.generate_result_description(outcome_type, yards_gained, minimum_yards, 
                                                     offensive_play, category, defensive_scenario)
        
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
            "yard_range": yard_range,
            "defensive_scenario_summary": f"{defensive_scenario.get('formation_data', {}).get('formation_name', 'Defense')} {defensive_scenario.get('coverage_data', {}).get('name', 'Coverage')}"
        }

def main():
    """Test the comprehensive play simulator"""
    # This would normally be called with real data from the engines
    simulator = ComprehensivePlaySimulator()
    
    # Example test with realistic data structure
    test_scenario = {
        "formation_name": "nickel",
        "coverage_name": "cover_2_zone", 
        "coverage_data": {"coverage_type": "zone"},
        "blitz_name": "base_coverage",
        "formation_data": {"formation_name": "Nickel Defense"},
        "coverage_data": {"name": "Cover 2 Zone"}
    }
    
    test_play = {
        "name": "Four Verticals",
        "type": "pass",
        "best_against": ["cover_2_zone_deep_middle_hole", "nickel_defense_light_box"],
        "worst_against": ["cover_4_quarters_coverage", "dime_defense_six_dbs"],
        "target_yards": 18
    }
    
    print("="*60)
    print("COMPREHENSIVE PLAY SIMULATOR TEST")
    print("="*60)
    
    for i in range(5):
        result = simulator.simulate_play(test_scenario, test_play)
        
        print(f"\nTest {i+1}:")
        print(f"Needed: {result['minimum_yards_needed']} yards ({result['yard_range']})")
        print(f"Category: {result['appropriateness_category']}")
        print(f"Success Rate: {result['success_rate_used']}%") 
        print(f"Result: {result['description']}")
        print(f"Success: {'✓' if result['overall_success'] else '✗'}")

if __name__ == "__main__":
    main()