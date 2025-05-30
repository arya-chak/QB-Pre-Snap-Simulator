"""
QB Pre-Snap Simulator Streamlit App
Author: Arya Chakraborty

This is the Streamlit app for the QB Pre-Snap Simulator project so users can interact through a web interface.
Enhanced with Strategic Play Selection Mode.
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
from library_browser import LibraryBrowser
from field_visualizer import FieldVisualizer

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
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = 'learner'  # 'learner' or 'pro'
if 'strategic_plays' not in st.session_state:
    st.session_state.strategic_plays = None
if 'shuffled_play_order' not in st.session_state:
    st.session_state.shuffled_play_order = None
if 'play_completed' not in st.session_state:
    st.session_state.play_completed = False
if 'current_result' not in st.session_state:
    st.session_state.current_result = None
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
    
    # Create field visualizer
    field_visualizer = FieldVisualizer()  # No parameters needed initially
    
    # Create strategic selector and library browser with field visualizer
    strategic_selector = StrategicPlaySelector(offense_engine, simulator)
    library_browser = LibraryBrowser(defense_engine, offense_engine, field_visualizer)
    
    return defense_engine, offense_engine, simulator, strategic_selector, library_browser, field_visualizer


def display_defensive_scenario(scenario, field_visualizer, minimum_yards=10, visibility_settings=None):
    """Display the defensive scenario with configurable visibility based on pre-snap read settings"""
    if visibility_settings is None:
        visibility_settings = {
            'formation_name': True,
            'personnel': True,
            'coverage_name': False,
            'coverage_type': False,
            'blitz_name': False,
            'rushers': False,
            'coverage_adjustment': False,
            'field_visual': True
        }
    
    st.markdown('<div class="scenario-box">', unsafe_allow_html=True)
    
    # Update the field visualizer with yards to go
    field_visualizer.update_yards_to_go(minimum_yards)
    
    # Create two columns - field visual and details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if visibility_settings['field_visual']:
            st.markdown("**🛡️ Defensive Formation Visual**")
            
            # Get the formation name for visualization
            formation_name = scenario['formation_name']
            
            # Only show coverage name in visual if it's visible
            if visibility_settings['coverage_name']:
                coverage_name = scenario['coverage_data']['name']
            else:
                coverage_name = "Base Coverage"  # Generic name
            
            # Determine if we should show labels (formation/coverage names in the visual)
            show_labels = visibility_settings['formation_name'] or visibility_settings['coverage_name']
            
            # Display the field visualization
            field_display, legend = field_visualizer.display_defensive_formation(
                formation_name, coverage_name, show_labels
            )
            st.markdown(field_display)
        else:
            st.markdown("**🛡️ Defensive Formation**")
            st.info("🚫 Field visual disabled - You must rely on other visible information to read the defense")
    
    with col2:
        st.markdown("**📋 Defensive Information**")
        
        # Formation name - almost always visible in real games
        if visibility_settings['formation_name']:
            st.write(f"**Formation:** {scenario['formation_data']['formation_name']}")
        
        # Personnel - visible by counting players
        if visibility_settings['personnel']:
            st.write(f"**Personnel:** {scenario['formation_data']['personnel']}")
        
        # Coverage name - harder to tell pre-snap
        if visibility_settings['coverage_name']:
            st.write(f"**Coverage:** {scenario['coverage_data']['name']}")
        
        # Coverage type - requires film study/experience
        if visibility_settings['coverage_type']:
            st.write(f"**Type:** {scenario['coverage_data']['coverage_type'].title()}")
        
        if visibility_settings['blitz_name'] or visibility_settings['rushers'] or visibility_settings['coverage_adjustment']:
            st.markdown("**🔥 Pressure Package**")
            
            # Blitz name - very hard to tell pre-snap
            if visibility_settings['blitz_name']:
                st.write(f"**Blitz:** {scenario['blitz_data']['name']}")
            
            # Number of rushers - somewhat visible
            if visibility_settings['rushers']:
                st.write(f"**Rushers:** {scenario['blitz_data']['rushers']}")
            
            # Coverage adjustment - nearly impossible pre-snap
            if visibility_settings['coverage_adjustment']:
                st.write(f"**Adjustment:** {scenario['blitz_data']['coverage_adjustment'].replace('_', ' ').title()}")
        
        # Always show legend if field visual is visible
        if visibility_settings['field_visual']:
            field_display, legend = field_visualizer.display_defensive_formation(scenario['formation_name'], "Base Coverage")
            st.markdown("**Legend:**")
            for category, symbols in legend.items():
                st.write(f"**{category}:** {symbols}")
            
            st.markdown("**Field Markers:**")
            st.write("**─** = Line of Scrimmage")
            st.write("**═** = First Down Marker")
            st.write("**|** = 5-yard markers")
            st.write("**.** = Hash marks")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_yards_needed(yards):
    """Display yards needed prominently"""
    st.markdown(f"""
    <div class="yards-needed">
        🎯 YOU NEED AT LEAST {yards} YARDS
    </div>
    """, unsafe_allow_html=True)

def display_learner_mode_plays(strategic_result, simulator, scenario, minimum_yards):
    """Display the 5 plays without revealing appropriateness - for learning"""
    
    st.markdown("### 🎓 Learner Mode - Choose Your Play")
    st.markdown("*5 plays have been selected for this scenario. Make your decision based on the defense you see:*")
    
    # Display selection info without revealing categories
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Plays Available", "5")
    with col2:
        st.metric("Formation Variety", strategic_result['diversity_info']['formation_diversity'])
    
    # Create a list of plays without revealing their categories
    strategic_plays = strategic_result['strategic_plays']
    
    # Create shuffled order only once and store in session state
    if st.session_state.shuffled_play_order is None:
        play_options = []
        for category, play_eval in strategic_plays.items():
            if play_eval:
                play_options.append(play_eval)
        
        # Shuffle once and store
        import random
        random.shuffle(play_options)
        st.session_state.shuffled_play_order = play_options
    
    # Use the stored shuffled order
    play_options = st.session_state.shuffled_play_order
    
    for i, play_eval in enumerate(play_options, 1):
        if play_eval:
            # Format play for display
            from strategic_play_selector import StrategicPlaySelector
            temp_selector = StrategicPlaySelector(None, None)
            formatted_play = temp_selector.format_play_for_display(play_eval)
            
            # NO appropriateness indicators - just the play info
            with st.expander(f"Option {i}: {formatted_play['name']}", expanded=False):
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Formation:** {formatted_play['formation']}")
                    st.markdown(f"**Type:** {formatted_play['type']} - {formatted_play['concept']}")
                    
                    if formatted_play['type'] == 'Pass':
                        st.markdown(f"**Protection:** {formatted_play.get('protection', 'N/A')}")
                        if formatted_play.get('routes'):
                            st.markdown("**Routes:**")
                            for receiver, route in formatted_play['routes'].items():
                                st.markdown(f"• {receiver.replace('_', ' ').title()}: {route.replace('_', ' ').title()}")
                    else:
                        st.markdown(f"**Blocking:** {formatted_play.get('blocking', 'N/A')}")
                        st.markdown(f"**Ball Carrier:** {formatted_play.get('ball_carrier', 'N/A')}")
                
                with col2:
                    # NO success rate shown in learner mode
                    st.markdown("**Make your read!**")
                    st.markdown("*Trust your instincts based on what you see in the defense.*")
                
                # Selection button with stable key - only show if play not completed
                if not st.session_state.play_completed:
                    if st.button(f"Call {formatted_play['name']}", key=f"learner_stable_{i}_{formatted_play['name'].replace(' ', '_')}"):
                        # Run simulation immediately and store result
                        with st.spinner("Simulating play..."):
                            result = simulator.simulate_play(scenario, formatted_play['full_data'], minimum_yards)
                        
                        # Store result and mark play as completed
                        st.session_state.current_result = result
                        st.session_state.play_completed = True
                        
                        # Update stats
                        update_game_stats(result)
                        
                        st.rerun()
                else:
                    st.info("Play completed! Choose your next action below.")
    
    return None
def display_play_selection(offense_engine, formation_name, simulator, scenario, minimum_yards):
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
                        if not st.session_state.play_completed:
                            # Get full play details for comprehensive analysis
                            full_play_details = offense_engine.get_play_full_details(
                                play['formation'], 
                                play['key']
                            )
                            
                            if full_play_details:
                                comprehensive_play_data = {**play, **full_play_details}
                            else:
                                comprehensive_play_data = play
                            
                            # Run simulation immediately and store result
                            with st.spinner("Simulating play..."):
                                result = simulator.simulate_play(scenario, comprehensive_play_data, minimum_yards)
                            
                            # Store result and mark play as completed
                            st.session_state.current_result = result
                            st.session_state.play_completed = True
                            
                            # Update stats
                            update_game_stats(result)
                            
                            st.rerun()
                        else:
                            st.info("Play completed! Choose your next action below.")
    
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
                        if not st.session_state.play_completed:
                            # Get full play details for comprehensive analysis
                            full_play_details = offense_engine.get_play_full_details(
                                play['formation'], 
                                play['key']
                            )
                            
                            if full_play_details:
                                comprehensive_play_data = {**play, **full_play_details}
                            else:
                                comprehensive_play_data = play
                            
                            # Run simulation immediately and store result
                            with st.spinner("Simulating play..."):
                                result = simulator.simulate_play(scenario, comprehensive_play_data, minimum_yards)
                            
                            # Store result and mark play as completed
                            st.session_state.current_result = result
                            st.session_state.play_completed = True
                            
                            # Update stats
                            update_game_stats(result)
                            
                            st.rerun()
                        else:
                            st.info("Play completed! Choose your next action below.")
    
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

def display_pre_snap_read_settings():
    """Display pre-snap read settings in sidebar"""
    st.sidebar.markdown("### 👁️ Pre-Snap Read Settings")
    st.sidebar.markdown("*Control what you can see about the defense*")
    
    # Create difficulty presets
    difficulty = st.sidebar.radio(
        "**Difficulty Level:**",
        ["👶 Rookie", "🎮 Custom", "🧠 Pro", "🔥 Elite"],
        index=1,  # Default to Custom
        key="difficulty_level"
    )
    
    # Preset configurations
    if difficulty == "👶 Rookie":
        # Rookie: See almost everything (training mode)
        visibility_settings = {
            'formation_name': True,
            'personnel': True,
            'coverage_name': True,
            'coverage_type': True,
            'blitz_name': False,
            'rushers': True,
            'coverage_adjustment': False,
            'field_visual': True
        }
        st.sidebar.info("🎓 **Rookie Mode:** Most information visible for learning")
        
    elif difficulty == "🧠 Pro":
        # Pro: Realistic pre-snap reads
        visibility_settings = {
            'formation_name': True,
            'personnel': True,
            'coverage_name': False,
            'coverage_type': False,
            'blitz_name': False,
            'rushers': False,
            'coverage_adjustment': False,
            'field_visual': True
        }
        st.sidebar.info("🏈 **Pro Mode:** Realistic pre-snap information only")
        
    elif difficulty == "🔥 Elite":
        # Elite: Visual only - no text information
        visibility_settings = {
            'formation_name': False,
            'personnel': False,
            'coverage_name': False,
            'coverage_type': False,
            'blitz_name': False,
            'rushers': False,
            'coverage_adjustment': False,
            'field_visual': True
        }
        st.sidebar.info("🔥 **Elite Mode:** Visual only - identify the formation and read the defense yourself!")
        
    else:  # Custom
        st.sidebar.info("🎮 **Custom Mode:** Choose your own settings below")
        
        # Custom settings - show checkboxes
        st.sidebar.markdown("**Visible Information:**")
        
        visibility_settings = {}
        
        # Always show field visual option first
        visibility_settings['field_visual'] = st.sidebar.checkbox(
            "🏈 Field Visual", 
            value=True,
            help="Show the X's and O's field representation"
        )
        
        # Formation information (easier to see)
        st.sidebar.markdown("**Formation Info:**")
        visibility_settings['formation_name'] = st.sidebar.checkbox(
            "📋 Formation Name", 
            value=True,
            help="Defense formation (4-3, Nickel, etc.) - usually obvious"
        )
        
        visibility_settings['personnel'] = st.sidebar.checkbox(
            "👥 Personnel Package", 
            value=True,
            help="Number of DBs, LBs, etc. - can count players"
        )
        
        # Coverage information (harder to determine)
        st.sidebar.markdown("**Coverage Info:**")
        visibility_settings['coverage_name'] = st.sidebar.checkbox(
            "🎯 Coverage Name", 
            value=False,
            help="Specific coverage (Cover 2, Cover 3, etc.) - hard to tell pre-snap"
        )
        
        visibility_settings['coverage_type'] = st.sidebar.checkbox(
            "🔍 Coverage Type", 
            value=False,
            help="Man vs Zone - requires experience to identify"
        )
        
        # Blitz information (very hard to determine)
        st.sidebar.markdown("**Pressure Info:**")
        visibility_settings['blitz_name'] = st.sidebar.checkbox(
            "🔥 Blitz Package", 
            value=False,
            help="Specific blitz name - nearly impossible to know pre-snap"
        )
        
        visibility_settings['rushers'] = st.sidebar.checkbox(
            "⚡ Number of Rushers", 
            value=False,
            help="How many will rush - sometimes can guess from alignment"
        )
        
        visibility_settings['coverage_adjustment'] = st.sidebar.checkbox(
            "🔄 Coverage Adjustment", 
            value=False,
            help="How coverage changes with blitz - impossible to know pre-snap"
        )
    
    return visibility_settings

def main():
    """Main Streamlit app with pre-snap read settings"""
    
    # Header
    st.markdown('<h1 class="main-header">🏈 QB Pre-Snap Simulator</h1>', unsafe_allow_html=True)
    
    # Tom Brady Quote
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f4e79;
        margin: 20px 0;
        font-style: italic;
        text-align: center;
    ">
        <p style="margin: 0; font-size: 16px; color: #2c3e50; line-height: 1.6;">
            "I could figure out what they were doing before they did it because that's how I learned the game... Unfortunately, most quarterbacks aren't playing the game like that anymore. They're fast when they get out of the pocket when they have to make decisions, but I didn't snap the ball unless I knew what they were doing... The one benefit you have as a quarterback before you snap the ball, you know where everybody on your team is running... If I look at the defense and I say 'None of my guys are going to be open based on this coverage', I don't need to snap the ball. I can run something different."
        </p>
        <p style="margin: 10px 0 0 0; font-weight: bold; color: #1f4e79;">
            — Tom Brady
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Test your quarterback decision-making skills by reading defenses and calling the right plays!**")
    
    # Load engines
    try:
        if not st.session_state.engines_loaded:
            with st.spinner("Loading defensive and offensive formations..."):
                defense_engine, offense_engine, simulator, strategic_selector, library_browser, field_visualizer = load_engines()
                st.session_state.defense_engine = defense_engine
                st.session_state.offense_engine = offense_engine
                st.session_state.simulator = simulator
                st.session_state.strategic_selector = strategic_selector
                st.session_state.library_browser = library_browser
                st.session_state.field_visualizer = field_visualizer
                st.session_state.engines_loaded = True
                st.success("✅ All formations loaded successfully!")
        
        defense_engine = st.session_state.defense_engine
        offense_engine = st.session_state.offense_engine
        simulator = st.session_state.simulator
        strategic_selector = st.session_state.strategic_selector
        library_browser = st.session_state.library_browser
        field_visualizer = st.session_state.field_visualizer
        
    except Exception as e:
        st.error(f"❌ Error loading formations: {e}")
        st.error("Make sure all JSON files are in the correct directories (data/defenses/ and data/offenses/)")
        return
    
    # Sidebar controls
    st.sidebar.markdown("### 🎮 Game Controls")
    
    # Navigation
    page = st.sidebar.radio(
        "Choose Section:",
        ["🎯 Play Game", "📚 Formation Library"],
        key="navigation_radio"
    )
    
    if page == "📚 Formation Library":
        # Display library
        st.markdown('<h1 class="main-header">📚 Formation Library</h1>', unsafe_allow_html=True)
        st.markdown("**Explore all offensive and defensive formations, plays, and coverage packages in detail**")
        
        # Create tabs for library
        off_tab, def_tab, compare_tab = st.tabs(["🏈 Offensive Library", "🛡️ Defensive Library", "⚖️ Compare Formations"])
        
        with off_tab:
            library_browser.display_offensive_library()
        
        with def_tab:
            library_browser.display_defensive_library()
        
        with compare_tab:
            library_browser.display_formation_comparison()
        
        return  # Exit early for library view
    
    # Pre-Snap Read Settings (only show during game)
    visibility_settings = display_pre_snap_read_settings()
    
    # Game mode selection
    game_mode = st.sidebar.radio(
        "Choose Game Mode:",
        ["🎓 Learner Mode (5 Plays)", "⚡ Pro Mode (Full Playbook)"],
        key="game_mode_radio"
    )
    
    # Update session state based on selection
    if "Learner" in game_mode:
        st.session_state.game_mode = 'learner'
    else:
        st.session_state.game_mode = 'pro'
    
    # Generate new scenario button
    if st.sidebar.button("🎲 Generate New Scenario", type="primary"):
        st.session_state.current_scenario = defense_engine.get_random_scenario()
        st.session_state.minimum_yards = simulator.generate_minimum_yards()
        st.session_state.strategic_plays = None  # Reset strategic plays
        st.session_state.shuffled_play_order = None  # Reset shuffled order
        st.session_state.play_completed = False  # Reset play completion
        st.session_state.current_result = None  # Reset current result
        st.rerun()
    
    # Display game stats
    display_game_stats()
    
    # Main game area
    if st.session_state.current_scenario is None:
        st.info("👆 Click 'Generate New Scenario' in the sidebar to start playing!")
        st.markdown("### 💡 How to Use Pre-Snap Read Settings:")
        st.markdown("""
        - **👶 Rookie Mode:** See most defensive information (great for learning)
        - **🎮 Custom Mode:** Choose exactly what you can see
        - **🧠 Pro Mode:** Realistic pre-snap reads only
        - **🔥 Elite Mode:** Minimal information - read the defense like a pro!
        
        **Real QBs** can usually see the formation and personnel, but coverage and blitz packages are much harder to identify before the snap!
        """)
        return
    
    scenario = st.session_state.current_scenario
    minimum_yards = st.session_state.minimum_yards
    
    # Display defensive scenario with visibility settings
    st.markdown("## 🛡️ Defensive Scenario")
    display_defensive_scenario(scenario, field_visualizer, minimum_yards, visibility_settings)
    
    # Display yards needed
    display_yards_needed(minimum_yards)
    
    # Different UI based on game mode
    if st.session_state.game_mode == 'learner':
        # Learner mode - 5 plays without appropriateness revealed
        st.markdown("## 🎓 Learner Mode")
        st.markdown("*Read the defense and make your call. You'll learn if it was a good choice after the play!*")
        
        # Generate strategic plays if not already done
        if st.session_state.strategic_plays is None:
            with st.spinner("Preparing 5 plays for this scenario..."):
                strategic_result = strategic_selector.get_strategic_play_selection(scenario, minimum_yards)
                st.session_state.strategic_plays = strategic_result
        
        # Display learner mode options (no appropriateness shown)
        display_learner_mode_plays(
            st.session_state.strategic_plays, 
            simulator, 
            scenario, 
            minimum_yards
        )
        
        # Show results if play is completed
        if st.session_state.play_completed and st.session_state.current_result:
            result = st.session_state.current_result
            
            # Display results with LEARNING feedback
            st.markdown("## 📊 Play Result & Learning")
            display_result(result)
            
            # REVEAL the appropriateness after the play
            st.markdown("### 🧑‍🏫 Learning Analysis")
            appropriateness = result['appropriateness_category']
            
            if appropriateness == 'Perfect':
                st.success("📚 **EXCELLENT READ!** 🎯 This was a Perfect call - you correctly identified and exploited a weakness in this defense!")
            elif appropriateness == 'Good':
                st.success("📚 **GOOD READ!** ✅ This was a solid choice that worked well against this defensive setup.")
            elif appropriateness == 'Average':
                st.info("📚 **DECENT READ** ⚖️ This was an Average call - not bad, but there were better options available against this defense.")
            elif appropriateness == 'Poor':
                st.warning("📚 **LEARNING MOMENT** ⚠️ This was a Poor choice - the defense had advantages. Study what they were showing!")
            elif appropriateness == 'Terrible':
                st.error("📚 **TOUGH LESSON** ❌ This was a Terrible call - this defense was set up perfectly to stop that play. Learn from this!")
            elif appropriateness == 'Overkill':
                st.info("📚 **CREATIVE CHOICE** 🚀 This was Overkill - it worked but was more complex than needed for this situation.")
            
            # Option to try same scenario again
            if st.button("🔄 Try This Scenario Again", type="secondary"):
                st.session_state.strategic_plays = None
                st.session_state.shuffled_play_order = None  # Reset shuffled order
                st.session_state.play_completed = False  # Reset play completion
                st.session_state.current_result = None  # Reset current result
                st.rerun()
    
    elif st.session_state.game_mode == 'pro':
        # Pro mode - full playbook access
        st.markdown("## ⚡ Pro Mode")
        st.markdown("*Full playbook access - browse through all formations and plays.*")
        
        # Formation selection
        st.markdown("### ⚔️ Select Your Formation")
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
            selected_play = display_play_selection(offense_engine, formation_name, simulator, scenario, minimum_yards)
            
            # Show results if play is completed
            if st.session_state.play_completed and st.session_state.current_result:
                result = st.session_state.current_result
                
                # Display results
                st.markdown("## 📊 Play Result")
                display_result(result)
                
                # Option to try same scenario again
                if st.button("🔄 Try This Scenario Again", type="secondary"):
                    st.session_state.play_completed = False  # Reset play completion
                    st.session_state.current_result = None  # Reset current result
                    st.rerun()

if __name__ == "__main__":
    main()