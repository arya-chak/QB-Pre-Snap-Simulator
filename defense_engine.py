"""
Defense Engine
Author: Arya Chakraborty

Loads defensive formations from JSON files, generates random defensive scenarios for the user, and displays detailed information about each scenario.
"""

import json
import os
import random

class DefenseEngine:
    def __init__(self):
        """Initialize the Defense Engine"""
        self.formations = {}
        self.data_path = "data/defenses/"
        self.available_formations = ["4-3", "3-4", "5-2", "4-4", "46", "nickel", "dime"]
    
    def load_formation(self, formation_name):
        """Load a specific defensive formation from JSON file"""
        try:
            file_path = os.path.join(self.data_path, f"{formation_name}.json")
            with open(file_path, 'r') as file:
                formation_data = json.load(file)
                self.formations[formation_name] = formation_data
                return formation_data
        except FileNotFoundError:
            print(f"Error: Could not find {formation_name}.json in {self.data_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {formation_name}.json")
            return None
    
    def load_all_formations(self):
        """Load all available defensive formations"""
        print("Loading defensive formations...")
        for formation in self.available_formations:
            result = self.load_formation(formation)
            if result:
                print(f"✓ Loaded {formation} defense")
            else:
                print(f"✗ Failed to load {formation} defense")
        print(f"\nTotal formations loaded: {len(self.formations)}")
    
    def get_random_scenario(self):
        """Get a random defensive scenario from all loaded formations"""
        if not self.formations:
            print("No formations loaded! Please load formations first.")
            return None
        
        # Randomly select a formation
        formation_name = random.choice(list(self.formations.keys()))
        formation_data = self.formations[formation_name]
        
        # Randomly select a coverage
        coverage_name = random.choice(list(formation_data["coverages"].keys()))
        coverage_data = formation_data["coverages"][coverage_name]
        
        # Randomly select a blitz package
        blitz_name = random.choice(list(coverage_data["blitz_packages"].keys()))
        blitz_data = coverage_data["blitz_packages"][blitz_name]
        
        return {
            "formation_name": formation_name,
            "formation_data": formation_data,
            "coverage_name": coverage_name,
            "coverage_data": coverage_data,
            "blitz_name": blitz_name,
            "blitz_data": blitz_data
        }
    
    def display_scenario(self, scenario):
        """Display a defensive scenario to the user"""
        if not scenario:
            return
        
        print("=" * 60)
        print("DEFENSIVE SCENARIO")
        print("=" * 60)
        
        # Formation info
        print(f"Formation: {scenario['formation_data']['formation_name']}")
        print(f"Personnel: {scenario['formation_data']['personnel']}")
        print(f"Description: {scenario['formation_data']['description']}")
        print()
        
        # Coverage info
        print(f"Coverage: {scenario['coverage_data']['name']}")
        print(f"Type: {scenario['coverage_data']['coverage_type'].title()}")
        print(f"Description: {scenario['coverage_data']['description']}")
        print()
        
        # Blitz package info
        print(f"Blitz Package: {scenario['blitz_data']['name']}")
        print(f"Blitzer: {scenario['blitz_data']['blitzer'].replace('_', ' ').title()}")
        print(f"Total Rushers: {scenario['blitz_data']['rushers']}")
        print(f"Coverage Adjustment: {scenario['blitz_data']['coverage_adjustment'].replace('_', ' ').title()}")
        print()
        
        # Strengths and weaknesses
        print("Run Strengths:", ", ".join(scenario['blitz_data']['run_strengths']))
        print("Run Weaknesses:", ", ".join(scenario['blitz_data']['run_weaknesses']))
        print("Pass Strengths:", ", ".join(scenario['blitz_data']['pass_strengths']))
        print("Pass Weaknesses:", ", ".join(scenario['blitz_data']['pass_weaknesses']))
        print()
        
        print("Best Against:", ", ".join(scenario['blitz_data']['best_against']))
        print("=" * 60)
    
    def display_formation_summary(self, formation_name):
        """Display summary information about a specific formation"""
        if formation_name not in self.formations:
            print(f"Formation {formation_name} not loaded.")
            return
        
        formation = self.formations[formation_name]
        print(f"\n{formation['formation_name']} Summary:")
        print(f"Personnel: {formation['personnel']}")
        print(f"Coverages Available: {len(formation['coverages'])}")
        
        total_scenarios = 0
        for coverage_name, coverage_data in formation['coverages'].items():
            blitz_count = len(coverage_data['blitz_packages'])
            total_scenarios += blitz_count
            print(f"  - {coverage_data['name']}: {blitz_count} blitz packages")
        
        print(f"Total Scenarios: {total_scenarios}")

def main():
    """Test the Defense Engine"""
    # Create defense engine
    engine = DefenseEngine()
    
    # Load all formations
    engine.load_all_formations()
    
    # Show summary of loaded formations
    print("\n" + "="*50)
    print("FORMATION SUMMARIES")
    print("="*50)
    for formation_name in engine.formations.keys():
        engine.display_formation_summary(formation_name)
    
    # Generate and display random scenarios
    print("\n" + "="*50)
    print("RANDOM SCENARIOS")
    print("="*50)
    
    for i in range(3):
        print(f"\nScenario {i+1}:")
        scenario = engine.get_random_scenario()
        engine.display_scenario(scenario)
        
        if i < 2:  # Don't ask after the last scenario
            input("\nPress Enter for next scenario...")

if __name__ == "__main__":
    main()