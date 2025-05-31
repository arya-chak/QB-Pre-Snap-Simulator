"""
Library Browser
Author: Arya Chakraborty

Comprehensive library for viewing all offensive and defensive formations and plays.
Displays detailed information from JSON files in an organized, searchable format.
"""

import streamlit as st
from defense_engine import DefenseEngine
from offense_engine import OffenseEngine

class LibraryBrowser:
    def __init__(self, defense_engine, offense_engine):
        """Initialize library with loaded engines"""
        self.defense_engine = defense_engine
        self.offense_engine = offense_engine
    
    def display_offensive_library(self):
        """Display comprehensive offensive formations and plays"""
        st.markdown("## 🏈 Offensive Formations Library")
        st.markdown("*Explore all offensive formations and their plays in detail*")
        
        if not self.offense_engine.formations:
            st.error("No offensive formations loaded")
            return
        
        # Formation selection
        formation_names = list(self.offense_engine.formations.keys())
        selected_formation = st.selectbox(
            "Select Formation to Explore:",
            formation_names,
            format_func=lambda x: self.offense_engine.formations[x]['formation_name'],
            key="offensive_library_select"
        )
        
        if selected_formation:
            self._display_offensive_formation_details(selected_formation)
    
    def _display_offensive_formation_details(self, formation_name):
        """Display detailed information about an offensive formation"""
        formation_data = self.offense_engine.formations[formation_name]
        
        # Formation header
        st.markdown(f"### {formation_data['formation_name']}")
        
        # Basic formation info
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📋 Formation Details**")
            st.write(f"**Personnel:** {formation_data['personnel']}")
            st.write(f"**Package:** {formation_data.get('personnel_package', 'N/A')}")
            st.write(f"**Description:** {formation_data['description']}")
        
        with col2:
            st.markdown("**⚡ Formation Strengths**")
            for strength in formation_data.get('formation_strengths', [])[:5]:
                st.write(f"• {strength.replace('_', ' ').title()}")
        
        # Formation weaknesses and situations
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**⚠️ Formation Weaknesses**")
            for weakness in formation_data.get('formation_weaknesses', [])[:5]:
                st.write(f"• {weakness.replace('_', ' ').title()}")
        
        with col4:
            st.markdown("**🎯 Optimal Situations**")
            for situation in formation_data.get('optimal_situations', [])[:5]:
                st.write(f"• {situation.replace('_', ' ').title()}")
        
        st.divider()
        
        # Plays section
        st.markdown("### 📋 Plays from this Formation")
        
        # Create tabs for passing and running plays
        pass_tab, run_tab = st.tabs(["🎯 Passing Plays", "🏃 Running Plays"])
        
        with pass_tab:
            self._display_passing_plays(formation_data.get('passing_plays', {}))
        
        with run_tab:
            self._display_running_plays(formation_data.get('running_plays', {}))
    
    def _display_passing_plays(self, passing_plays):
        """Display detailed passing play information"""
        if not passing_plays:
            st.info("No passing plays available for this formation")
            return
        
        st.markdown(f"**{len(passing_plays)} Passing Plays Available**")
        
        for play_key, play_data in passing_plays.items():
            with st.expander(f"🎯 {play_data['name']}", expanded=False):
                
                # Basic play info
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Concept:** {play_data['concept']}")
                    st.markdown(f"**Protection:** {play_data.get('protection', 'N/A')}")
                    st.markdown(f"**Target Yards:** {play_data.get('target_yards', 'N/A')}")
                    st.markdown(f"**Time to Throw:** {play_data.get('time_to_throw', 'N/A').replace('_', ' ').title()}")
                
                with col2:
                    if play_data.get('routes'):
                        st.markdown("**Routes:**")
                        for receiver, route in play_data['routes'].items():
                            st.write(f"• {receiver.replace('_', ' ').title()}: {route.replace('_', ' ').title()}")
                
                # Strengths and weaknesses
                col3, col4 = st.columns(2)
                
                with col3:
                    if play_data.get('best_against'):
                        st.markdown("**✅ Best Against:**")
                        for item in play_data['best_against']:
                            st.write(f"• {item.replace('_', ' ').title()}")
                    
                    if play_data.get('strengths'):
                        st.markdown("**💪 Strengths:**")
                        for strength in play_data['strengths']:
                            st.write(f"• {strength.replace('_', ' ').title()}")
                
                with col4:
                    if play_data.get('worst_against'):
                        st.markdown("**❌ Worst Against:**")
                        for item in play_data['worst_against']:
                            st.write(f"• {item.replace('_', ' ').title()}")
                    
                    if play_data.get('weaknesses'):
                        st.markdown("**⚠️ Weaknesses:**")
                        for weakness in play_data['weaknesses']:
                            st.write(f"• {weakness.replace('_', ' ').title()}")
    
    def _display_running_plays(self, running_plays):
        """Display detailed running play information"""
        if not running_plays:
            st.info("No running plays available for this formation")
            return
        
        st.markdown(f"**{len(running_plays)} Running Plays Available**")
        
        for play_key, play_data in running_plays.items():
            with st.expander(f"🏃 {play_data['name']}", expanded=False):
                
                # Basic play info
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Concept:** {play_data['concept']}")
                    st.markdown(f"**Blocking Scheme:** {play_data.get('blocking_scheme', 'N/A').replace('_', ' ').title()}")
                    st.markdown(f"**Ball Carrier:** {play_data.get('ball_carrier', 'N/A').replace('_', ' ').title()}")
                    st.markdown(f"**Target Yards:** {play_data.get('target_yards', 'N/A')}")
                
                with col2:
                    st.markdown(f"**Lead Blocker:** {play_data.get('lead_blocker', 'N/A').replace('_', ' ').title()}")
                    st.markdown(f"**Target Gap:** {play_data.get('target_gap', 'N/A').replace('_', ' ').title()}")
                
                # Strengths and weaknesses
                col3, col4 = st.columns(2)
                
                with col3:
                    if play_data.get('best_against'):
                        st.markdown("**✅ Best Against:**")
                        for item in play_data['best_against']:
                            st.write(f"• {item.replace('_', ' ').title()}")
                    
                    if play_data.get('strengths'):
                        st.markdown("**💪 Strengths:**")
                        for strength in play_data['strengths']:
                            st.write(f"• {strength.replace('_', ' ').title()}")
                
                with col4:
                    if play_data.get('worst_against'):
                        st.markdown("**❌ Worst Against:**")
                        for item in play_data['worst_against']:
                            st.write(f"• {item.replace('_', ' ').title()}")
                    
                    if play_data.get('weaknesses'):
                        st.markdown("**⚠️ Weaknesses:**")
                        for weakness in play_data['weaknesses']:
                            st.write(f"• {weakness.replace('_', ' ').title()}")
    
    def display_defensive_library(self):
        """Display comprehensive defensive formations and coverages"""
        st.markdown("## 🛡️ Defensive Formations Library")
        st.markdown("*Explore all defensive formations and their coverage packages in detail*")
        
        if not self.defense_engine.formations:
            st.error("No defensive formations loaded")
            return
        
        # Formation selection
        formation_names = list(self.defense_engine.formations.keys())
        selected_formation = st.selectbox(
            "Select Formation to Explore:",
            formation_names,
            format_func=lambda x: self.defense_engine.formations[x]['formation_name'],
            key="defensive_library_select"
        )
        
        if selected_formation:
            self._display_defensive_formation_details(selected_formation)
    
    def _display_defensive_formation_details(self, formation_name):
        """Display detailed information about a defensive formation"""
        formation_data = self.defense_engine.formations[formation_name]
        
        # Formation header
        st.markdown(f"### {formation_data['formation_name']}")
        
        # Basic formation info
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📋 Formation Details**")
            st.write(f"**Personnel:** {formation_data['personnel']}")
            st.write(f"**Description:** {formation_data['description']}")
        
        with col2:
            st.markdown(f"**🎯 Coverage Options Available: {len(formation_data['coverages'])}**")
            for coverage_name in formation_data['coverages'].keys():
                coverage_display = formation_data['coverages'][coverage_name]['name']
                st.write(f"• {coverage_display}")
        
        st.divider()
        
        # Coverage details
        st.markdown("### 🛡️ Coverage Packages")
        
        coverage_names = list(formation_data['coverages'].keys())
        selected_coverage = st.selectbox(
            "Select Coverage to Explore:",
            coverage_names,
            format_func=lambda x: formation_data['coverages'][x]['name'],
            key=f"coverage_select_{formation_name}"
        )
        
        if selected_coverage:
            self._display_coverage_details(formation_data['coverages'][selected_coverage])
    
    def _display_coverage_details(self, coverage_data):
        """Display detailed coverage information"""
        st.markdown(f"#### {coverage_data['name']}")
        
        # Basic coverage info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Coverage Details**")
            st.write(f"**Type:** {coverage_data['coverage_type'].title()}")
            st.write(f"**Description:** {coverage_data['description']}")
        
        with col2:
            st.markdown(f"**🔥 Blitz Packages: {len(coverage_data['blitz_packages'])}**")
            for blitz_name in coverage_data['blitz_packages'].keys():
                blitz_display = coverage_data['blitz_packages'][blitz_name]['name']
                st.write(f"• {blitz_display}")
        
        # Coverage strengths and weaknesses
        col3, col4 = st.columns(2)
        
        with col3:
            if coverage_data.get('base_strengths'):
                st.markdown("**💪 Base Strengths:**")
                for strength in coverage_data['base_strengths']:
                    st.write(f"• {strength.replace('_', ' ').title()}")
            
            if coverage_data.get('optimal_situations'):
                st.markdown("**🎯 Optimal Situations:**")
                for situation in coverage_data['optimal_situations']:
                    st.write(f"• {situation.replace('_', ' ').title()}")
        
        with col4:
            if coverage_data.get('base_weaknesses'):
                st.markdown("**⚠️ Base Weaknesses:**")
                for weakness in coverage_data['base_weaknesses']:
                    st.write(f"• {weakness.replace('_', ' ').title()}")
            
            if coverage_data.get('vulnerable_to'):
                st.markdown("**❌ Vulnerable To:**")
                for vulnerability in coverage_data['vulnerable_to']:
                    st.write(f"• {vulnerability.replace('_', ' ').title()}")
        
        # Blitz packages
        st.markdown("#### 🔥 Blitz Packages")
        
        for blitz_key, blitz_data in coverage_data['blitz_packages'].items():
            with st.expander(f"🔥 {blitz_data['name']}", expanded=False):
                
                # Basic blitz info
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Blitzer:** {blitz_data.get('blitzer', 'N/A').replace('_', ' ').title()}")
                    st.markdown(f"**Total Rushers:** {blitz_data.get('rushers', 'N/A')}")
                    st.markdown(f"**Coverage Adjustment:** {blitz_data.get('coverage_adjustment', 'N/A').replace('_', ' ').title()}")
                
                with col2:
                    if blitz_data.get('best_against'):
                        st.markdown("**🎯 Best Against:**")
                        for item in blitz_data['best_against'][:3]:
                            st.write(f"• {item.replace('_', ' ').title()}")
                
                # Detailed strengths and weaknesses
                col3, col4 = st.columns(2)
                
                with col3:
                    if blitz_data.get('run_strengths'):
                        st.markdown("**🏃 Run Strengths:**")
                        for strength in blitz_data['run_strengths']:
                            st.write(f"• {strength.replace('_', ' ').title()}")
                    
                    if blitz_data.get('pass_strengths'):
                        st.markdown("**🎯 Pass Strengths:**")
                        for strength in blitz_data['pass_strengths']:
                            st.write(f"• {strength.replace('_', ' ').title()}")
                
                with col4:
                    if blitz_data.get('run_weaknesses'):
                        st.markdown("**🏃 Run Weaknesses:**")
                        for weakness in blitz_data['run_weaknesses']:
                            st.write(f"• {weakness.replace('_', ' ').title()}")
                    
                    if blitz_data.get('pass_weaknesses'):
                        st.markdown("**🎯 Pass Weaknesses:**")
                        for weakness in blitz_data['pass_weaknesses']:
                            st.write(f"• {weakness.replace('_', ' ').title()}")
    
    def display_formation_comparison(self):
        """Display side-by-side comparison of formations"""
        st.markdown("## ⚖️ Formation Comparison Tool")
        st.markdown("*Compare different formations side by side*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏈 Offensive Formation")
            off_formations = list(self.offense_engine.formations.keys())
            selected_off = st.selectbox(
                "Select Offensive Formation:",
                off_formations,
                format_func=lambda x: self.offense_engine.formations[x]['formation_name'],
                key="compare_off"
            )
        
        with col2:
            st.markdown("### 🛡️ Defensive Formation")
            def_formations = list(self.defense_engine.formations.keys())
            selected_def = st.selectbox(
                "Select Defensive Formation:",
                def_formations,
                format_func=lambda x: self.defense_engine.formations[x]['formation_name'],
                key="compare_def"
            )
        
        if selected_off and selected_def:
            self._display_matchup_comparison(selected_off, selected_def)
    
    def _display_matchup_comparison(self, off_formation, def_formation):
        """Display comparison between offensive and defensive formations"""
        off_data = self.offense_engine.formations[off_formation]
        def_data = self.defense_engine.formations[def_formation]
        
        st.divider()
        st.markdown("### 📊 Formation Matchup Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 🏈 {off_data['formation_name']}")
            st.write(f"**Personnel:** {off_data['personnel']}")
            st.write(f"**Package:** {off_data.get('personnel_package', 'N/A')}")
            
            st.markdown("**Key Strengths:**")
            for strength in off_data.get('formation_strengths', [])[:4]:
                st.write(f"• {strength.replace('_', ' ').title()}")
            
            st.markdown("**Optimal Situations:**")
            for situation in off_data.get('optimal_situations', [])[:4]:
                st.write(f"• {situation.replace('_', ' ').title()}")
        
        with col2:
            st.markdown(f"#### 🛡️ {def_data['formation_name']}")
            st.write(f"**Personnel:** {def_data['personnel']}")
            st.write(f"**Coverages Available:** {len(def_data['coverages'])}")
            
            # Get a sample coverage for analysis
            sample_coverage = list(def_data['coverages'].values())[0]
            st.markdown("**Key Strengths (Base Coverage):**")
            for strength in sample_coverage.get('base_strengths', [])[:4]:
                st.write(f"• {strength.replace('_', ' ').title()}")
            
            st.markdown("**Optimal Situations:**")
            for situation in sample_coverage.get('optimal_situations', [])[:4]:
                st.write(f"• {situation.replace('_', ' ').title()}")
        
        # Matchup insights
        st.markdown("### 🎯 Matchup Insights")
        st.info("💡 **Tip:** Look for overlaps between the offensive formation's strengths and the defensive formation's weaknesses to identify potential advantages!")

def main():
    """Standalone library browser for testing"""
    st.set_page_config(page_title="Formation Library", page_icon="📚", layout="wide")
    
    st.markdown("# 📚 Football Formation Library")
    
    # Initialize engines
    @st.cache_resource
    def load_engines():
        defense_engine = DefenseEngine()
        offense_engine = OffenseEngine()
        defense_engine.load_all_formations()
        offense_engine.load_all_formations()
        return defense_engine, offense_engine
    
    try:
        defense_engine, offense_engine = load_engines()
        library = LibraryBrowser(defense_engine, offense_engine)
        
        # Create tabs
        off_tab, def_tab, compare_tab = st.tabs(["🏈 Offensive Library", "🛡️ Defensive Library", "⚖️ Compare Formations"])
        
        with off_tab:
            library.display_offensive_library()
        
        with def_tab:
            library.display_defensive_library()
        
        with compare_tab:
            library.display_formation_comparison()
            
    except Exception as e:
        st.error(f"Error loading formation data: {e}")

if __name__ == "__main__":
    main()