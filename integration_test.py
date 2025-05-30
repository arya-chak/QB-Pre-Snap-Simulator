"""
Integrtion Test
Author: Arya Chakraborty

Tests that the defense engine, offense engine, and play simulator work together correctly.
"""

import sys
import os

# Add the current directory to the path so we can import our engines
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from defense_engine import DefenseEngine
from offense_engine import OffenseEngine
from comprehensive_play_simulator import ComprehensivePlaySimulator

class IntegrationTest:
    def __init__(self):
        """Initialize all three engines"""
        print("Initializing QB Decision Game...")
        print("="*50)
        
        self.defense_engine = DefenseEngine()
        self.offense_engine = OffenseEngine()
        self.simulator = ComprehensivePlaySimulator()
        
        # Load all data
        self.load_all_data()
    
    def load_all_data(self):
        """Load all defensive and offensive formations"""
        print("\n1. Loading Defensive Formations...")
        self.defense_engine.load_all_formations()
        
        print("\n2. Loading Offensive Formations...")
        self.offense_engine.load_all_formations()
        
        print("\n3. Initializing Comprehensive Play Simulator...")
        print("✓ Comprehensive Play Simulator ready with keyword matching")
        
        print(f"\nData Summary:")
        print(f"- Defensive formations: {len(self.defense_engine.formations)}")
        print(f"- Offensive formations: {len(self.offense_engine.formations)}")
        
        # Calculate total scenarios
        total_def_scenarios = 0
        for formation in self.defense_engine.formations.values():
            for coverage in formation["coverages"].values():
                total_def_scenarios += len(coverage["blitz_packages"])
        
        total_off_plays = 0
        for formation in self.offense_engine.formations.values():
            total_off_plays += len(formation.get("passing_plays", {}))
            total_off_plays += len(formation.get("running_plays", {}))
        
        print(f"- Total defensive scenarios: {total_def_scenarios}")
        print(f"- Total offensive plays: {total_off_plays}")
        print(f"- Total possible matchups: {total_def_scenarios * total_off_plays:,}")
    
    def run_single_test(self):
        """Run a single complete test scenario"""
        print("\n" + "="*60)
        print("SINGLE INTEGRATION TEST")
        print("="*60)
        
        # Step 1: Generate random defensive scenario
        print("\n1. GENERATING DEFENSIVE SCENARIO...")
        defensive_scenario = self.defense_engine.get_random_scenario()
        
        if not defensive_scenario:
            print("Error: Could not generate defensive scenario")
            return
        
        self.display_defensive_scenario(defensive_scenario)
        
        # Step 2: Generate minimum yards needed (PRE-SNAP INFO)
        minimum_yards = self.simulator.generate_minimum_yards()
        print(f"\n2. SITUATION: YOU NEED AT LEAST {minimum_yards} YARDS")
        print("="*50)
        
        # Step 3: Let user select offensive formation and play
        print("\n3. SELECTING OFFENSIVE PLAY...")
        selected_play = self.get_user_offensive_choice()
        
        if not selected_play:
            print("No play selected.")
            return
        
        self.display_selected_play(selected_play)
        
        # Step 4: Run simulation with predetermined minimum yards
        print("\n4. SIMULATING PLAY WITH COMPREHENSIVE MATCHING...")
        
        # Get full play details for comprehensive analysis
        full_play_details = self.offense_engine.get_play_full_details(
            selected_play['formation'], 
            selected_play['key']
        )
        
        if full_play_details:
            # Merge basic play info with full details for comprehensive analysis
            comprehensive_play_data = {
                **selected_play,  # Basic info (name, type, concept, etc.)
                **full_play_details  # Full details (best_against, worst_against, etc.)
            }
            result = self.simulator.simulate_play(defensive_scenario, comprehensive_play_data, minimum_yards)
        else:
            # Fallback to basic play data
            result = self.simulator.simulate_play(defensive_scenario, selected_play, minimum_yards)
        
        self.display_simulation_result(result, defensive_scenario, selected_play)
    
    def display_defensive_scenario(self, scenario):
        """Display the defensive scenario clearly"""
        print(f"\nDefensive Scenario:")
        print(f"Formation: {scenario['formation_data']['formation_name']}")
        print(f"Personnel: {scenario['formation_data']['personnel']}")
        print(f"Coverage: {scenario['coverage_data']['name']}")
        print(f"Coverage Type: {scenario['coverage_data']['coverage_type'].title()}")
        print(f"Blitz Package: {scenario['blitz_data']['name']}")
        print(f"Rushers: {scenario['blitz_data']['rushers']}")
        print(f"Coverage Adjustment: {scenario['blitz_data']['coverage_adjustment'].replace('_', ' ').title()}")
    
    def get_user_offensive_choice(self):
        """Let user select offensive formation and play with detailed display"""
        # Display available formations
        formations = self.offense_engine.get_available_formations()
        if not formations:
            return None
        
        print("\nAvailable Formations:")
        for i, formation in enumerate(formations, 1):
            print(f"{i}. {formation['display_name']} ({formation['personnel']})")
        
        try:
            # Get formation choice
            choice = input(f"\nSelect formation (1-{len(formations)}): ")
            formation_index = int(choice) - 1
            
            if not (0 <= formation_index < len(formations)):
                print("Invalid formation selection.")
                return None
            
            selected_formation = formations[formation_index]["name"]
            
            # Use the detailed display from offense engine
            print(f"\n" + "="*60)
            self.offense_engine.display_formation_plays(selected_formation)
            
            # Get plays for selection
            plays = self.offense_engine.get_formation_plays(selected_formation)
            if not plays:
                return None
            
            # Get play choice
            play_choice = input(f"\nSelect play (1-{len(plays)}): ")
            play_index = int(play_choice) - 1
            
            if not (0 <= play_index < len(plays)):
                print("Invalid play selection.")
                return None
            
            return plays[play_index]
            
        except ValueError:
            print("Please enter a valid number.")
            return None
        except KeyboardInterrupt:
            print("\nTest cancelled.")
            return None
    
    def display_selected_play(self, play):
        """Display the selected offensive play"""
        print(f"\nSelected Play:")
        print(f"Formation: {play['formation'].replace('-', ' ').title()}")
        print(f"Play: {play['name']}")
        print(f"Type: {play['type'].title()}")
        print(f"Concept: {play['concept']}")
        
        if play['type'] == 'pass':
            print(f"Protection: {play.get('protection', 'N/A')}")
            if play.get('routes'):
                print("Routes:")
                for receiver, route in play['routes'].items():
                    print(f"  • {receiver.replace('_', ' ').title()}: {route.replace('_', ' ').title()}")
        else:  # run play
            print(f"Blocking: {play.get('blocking_scheme', 'N/A').replace('_', ' ').title()}")
            print(f"Ball Carrier: {play.get('ball_carrier', 'N/A').replace('_', ' ').title()}")
            if play.get('lead_blocker') and play['lead_blocker'] != 'none':
                print(f"Lead Blocker: {play['lead_blocker'].replace('_', ' ').title()}")
            print(f"Target Gap: {play.get('target_gap', 'N/A').replace('_', ' ').title()}")
    
    def display_simulation_result(self, result, defensive_scenario, offensive_play):
        """Display the simulation result with context"""
        print("\n" + "="*50)
        print("COMPREHENSIVE SIMULATION RESULT")
        print("="*50)
        
        print(f"Minimum Yards Needed: {result['minimum_yards_needed']}")
        print(f"Yards Gained: {result['yards_gained']}")
        print(f"Overall Success: {'✓ SUCCESS' if result['overall_success'] else '✗ FAILURE'}")
        print(f"Appropriateness: {result['appropriateness_category']}")
        print(f"Success Rate Used: {result['success_rate_used']}%")
        print(f"Yard Range: {result['yard_range'].title()}")
        print(f"Outcome Type: {result['outcome_type'].replace('_', ' ').title()}")
        print(f"vs: {result.get('defensive_scenario_summary', 'Defense')}")
        print()
        print("Play Description:")
        print(f"  {result['description']}")
        print()
        
        # Enhanced Analysis with comprehensive feedback
        print("Comprehensive Analysis:")
        if result['appropriateness_category'] == 'Perfect':
            print("  • 🎯 PERFECT CALL - This play was ideally suited for this defensive scenario")
            print("  • The play exploits specific weaknesses in this coverage")
        elif result['appropriateness_category'] == 'Good':
            print("  • ✅ GOOD CALL - Solid choice that works well against this defense")
            print("  • The play has favorable matchups in this situation")
        elif result['appropriateness_category'] == 'Average':
            print("  • ⚖️ AVERAGE CALL - Neutral matchup, success depends on execution")
            print("  • This play neither exploits nor struggles against this defense")
        elif result['appropriateness_category'] == 'Poor':
            print("  • ⚠️ POOR CALL - Risky choice against this defensive setup")
            print("  • The defense has advantages that make this play difficult")
        elif result['appropriateness_category'] == 'Terrible':
            print("  • ❌ TERRIBLE CALL - This defense is well-equipped to stop this play")
            print("  • Consider a different concept that better attacks this coverage")
        elif result['appropriateness_category'] == 'Overkill':
            print("  • 🚀 OVERKILL - This play works but is more complex than needed")
            print("  • You're using a cannon to kill a fly - effective but risky")
        
        # Outcome-specific feedback
        if result['outcome_type'] in ['interception', 'fumble']:
            print("  • 💔 TURNOVER - These are always costly, regardless of play call")
        elif result['outcome_type'] == 'sack':
            print("  • 📉 SACK - Play took too long to develop or protection failed")
        elif result['outcome_type'] == 'big_play_success':
            print("  • 💥 BIG PLAY - Excellent execution and/or favorable matchup!")
        
        # Yard range context
        yard_range = result['yard_range']
        if yard_range == 'short':
            print("  • 📏 SHORT YARDAGE - Power concepts and quick routes typically work best")
        elif yard_range == 'medium':
            print("  • 📏 MEDIUM YARDAGE - Balanced approach with multiple options")
        elif yard_range == 'long':
            print("  • 📏 LONG YARDAGE - Deep concepts and big-play routes favored")
    
    def run_multiple_tests(self, num_tests=5):
        """Run multiple automated tests to show variety"""
        print("\n" + "="*60)
        print(f"RUNNING {num_tests} AUTOMATED TESTS")
        print("="*60)
        
        for i in range(num_tests):
            print(f"\n--- Test {i+1} ---")
            
            # Generate random scenario
            scenario = self.defense_engine.get_random_scenario()
            
            # Pick random offensive play with full details
            formation_name = list(self.offense_engine.formations.keys())[
                i % len(self.offense_engine.formations)
            ]
            plays = self.offense_engine.get_formation_plays(formation_name)
            play = plays[i % len(plays)]
            
            # Get full play details for comprehensive analysis
            full_play_details = self.offense_engine.get_play_full_details(
                play['formation'], 
                play['key']
            )
            
            if full_play_details:
                comprehensive_play_data = {**play, **full_play_details}
            else:
                comprehensive_play_data = play
            
            # Run simulation
            result = self.simulator.simulate_play(scenario, comprehensive_play_data)
            
            print(f"Defense: {scenario['formation_data']['formation_name']} {scenario['coverage_data']['name']}")
            print(f"Offense: {play['name']} from {play['formation'].replace('-', ' ').title()}")
            print(f"Result: {result['description']}")
    
    def run_interactive_session(self):
        """Run multiple interactive tests"""
        print("\n" + "="*60)
        print("INTERACTIVE TEST SESSION")
        print("="*60)
        
        while True:
            try:
                print("\nOptions:")
                print("1. Run single test")
                print("2. Run 5 automated tests")
                print("3. Quit")
                
                choice = input("\nSelect option (1-3): ")
                
                if choice == "1":
                    self.run_single_test()
                elif choice == "2":
                    self.run_multiple_tests()
                elif choice == "3":
                    print("Thanks for testing!")
                    break
                else:
                    print("Invalid choice.")
                
                if choice in ["1", "2"]:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

def main():
    """Main function to run integration tests"""
    try:
        # Initialize the integration test
        test = IntegrationTest()
        
        # Check if data loaded successfully
        if not test.defense_engine.formations or not test.offense_engine.formations:
            print("\nError: Could not load formation data.")
            print("Make sure the following directories exist with JSON files:")
            print("- data/defenses/ (with 4-3.json, 3-4.json, etc.)")
            print("- data/offenses/ (with i-formation.json, shotgun.json, etc.)")
            return
        
        print("\n" + "="*50)
        print("INTEGRATION TEST SUCCESSFUL!")
        print("All engines loaded and connected properly.")
        print("="*50)
        
        # Run interactive session
        test.run_interactive_session()
        
    except Exception as e:
        print(f"\nError during integration test: {e}")
        print("Make sure all engine files are in the same directory and data files exist.")

if __name__ == "__main__":
    main()