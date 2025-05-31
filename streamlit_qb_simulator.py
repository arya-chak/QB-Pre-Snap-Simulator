"""
QB Pre-Snap Simulator Streamlit App
Author: Arya Chakraborty

This is the Streamlit app for the QB Pre-Snap Simulator project so users can interact through a web interface.
"""

import streamlit as st
import sys
import os

# Add the current directory to the path so we can import our engines
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from defense_engine import DefenseEngine
from offense_engine import OffenseEngine
from comprehensive_play_simulator import ComprehensivePlaySimulator
from strategic_play_selector import StrategicPlaySelector

# Page configuration
st.set_page_config(
    page_title="QB Pre-Snap Simulator",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        margin-bottom: 30px;
    }
    .scenario-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f4e79;
        margin: 10px 0;
    }
    .success {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .failure {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .yards-needed {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'engines_loaded' not in st.session_state:
    st.session_state.engines_loaded = False
if 'current_scenario' not in st.session_state:
    st.session_state.current_scenario = None
if 'minimum_yards' not in st.session_state:
    st.session_state.minimum_yards = None
if 'game_stats' not in st.session_state:
    st.session_state.game_stats = {
        'total_plays': 0,
        'successful_plays': 0,
        'perfect_calls': 0,
        'terrible_calls': 0,
        'total_yards': 0
    }

@st.cache_resource
def load_engines():
    """Load all engines and cache them"""
    defense_engine = DefenseEngine()
    offense_engine = OffenseEngine()
    simulator = ComprehensivePlaySimulator()
    
    # Load all data
    defense_engine.load_all_formations()
    offense_engine.load_all_formations()
    
    return defense_engine, offense_engine, simulator

def display_defensive_scenario(scenario):
    """Display the defensive scenario in a nice format"""
    st.markdown('<div class="scenario-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🛡️ Defensive Formation**")
        st.write(f"**Formation:** {scenario['formation_data']['formation_name']}")
        st.write(f"**Personnel:** {scenario['formation_data']['personnel']}")
        st.write(f"**Coverage:** {scenario['coverage_data']['name']}")
        st.write(f"**Type:** {scenario['coverage_data']['coverage_type'].title()}")
    
    with col2:
        st.markdown("**🔥 Pressure Package**")
        st.write(f"**Blitz:** {scenario['blitz_data']['name']}")
        st.write(f"**Rushers:** {scenario['blitz_data']['rushers']}")
        st.write(f"**Adjustment:** {scenario['blitz_data']['coverage_adjustment'].replace('_', ' ').title()}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_yards_needed(yards):
    """Display yards needed prominently"""
    st.markdown(f"""
    <div class="yards-needed">
        🎯 YOU NEED AT LEAST {yards} YARDS
    </div>
    """, unsafe_allow_html=True)

def display_play_selection(offense_engine, formation_name):
    """Display plays from selected formation"""
    plays = offense_engine.get_formation_plays(formation_name)
    
    if not plays:
        st.error("No plays found for this formation")
        return None
    
    # Separate passing and running plays
    passing_plays = [p for p in plays if p["type"] == "pass"]
    running_plays = [p for p in plays if p["type"] == "run"]
    
    st.markdown("### 📋 Available Plays")
    
    # Create tabs for passing and running
    pass_tab, run_tab = st.tabs(["🎯 Passing Plays", "🏃 Running Plays"])
    
    with pass_tab:
        if passing_plays:
            for i, play in enumerate(passing_plays):
                with st.expander(f"{play['name']} - {play['concept']}", expanded=False):
                    st.write(f"**Protection:** {play.get('protection', 'N/A')}")
                    if play.get('routes'):
                        st.write("**Routes:**")
                        for receiver, route in play['routes'].items():
                            st.write(f"• {receiver.replace('_', ' ').title()}: {route.replace('_', ' ').title()}")
                    
                    if st.button(f"Select {play['name']}", key=f"pass_{i}"):
                        return play
    
    with run_tab:
        if running_plays:
            for i, play in enumerate(running_plays):
                with st.expander(f"{play['name']} - {play['concept']}", expanded=False):
                    st.write(f"**Blocking:** {play.get('blocking_scheme', 'N/A').replace('_', ' ').title()}")
                    st.write(f"**Ball Carrier:** {play.get('ball_carrier', 'N/A').replace('_', ' ').title()}")
                    if play.get('lead_blocker') and play['lead_blocker'] != 'none':
                        st.write(f"**Lead Blocker:** {play['lead_blocker'].replace('_', ' ').title()}")
                    st.write(f"**Target Gap:** {play.get('target_gap', 'N/A').replace('_', ' ').title()}")
                    
                    if st.button(f"Select {play['name']}", key=f"run_{i}"):
                        return play
    
    return None

def display_result(result):
    """Display simulation result with enhanced formatting"""
    # Success/Failure styling
    if result['overall_success']:
        st.markdown(f"""
        <div class="success">
            <h3>✅ SUCCESS! {result['yards_gained']} yards gained</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="failure">
            <h3>❌ FAILURE! {result['yards_gained']} yards gained</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Result details in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Yards Needed", result['minimum_yards_needed'])
        st.metric("Yards Gained", result['yards_gained'])
    
    with col2:
        st.metric("Success Rate", f"{result['success_rate_used']}%")
        st.metric("Yard Range", result['yard_range'].title())
    
    with col3:
        # Appropriateness with emoji
        appropriateness_emoji = {
            'Perfect': '🎯',
            'Good': '✅', 
            'Average': '⚖️',
            'Poor': '⚠️',
            'Terrible': '❌',
            'Overkill': '🚀'
        }
        emoji = appropriateness_emoji.get(result['appropriateness_category'], '❓')
        st.metric("Appropriateness", f"{emoji} {result['appropriateness_category']}")
        st.metric("Outcome", result['outcome_type'].replace('_', ' ').title())
    
    # Play description
    st.markdown("### 📝 Play Result")
    st.info(result['description'])
    
    # Analysis
    st.markdown("### 🧠 Analysis")
    appropriateness = result['appropriateness_category']
    
    if appropriateness == 'Perfect':
        st.success("🎯 **PERFECT CALL** - This play was ideally suited for this defensive scenario. The play exploits specific weaknesses in this coverage.")
    elif appropriateness == 'Good':
        st.success("✅ **GOOD CALL** - Solid choice that works well against this defense. The play has favorable matchups in this situation.")
    elif appropriateness == 'Average':
        st.warning("⚖️ **AVERAGE CALL** - Neutral matchup, success depends on execution. This play neither exploits nor struggles against this defense.")
    elif appropriateness == 'Poor':
        st.warning("⚠️ **POOR CALL** - Risky choice against this defensive setup. The defense has advantages that make this play difficult.")
    elif appropriateness == 'Terrible':
        st.error("❌ **TERRIBLE CALL** - This defense is well-equipped to stop this play. Consider a different concept that better attacks this coverage.")
    elif appropriateness == 'Overkill':
        st.info("🚀 **OVERKILL** - This play works but is more complex than needed. You're using a cannon to kill a fly - effective but risky.")

def update_game_stats(result):
    """Update game statistics"""
    st.session_state.game_stats['total_plays'] += 1
    st.session_state.game_stats['total_yards'] += result['yards_gained']
    
    if result['overall_success']:
        st.session_state.game_stats['successful_plays'] += 1
    
    if result['appropriateness_category'] == 'Perfect':
        st.session_state.game_stats['perfect_calls'] += 1
    elif result['appropriateness_category'] == 'Terrible':
        st.session_state.game_stats['terrible_calls'] += 1

def display_game_stats():
    """Display game statistics in sidebar"""
    stats = st.session_state.game_stats
    
    if stats['total_plays'] > 0:
        success_rate = (stats['successful_plays'] / stats['total_plays']) * 100
        avg_yards = stats['total_yards'] / stats['total_plays']
        
        st.sidebar.markdown("### 📊 Game Stats")
        st.sidebar.metric("Total Plays", stats['total_plays'])
        st.sidebar.metric("Success Rate", f"{success_rate:.1f}%")
        st.sidebar.metric("Perfect Calls", stats['perfect_calls'])
        st.sidebar.metric("Terrible Calls", stats['terrible_calls'])
        st.sidebar.metric("Avg Yards/Play", f"{avg_yards:.1f}")
        
        if st.sidebar.button("Reset Stats"):
            st.session_state.game_stats = {
                'total_plays': 0,
                'successful_plays': 0,
                'perfect_calls': 0,
                'terrible_calls': 0,
                'total_yards': 0
            }
            st.rerun()

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">🏈 QB Pre-Snap Simulator</h1>', unsafe_allow_html=True)
    st.markdown("**Test your quarterback decision-making skills by reading defenses and calling the right plays!**")
    
    # Load engines
    try:
        if not st.session_state.engines_loaded:
            with st.spinner("Loading defensive and offensive formations..."):
                defense_engine, offense_engine, simulator = load_engines()
                st.session_state.defense_engine = defense_engine
                st.session_state.offense_engine = offense_engine
                st.session_state.simulator = simulator
                st.session_state.engines_loaded = True
                st.success("✅ All formations loaded successfully!")
        
        defense_engine = st.session_state.defense_engine
        offense_engine = st.session_state.offense_engine
        simulator = st.session_state.simulator
        
    except Exception as e:
        st.error(f"❌ Error loading formations: {e}")
        st.error("Make sure all JSON files are in the correct directories (data/defenses/ and data/offenses/)")
        return
    
    # Sidebar controls
    st.sidebar.markdown("### 🎮 Game Controls")
    
    # Generate new scenario button
    if st.sidebar.button("🎲 Generate New Scenario", type="primary"):
        st.session_state.current_scenario = defense_engine.get_random_scenario()
        st.session_state.minimum_yards = simulator.generate_minimum_yards()
        st.rerun()
    
    # Display game stats
    display_game_stats()
    
    # Main game area
    if st.session_state.current_scenario is None:
        st.info("👆 Click 'Generate New Scenario' in the sidebar to start playing!")
        return
    
    scenario = st.session_state.current_scenario
    minimum_yards = st.session_state.minimum_yards
    
    # Display defensive scenario
    st.markdown("## 🛡️ Defensive Scenario")
    display_defensive_scenario(scenario)
    
    # Display yards needed
    display_yards_needed(minimum_yards)
    
    # Formation selection
    st.markdown("## ⚡ Select Your Formation")
    formations = offense_engine.get_available_formations()
    
    formation_names = [f"{'⚡' if 'shotgun' in f['name'] else '🏃' if 'goal' in f['name'] else '⚔️'} {f['display_name']} ({f['personnel']})" 
                      for f in formations]
    
    selected_formation_idx = st.selectbox(
        "Choose your offensive formation:",
        range(len(formations)),
        format_func=lambda i: formation_names[i],
        key="formation_select"
    )
    
    if selected_formation_idx is not None:
        selected_formation = formations[selected_formation_idx]
        formation_name = selected_formation['name']
        
        st.markdown(f"### {selected_formation['display_name']}")
        st.write(f"*{selected_formation['description']}*")
        
        # Play selection
        selected_play = display_play_selection(offense_engine, formation_name)
        
        if selected_play:
            # Get full play details for comprehensive analysis
            full_play_details = offense_engine.get_play_full_details(
                selected_play['formation'], 
                selected_play['key']
            )
            
            if full_play_details:
                comprehensive_play_data = {**selected_play, **full_play_details}
            else:
                comprehensive_play_data = selected_play
            
            # Run simulation
            with st.spinner("Simulating play..."):
                result = simulator.simulate_play(scenario, comprehensive_play_data, minimum_yards)
            
            # Display results
            st.markdown("## 📊 Play Result")
            display_result(result)
            
            # Update stats
            update_game_stats(result)
            
            # Option to play again
            if st.button("🔄 Play Another Scenario", type="secondary"):
                st.session_state.current_scenario = defense_engine.get_random_scenario()
                st.session_state.minimum_yards = simulator.generate_minimum_yards()
                st.rerun()

if __name__ == "__main__":
    main()