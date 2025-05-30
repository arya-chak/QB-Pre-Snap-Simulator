"""
Appropriateness Analyzer
Author: Arya Chakraborty

Analyzes JSON data for common terms between offense and defense.
"""

import json
import os
from collections import defaultdict, Counter

class AppropriatenessAnalyzer:
    def __init__(self):
        """Initialize the analyzer to examine our JSON data"""
        self.offense_data_path = "data/offenses/"
        self.defense_data_path = "data/defenses/"
        
        self.offensive_formations = {}
        self.defensive_formations = {}
        
        # Track all terms used
        self.offensive_terms = {
            "best_against": [],
            "worst_against": [],
            "strengths": [],
            "weaknesses": []
        }
        
        self.defensive_terms = {
            "formation_names": [],
            "coverage_names": [],
            "coverage_types": [],
            "blitz_names": [],
            "strengths": [],
            "weaknesses": [],
            "optimal_situations": [],
            "vulnerable_to": []
        }
    
    def load_all_data(self):
        """Load all offensive and defensive formation data"""
        print("Loading offensive formations...")
        offense_files = ["i-form.json", "singleback.json", "shotgun.json", "trips.json", 
                        "bunch.json", "empty.json", "goal line.json"]
        
        for filename in offense_files:
            filepath = os.path.join(self.offense_data_path, filename)
            try:
                with open(filepath, 'r') as file:
                    formation_name = filename.replace('.json', '')
                    self.offensive_formations[formation_name] = json.load(file)
                    print(f"✓ Loaded {formation_name}")
            except FileNotFoundError:
                print(f"✗ Could not find {filename}")
        
        print("\nLoading defensive formations...")
        defense_files = ["4-3.json", "3-4.json", "5-2.json", "4-4.json", 
                        "46.json", "nickel.json", "dime.json"]
        
        for filename in defense_files:
            filepath = os.path.join(self.defense_data_path, filename)
            try:
                with open(filepath, 'r') as file:
                    formation_name = filename.replace('.json', '')
                    self.defensive_formations[formation_name] = json.load(file)
                    print(f"✓ Loaded {formation_name}")
            except FileNotFoundError:
                print(f"✗ Could not find {filename}")
    
    def extract_offensive_terms(self):
        """Extract all terms from offensive play data"""
        print("\nExtracting offensive terms...")
        
        for formation_name, formation_data in self.offensive_formations.items():
            # Extract from passing plays
            for play_name, play_data in formation_data.get("passing_plays", {}).items():
                self.offensive_terms["best_against"].extend(play_data.get("best_against", []))
                self.offensive_terms["worst_against"].extend(play_data.get("worst_against", []))
                self.offensive_terms["strengths"].extend(play_data.get("strengths", []))
                self.offensive_terms["weaknesses"].extend(play_data.get("weaknesses", []))
            
            # Extract from running plays
            for play_name, play_data in formation_data.get("running_plays", {}).items():
                self.offensive_terms["best_against"].extend(play_data.get("best_against", []))
                self.offensive_terms["worst_against"].extend(play_data.get("worst_against", []))
                self.offensive_terms["strengths"].extend(play_data.get("strengths", []))
                self.offensive_terms["weaknesses"].extend(play_data.get("weaknesses", []))
    
    def extract_defensive_terms(self):
        """Extract all terms from defensive formation data"""
        print("Extracting defensive terms...")
        
        for formation_name, formation_data in self.defensive_formations.items():
            self.defensive_terms["formation_names"].append(formation_data.get("formation_name", ""))
            
            for coverage_name, coverage_data in formation_data.get("coverages", {}).items():
                self.defensive_terms["coverage_names"].append(coverage_data.get("name", ""))
                self.defensive_terms["coverage_types"].append(coverage_data.get("coverage_type", ""))
                
                # Extract from blitz packages
                for blitz_name, blitz_data in coverage_data.get("blitz_packages", {}).items():
                    self.defensive_terms["blitz_names"].append(blitz_data.get("name", ""))
                
                # Extract strengths/weaknesses
                self.defensive_terms["strengths"].extend(coverage_data.get("base_strengths", []))
                self.defensive_terms["weaknesses"].extend(coverage_data.get("base_weaknesses", []))
                self.defensive_terms["optimal_situations"].extend(coverage_data.get("optimal_situations", []))
                self.defensive_terms["vulnerable_to"].extend(coverage_data.get("vulnerable_to", []))
    
    def find_common_keywords(self):
        """Find common keywords between offensive and defensive terms"""
        print("\nAnalyzing common keywords...")
        
        # Combine all offensive terms
        all_offensive = []
        for term_list in self.offensive_terms.values():
            all_offensive.extend(term_list)
        
        # Combine all defensive terms  
        all_defensive = []
        for term_list in self.defensive_terms.values():
            all_defensive.extend(term_list)
        
        # Extract individual words from terms
        offensive_words = set()
        for term in all_offensive:
            words = term.replace('_', ' ').replace('-', ' ').split()
            offensive_words.update(word.lower() for word in words)
        
        defensive_words = set()
        for term in all_defensive:
            words = term.replace('_', ' ').replace('-', ' ').split()
            defensive_words.update(word.lower() for word in words)
        
        # Find common words
        common_words = offensive_words.intersection(defensive_words)
        
        return common_words
    
    def create_keyword_mapping(self):
        """Create a comprehensive keyword mapping system"""
        common_words = self.find_common_keywords()
        
        # Key categories for matching
        keyword_mapping = {
            # Formation types
            "formations": {
                "4-3": ["4-3", "four_three", "base_defense"],
                "3-4": ["3-4", "three_four"],
                "5-2": ["5-2", "five_two"],
                "4-4": ["4-4", "four_four"],
                "46": ["46", "forty_six"],
                "nickel": ["nickel", "five_db", "5_db"],
                "dime": ["dime", "six_db", "6_db"]
            },
            
            # Coverage types
            "coverages": {
                "cover_0": ["cover_0", "cover_zero", "man_no_help", "all_out", "blitz"],
                "cover_1": ["cover_1", "cover_one", "man_coverage", "single_high"],
                "cover_2": ["cover_2", "cover_two", "zone", "deep_split", "safety_help"],
                "cover_3": ["cover_3", "cover_three", "single_safety", "deep_thirds"],
                "cover_4": ["cover_4", "cover_four", "quarters", "deep_help"],
                "man": ["man_coverage", "individual", "tight_coverage"],
                "zone": ["zone_coverage", "area", "soft_coverage"]
            },
            
            # Pressure/Blitz concepts
            "pressure": {
                "blitz": ["blitz", "pressure", "rush", "aggressive"],
                "no_blitz": ["base", "standard", "four_man", "three_man"],
                "heavy_rush": ["all_out", "overload", "max_rush"],
                "spy": ["spy", "contain", "qb_focused"]
            },
            
            # Situational concepts
            "situations": {
                "short_yardage": ["short_yardage", "goal_line", "inches"],
                "long_yardage": ["long_yardage", "obvious_passing", "third_long"],
                "red_zone": ["red_zone", "goal_line", "compressed"],
                "open_field": ["open_field", "spread", "space"]
            },
            
            # Personnel concepts
            "personnel": {
                "heavy_box": ["heavy_box", "eight_in_box", "stacked", "run_support"],
                "light_box": ["light_box", "spread_out", "pass_coverage"],
                "extra_db": ["extra_db", "nickel", "dime", "pass_defense"]
            }
        }
        
        return keyword_mapping
    
    def analyze_matchups(self):
        """Analyze potential matchups between offense and defense - CHECK ALL PLAYS"""
        print("\nAnalyzing ALL offensive plays for matchup data...")
        
        matchup_examples = []
        missing_data_plays = []
        total_plays = 0
        plays_with_data = 0
        
        # Check EVERY formation and EVERY play
        for formation_name, formation_data in self.offensive_formations.items():
            print(f"\n{'='*60}")
            print(f"FORMATION: {formation_name.upper()}")
            print(f"{'='*60}")
            
            # Analyze ALL passing plays
            passing_plays = formation_data.get("passing_plays", {})
            if passing_plays:
                print(f"\nPASSING PLAYS ({len(passing_plays)} total):")
                print("-" * 40)
                
                for play_name, play_data in passing_plays.items():
                    total_plays += 1
                    play_display_name = play_data.get('name', play_name)
                    
                    best_against = play_data.get('best_against', [])
                    worst_against = play_data.get('worst_against', [])
                    
                    if best_against or worst_against:
                        plays_with_data += 1
                        print(f"\n✓ {play_display_name}")
                        if best_against:
                            print(f"   Best against: {best_against}")
                        if worst_against:
                            print(f"   Worst against: {worst_against}")
                        
                        matchup_examples.append({
                            "formation": formation_name,
                            "play": play_display_name,
                            "type": "pass",
                            "best_against": best_against,
                            "worst_against": worst_against
                        })
                    else:
                        print(f"\n✗ {play_display_name} - MISSING MATCHUP DATA")
                        missing_data_plays.append({
                            "formation": formation_name,
                            "play": play_display_name,
                            "type": "pass"
                        })
            
            # Analyze ALL running plays
            running_plays = formation_data.get("running_plays", {})
            if running_plays:
                print(f"\nRUNNING PLAYS ({len(running_plays)} total):")
                print("-" * 40)
                
                for play_name, play_data in running_plays.items():
                    total_plays += 1
                    play_display_name = play_data.get('name', play_name)
                    
                    best_against = play_data.get('best_against', [])
                    worst_against = play_data.get('worst_against', [])
                    
                    if best_against or worst_against:
                        plays_with_data += 1
                        print(f"\n✓ {play_display_name}")
                        if best_against:
                            print(f"   Best against: {best_against}")
                        if worst_against:
                            print(f"   Worst against: {worst_against}")
                        
                        matchup_examples.append({
                            "formation": formation_name,
                            "play": play_display_name,
                            "type": "run",
                            "best_against": best_against,
                            "worst_against": worst_against
                        })
                    else:
                        print(f"\n✗ {play_display_name} - MISSING MATCHUP DATA")
                        missing_data_plays.append({
                            "formation": formation_name,
                            "play": play_display_name,
                            "type": "run"
                        })
        
        # Summary statistics
        print(f"\n{'='*80}")
        print("COMPREHENSIVE MATCHUP ANALYSIS SUMMARY")
        print(f"{'='*80}")
        print(f"Total plays analyzed: {total_plays}")
        print(f"Plays with matchup data: {plays_with_data}")
        print(f"Plays missing data: {len(missing_data_plays)}")
        print(f"Coverage percentage: {(plays_with_data/total_plays)*100:.1f}%")
        
        if missing_data_plays:
            print(f"\nPLAYS MISSING MATCHUP DATA:")
            print("-" * 40)
            for play in missing_data_plays:
                print(f"• {play['formation']} - {play['play']} ({play['type']})")
        
        return {
            "matchup_examples": matchup_examples,
            "missing_data_plays": missing_data_plays,
            "total_plays": total_plays,
            "plays_with_data": plays_with_data,
            "coverage_percentage": (plays_with_data/total_plays)*100
        }
    
    def display_analysis_results(self):
        """Display comprehensive analysis results"""
        print("\n" + "="*80)
        print("COMPREHENSIVE JSON ANALYSIS RESULTS")
        print("="*80)
        
        # Show data loading summary
        print(f"\nDATA LOADED:")
        print(f"Offensive formations: {len(self.offensive_formations)}")
        print(f"Defensive formations: {len(self.defensive_formations)}")
        
        # Show common keywords
        common_words = self.find_common_keywords()
        print(f"\nCOMMON KEYWORDS FOUND: {len(common_words)}")
        print("Sample common words:", sorted(list(common_words))[:20])
        
        # Show keyword mapping
        keyword_mapping = self.create_keyword_mapping()
        print(f"\nKEYWORD MAPPING CATEGORIES:")
        for category, mappings in keyword_mapping.items():
            print(f"  {category}: {len(mappings)} subcategories")
        
        # Show ALL matchup analysis
        matchup_analysis = self.analyze_matchups()
        print(f"\nCOMPLETE MATCHUP ANALYSIS:")
        print(f"Total plays: {matchup_analysis['total_plays']}")
        print(f"Plays with data: {matchup_analysis['plays_with_data']}")
        print(f"Coverage: {matchup_analysis['coverage_percentage']:.1f}%")
        
        return {
            "common_words": common_words,
            "keyword_mapping": keyword_mapping,
            "matchup_analysis": matchup_analysis,
            "offensive_terms": self.offensive_terms,
            "defensive_terms": self.defensive_terms
        }
    
    def generate_appropriateness_logic(self):
        """Generate the logic for the play appropriateness system"""
        keyword_mapping = self.create_keyword_mapping()
        
        logic_template = '''
def get_play_appropriateness_comprehensive(self, offensive_play, defensive_scenario, yard_range):
    """
    Comprehensive play appropriateness system using keyword matching
    """
    
    # Extract play characteristics
    play_best_against = offensive_play.get("best_against", [])
    play_worst_against = offensive_play.get("worst_against", [])
    
    # Extract defensive characteristics
    formation_name = defensive_scenario.get("formation_name", "").lower()
    coverage_name = defensive_scenario.get("coverage_name", "").lower()
    coverage_type = defensive_scenario.get("coverage_data", {}).get("coverage_type", "").lower()
    blitz_name = defensive_scenario.get("blitz_name", "").lower()
    
    # Scoring system: start neutral
    appropriateness_score = 50  # 0-100 scale
    
    # Check matches with keyword mapping
    keyword_mapping = ''' + str(keyword_mapping) + '''
    
    # [Logic for matching keywords and adjusting score would go here]
    
    # Adjust for yard range
    yard_range_adjustments = {
        "short": {
            "power_concepts": +20,
            "deep_concepts": -15,
            "quick_concepts": +10
        },
        "medium": {
            "balanced_concepts": +10,
            "intermediate_concepts": +15
        },
        "long": {
            "deep_concepts": +20,
            "power_concepts": -20,
            "quick_concepts": -10
        }
    }
    
    # Convert score to category
    if appropriateness_score >= 85:
        return "Perfect"
    elif appropriateness_score >= 70:
        return "Good" 
    elif appropriateness_score >= 40:
        return "Average"
    elif appropriateness_score >= 20:
        return "Poor"
    else:
        return "Terrible"
        '''
        
        return logic_template

def main():
    """Run the analysis"""
    analyzer = AppropriatenessAnalyzer()
    
    # Load all data
    analyzer.load_all_data()
    
    if not analyzer.offensive_formations or not analyzer.defensive_formations:
        print("Error: Could not load formation data. Check file paths.")
        return
    
    # Extract terms
    analyzer.extract_offensive_terms()
    analyzer.extract_defensive_terms()
    
    # Display comprehensive analysis
    results = analyzer.display_analysis_results()
    
    # Generate logic template
    logic_code = analyzer.generate_appropriateness_logic()
    
    print("\n" + "="*80)
    print("GENERATED LOGIC TEMPLATE")
    print("="*80)
    print("Here's a template for the comprehensive appropriateness system:")
    print(logic_code[:500] + "...")
    print("\n[Full logic template generated - ready for implementation]")

if __name__ == "__main__":
    main()