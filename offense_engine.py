"""
Offense Engine
Author: Arya Chakraborty

Loads offensive formations from JSON files, lets user pick a formation, and then a specific play from that formation.
"""

import json
import os

class OffenseEngine:
    def __init__(self):
        """Initialize the Offense Engine"""
        self.formations = {}
        self.data_path = "data/offenses/"
        self.available_formations = ["i-form", "singleback", "shotgun", "trips", "bunch", "empty", "goal line"]
    
    def load_formation(self, formation_name):
        """Load a specific offensive formation from JSON file"""
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
        """Load all available offensive formations"""
        print("Loading offensive formations...")
        for formation in self.available_formations:
            result = self.load_formation(formation)
            if result:
                print(f"✓ Loaded {formation} formation")
            else:
                print(f"✗ Failed to load {formation} formation")
        print(f"\nTotal formations loaded: {len(self.formations)}")
    
    def get_available_formations(self):
        """Get list of available formations with descriptions"""
        if not self.formations:
            print("No formations loaded! Please load formations first.")
            return []
        
        formation_list = []
        for formation_name, formation_data in self.formations.items():
            formation_info = {
                "name": formation_name,
                "display_name": formation_data["formation_name"],
                "personnel": formation_data["personnel"],
                "description": formation_data["description"]
            }
            formation_list.append(formation_info)
        
        return formation_list
    
    def display_formations(self):
        """Display all available formations for user selection"""
        formations = self.get_available_formations()
        if not formations:
            return
        
        print("\n" + "="*60)
        print("AVAILABLE FORMATIONS")
        print("="*60)
        
        for i, formation in enumerate(formations, 1):
            print(f"{i}. {formation['display_name']}")
            print(f"   Personnel: {formation['personnel']}")
            print(f"   {formation['description']}")
            print()
    
    def get_formation_plays(self, formation_name):
        """Get all plays from a specific formation"""
        if formation_name not in self.formations:
            print(f"Formation {formation_name} not loaded.")
            return None
        
        formation = self.formations[formation_name]
        all_plays = []
        
        # Get passing plays
        if "passing_plays" in formation:
            for play_key, play_data in formation["passing_plays"].items():
                play_info = {
                    "key": play_key,
                    "type": "pass",
                    "name": play_data["name"],
                    "concept": play_data["concept"],
                    "routes": play_data.get("routes", {}),
                    "protection": play_data.get("protection", ""),
                    "formation": formation_name
                }
                all_plays.append(play_info)
        
        # Get running plays
        if "running_plays" in formation:
            for play_key, play_data in formation["running_plays"].items():
                play_info = {
                    "key": play_key,
                    "type": "run",
                    "name": play_data["name"],
                    "concept": play_data["concept"],
                    "blocking_scheme": play_data.get("blocking_scheme", ""),
                    "ball_carrier": play_data.get("ball_carrier", ""),
                    "lead_blocker": play_data.get("lead_blocker", ""),
                    "target_gap": play_data.get("target_gap", ""),
                    "formation": formation_name
                }
                all_plays.append(play_info)
        
        return all_plays
    
    def display_formation_plays(self, formation_name):
        """Display all plays from a formation with pre-snap info only"""
        plays = self.get_formation_plays(formation_name)
        if not plays:
            return
        
        formation_display = self.formations[formation_name]["formation_name"]
        print(f"\n" + "="*60)
        print(f"PLAYS FROM {formation_display.upper()}")
        print("="*60)
        
        # Separate passing and running plays
        passing_plays = [p for p in plays if p["type"] == "pass"]
        running_plays = [p for p in plays if p["type"] == "run"]
        
        # Display passing plays
        if passing_plays:
            print("\nPASSING PLAYS:")
            print("-" * 40)
            for i, play in enumerate(passing_plays, 1):
                print(f"{i}. {play['name']}")
                print(f"   Concept: {play['concept']}")
                print(f"   Protection: {play['protection']}")
                if play['routes']:
                    print("   Routes:")
                    for receiver, route in play['routes'].items():
                        print(f"     • {receiver.replace('_', ' ').title()}: {route.replace('_', ' ').title()}")
                print()
        
        # Display running plays
        if running_plays:
            print("\nRUNNING PLAYS:")
            print("-" * 40)
            for i, play in enumerate(running_plays, len(passing_plays) + 1):
                print(f"{i}. {play['name']}")
                print(f"   Concept: {play['concept']}")
                print(f"   Blocking Scheme: {play['blocking_scheme'].replace('_', ' ').title()}")
                print(f"   Ball Carrier: {play['ball_carrier'].replace('_', ' ').title()}")
                if play['lead_blocker'] and play['lead_blocker'] != "none":
                    print(f"   Lead Blocker: {play['lead_blocker'].replace('_', ' ').title()}")
                print(f"   Target Gap: {play['target_gap'].replace('_', ' ').title()}")
                print()
    
    def get_play_by_number(self, formation_name, play_number):
        """Get a specific play by its display number"""
        plays = self.get_formation_plays(formation_name)
        if not plays or play_number < 1 or play_number > len(plays):
            return None
        
        return plays[play_number - 1]
    
    def get_play_full_details(self, formation_name, play_key):
        """Get complete play details for simulation (not shown to user)"""
        if formation_name not in self.formations:
            return None
        
        formation = self.formations[formation_name]
        
        # Check passing plays
        if "passing_plays" in formation and play_key in formation["passing_plays"]:
            return formation["passing_plays"][play_key]
        
        # Check running plays
        if "running_plays" in formation and play_key in formation["running_plays"]:
            return formation["running_plays"][play_key]
        
        return None
    
    def display_formation_summary(self, formation_name):
        """Display summary information about a specific formation"""
        if formation_name not in self.formations:
            print(f"Formation {formation_name} not loaded.")
            return
        
        formation = self.formations[formation_name]
        plays = self.get_formation_plays(formation_name)
        
        passing_count = len([p for p in plays if p["type"] == "pass"])
        running_count = len([p for p in plays if p["type"] == "run"])
        
        print(f"\n{formation['formation_name']} Summary:")
        print(f"Personnel: {formation['personnel']}")
        print(f"Personnel Package: {formation.get('personnel_package', 'N/A')}")
        print(f"Total Plays: {len(plays)} ({passing_count} passing, {running_count} running)")

