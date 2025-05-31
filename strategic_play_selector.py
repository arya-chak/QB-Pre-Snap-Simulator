"""
Strategic Play Selector
Author: Arya Chakraborty

Selects 5 plays representing different appropriateness categories against a specific defensive scenario.
This creates a more strategic decision-making experience where users choose between risk/reward options.
"""

import random
from comprehensive_play_simulator import ComprehensivePlaySimulator

class StrategicPlaySelector:
    def __init__(self, offense_engine, simulator):
        """Initialize with offense engine and simulator"""
        self.offense_engine = offense_engine
        self.simulator = simulator
        
        # Target categories for strategic selection
        self.target_categories = ['Perfect', 'Good', 'Average', 'Poor', 'Terrible']
        
    def evaluate_all_plays_against_defense(self, defensive_scenario, minimum_yards):
        """Evaluate every available play against the defensive scenario"""
        yard_range = self.simulator.determine_yard_range_category(minimum_yards)
        
        play_evaluations = []
        
        # Go through every formation
        for formation_name, formation_data in self.offense_engine.formations.items():
            plays = self.offense_engine.get_formation_plays(formation_name)
            
            for play in plays:
                # Get full play details for comprehensive analysis
                full_play_details = self.offense_engine.get_play_full_details(
                    play['formation'], 
                    play['key']
                )
                
                if full_play_details:
                    comprehensive_play_data = {**play, **full_play_details}
                else:
                    comprehensive_play_data = play
                
                # Get appropriateness category
                category = self.simulator.get_play_appropriateness_comprehensive(
                    comprehensive_play_data, defensive_scenario, yard_range
                )
                
                play_evaluation = {
                    'play_data': play,
                    'comprehensive_data': comprehensive_play_data,
                    'appropriateness_category': category,
                    'formation_name': formation_name,
                    'success_rate': self.simulator.calculate_final_success_rate(
                        category, comprehensive_play_data, defensive_scenario
                    )
                }
                
                play_evaluations.append(play_evaluation)
        
        return play_evaluations
    
    def group_plays_by_category(self, play_evaluations):
        """Group plays by their appropriateness category"""
        categorized_plays = {
            'Perfect': [],
            'Good': [],
            'Average': [],
            'Poor': [],
            'Terrible': [],
            'Overkill': []
        }
        
        for evaluation in play_evaluations:
            category = evaluation['appropriateness_category']
            categorized_plays[category].append(evaluation)
        
        return categorized_plays
    
    def select_best_play_from_category(self, plays_in_category):
        """Select the best play from a category based on success rate and diversity"""
        if not plays_in_category:
            return None
        
        # Sort by success rate (descending)
        sorted_plays = sorted(plays_in_category, key=lambda x: x['success_rate'], reverse=True)
        
        # For variety, sometimes pick from top 3 instead of always the best
        if len(sorted_plays) >= 3:
            return random.choice(sorted_plays[:3])
        else:
            return sorted_plays[0]
    
    def ensure_play_diversity(self, selected_plays):
        """Ensure we have diverse play types and formations"""
        # Check for formation diversity
        formations_used = [play['formation_name'] for play in selected_plays if play]
        play_types_used = [play['play_data']['type'] for play in selected_plays if play]
        
        # If we have too much repetition, try to diversify
        formation_counts = {}
        type_counts = {}
        
        for formation in formations_used:
            formation_counts[formation] = formation_counts.get(formation, 0) + 1
        
        for play_type in play_types_used:
            type_counts[play_type] = type_counts.get(play_type, 0) + 1
        
        return {
            'formation_diversity': len(formation_counts),
            'type_diversity': len(type_counts),
            'formation_distribution': formation_counts,
            'type_distribution': type_counts
        }
    
    def get_strategic_play_selection(self, defensive_scenario, minimum_yards):
        """
        Main function: Get 5 strategic plays representing different risk/reward levels
        """
        
        # Evaluate all plays
        all_evaluations = self.evaluate_all_plays_against_defense(defensive_scenario, minimum_yards)
        
        # Group by category
        categorized_plays = self.group_plays_by_category(all_evaluations)
        
        # Select one play from each target category
        strategic_selection = {}
        
        for category in self.target_categories:
            if categorized_plays[category]:
                selected_play = self.select_best_play_from_category(categorized_plays[category])
                strategic_selection[category] = selected_play
            else:
                # If no plays in this category, mark as None
                strategic_selection[category] = None
        
        # Handle special case: if we have Overkill plays but missing others
        if not strategic_selection.get('Perfect') and categorized_plays['Overkill']:
            # Use an Overkill play as Perfect if no Perfect exists
            strategic_selection['Perfect'] = self.select_best_play_from_category(categorized_plays['Overkill'])
        
        # Fallback: if any category is missing, try to fill from other categories
        self.fill_missing_categories(strategic_selection, categorized_plays)
        
        # Calculate diversity metrics
        selected_plays = [play for play in strategic_selection.values() if play]
        diversity_info = self.ensure_play_diversity(selected_plays)
        
        return {
            'strategic_plays': strategic_selection,
            'category_counts': {cat: len(plays) for cat, plays in categorized_plays.items()},
            'diversity_info': diversity_info,
            'total_plays_evaluated': len(all_evaluations)
        }
    
    def fill_missing_categories(self, strategic_selection, categorized_plays):
        """Fill any missing categories with plays from available categories"""
        
        # Priority order for substitutions
        substitution_priority = {
            'Perfect': ['Good', 'Overkill', 'Average'],
            'Good': ['Perfect', 'Average', 'Overkill'],
            'Average': ['Good', 'Poor', 'Perfect'],
            'Poor': ['Average', 'Terrible', 'Good'],
            'Terrible': ['Poor', 'Average', 'Good']
        }
        
        for category in self.target_categories:
            if not strategic_selection.get(category):
                # Try to substitute from priority list
                for substitute_category in substitution_priority.get(category, []):
                    if categorized_plays[substitute_category]:
                        # Pick a different play than already selected
                        used_play_keys = {play['play_data']['key'] for play in strategic_selection.values() if play}
                        
                        available_substitutes = [
                            play for play in categorized_plays[substitute_category] 
                            if play['play_data']['key'] not in used_play_keys
                        ]
                        
                        if available_substitutes:
                            strategic_selection[category] = self.select_best_play_from_category(available_substitutes)
                            break
    
    def format_play_for_display(self, play_evaluation):
        """Format a play evaluation for clean display"""
        if not play_evaluation:
            return None
        
        play_data = play_evaluation['play_data']
        formation_name = play_evaluation['formation_name']
        
        formatted_play = {
            'name': play_data['name'],
            'formation': formation_name.replace('-', ' ').title(),
            'type': play_data['type'].title(),
            'concept': play_data['concept'],
            'appropriateness': play_evaluation['appropriateness_category'],
            'success_rate': f"{play_evaluation['success_rate']}%",
            'full_data': play_evaluation['comprehensive_data'],  # For simulation
            'risk_level': self.get_risk_description(play_evaluation['appropriateness_category'])
        }
        
        # Add type-specific details
        if play_data['type'] == 'pass':
            formatted_play['protection'] = play_data.get('protection', 'N/A')
            formatted_play['routes'] = play_data.get('routes', {})
        else:
            formatted_play['blocking'] = play_data.get('blocking_scheme', 'N/A').replace('_', ' ').title()
            formatted_play['ball_carrier'] = play_data.get('ball_carrier', 'N/A').replace('_', ' ').title()
        
        return formatted_play
    
    def get_risk_description(self, category):
        """Get risk/reward description for each category"""
        descriptions = {
            'Perfect': 'High Success, Low Risk - Exploits defensive weakness',
            'Good': 'Good Success, Low Risk - Solid matchup advantage', 
            'Average': 'Moderate Success, Moderate Risk - Neutral matchup',
            'Poor': 'Low Success, High Risk - Defense has advantage',
            'Terrible': 'Very Low Success, Very High Risk - Defense counters this play',
            'Overkill': 'High Success, Moderate Risk - More complex than needed'
        }
        return descriptions.get(category, 'Unknown risk level')

def main():
    """Test the strategic play selector"""
    import sys
    import os
    
    # Add path for imports
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from defense_engine import DefenseEngine
    from offense_engine import OffenseEngine
    from comprehensive_play_simulator import ComprehensivePlaySimulator
    
    # Initialize engines
    print("Initializing Strategic Play Selector Test...")
    print("="*60)
    
    defense_engine = DefenseEngine()
    offense_engine = OffenseEngine()
    simulator = ComprehensivePlaySimulator()
    
    # Load data
    defense_engine.load_all_formations()
    offense_engine.load_all_formations()
    
    # Create selector
    selector = StrategicPlaySelector(offense_engine, simulator)
    
    # Generate test scenario
    defensive_scenario = defense_engine.get_random_scenario()
    minimum_yards = simulator.generate_minimum_yards()
    
    print(f"\nTest Scenario:")
    print(f"Defense: {defensive_scenario['formation_data']['formation_name']} {defensive_scenario['coverage_data']['name']}")
    print(f"Minimum Yards Needed: {minimum_yards}")
    print(f"Yard Range: {simulator.determine_yard_range_category(minimum_yards)}")
    
    # Get strategic selection
    print(f"\nAnalyzing all plays against this defense...")
    result = selector.get_strategic_play_selection(defensive_scenario, minimum_yards)
    
    print(f"\n{'='*60}")
    print("STRATEGIC PLAY SELECTION RESULTS")
    print(f"{'='*60}")
    
    print(f"Total plays evaluated: {result['total_plays_evaluated']}")
    print(f"Category distribution: {result['category_counts']}")
    print(f"Formation diversity: {result['diversity_info']['formation_diversity']}")
    print(f"Type diversity: {result['diversity_info']['type_diversity']}")
    
    print(f"\n5 STRATEGIC PLAY OPTIONS:")
    print("-"*40)
    
    for i, (category, play_eval) in enumerate(result['strategic_plays'].items(), 1):
        if play_eval:
            formatted_play = selector.format_play_for_display(play_eval)
            print(f"\n{i}. {formatted_play['name']} ({formatted_play['appropriateness']})")
            print(f"   Formation: {formatted_play['formation']}")
            print(f"   Type: {formatted_play['type']} - {formatted_play['concept']}")
            print(f"   Success Rate: {formatted_play['success_rate']}")
            print(f"   Risk Level: {formatted_play['risk_level']}")
        else:
            print(f"\n{i}. No {category} play available against this defense")

if __name__ == "__main__":
    main()