def main():
    """Test the Offense Engine"""
    # Create offense engine
    engine = OffenseEngine()
    
    # Load all formations
    engine.load_all_formations()
    
    # Show formation summaries
    print("\n" + "="*50)
    print("FORMATION SUMMARIES")
    print("="*50)
    for formation_name in engine.formations.keys():
        engine.display_formation_summary(formation_name)
    
    # Interactive formation and play selection
    print("\n" + "="*50)
    print("INTERACTIVE PLAY SELECTION")
    print("="*50)
    
    while True:
        # Display formations
        engine.display_formations()
        
        try:
            formations = engine.get_available_formations()
            choice = input(f"Select formation (1-{len(formations)}) or 'q' to quit: ")
            
            if choice.lower() == 'q':
                break
            
            formation_index = int(choice) - 1
            if 0 <= formation_index < len(formations):
                selected_formation = formations[formation_index]["name"]
                
                # Display plays from selected formation
                engine.display_formation_plays(selected_formation)
                
                # Let user select a play
                plays = engine.get_formation_plays(selected_formation)
                play_choice = input(f"Select play (1-{len(plays)}) or 'b' to go back: ")
                
                if play_choice.lower() == 'b':
                    continue
                
                play_number = int(play_choice)
                selected_play = engine.get_play_by_number(selected_formation, play_number)
                
                if selected_play:
                    print(f"\n{'='*40}")
                    print("SELECTED PLAY")
                    print("="*40)
                    print(f"Formation: {selected_play['formation'].replace('-', ' ').title()}")
                    print(f"Play: {selected_play['name']}")
                    print(f"Type: {selected_play['type'].title()}")
                    print(f"Concept: {selected_play['concept']}")
                    print("\n[This play would now go to the simulator]")
                    input("\nPress Enter to continue...")
                else:
                    print("Invalid play selection.")
            else:
                print("Invalid formation selection.")
                
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()