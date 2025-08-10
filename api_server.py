"""
FastAPI Backend for QB Pre-Snap Simulator Mobile App
Author: Arya Chakraborty

This API serves your existing Python logic to the React Native mobile app.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import sys
import os

# Add the current directory to the path so we can import our engines
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from defense_engine import DefenseEngine
from offense_engine import OffenseEngine
from comprehensive_play_simulator import ComprehensivePlaySimulator
from strategic_play_selector import StrategicPlaySelector

# Initialize FastAPI app
app = FastAPI(
    title="QB Pre-Snap Simulator API",
    description="API for the QB Pre-Snap Simulator mobile app",
    version="1.0.0"
)

# Add CORS middleware to allow requests from mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your mobile app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
defense_engine = DefenseEngine()
offense_engine = OffenseEngine()
simulator = ComprehensivePlaySimulator()
strategic_selector = None  # Will be initialized after engines load

# Load all data on startup
@app.on_event("startup")
async def startup_event():
    """Load all formation data when the API starts"""
    global strategic_selector
    try:
        defense_engine.load_all_formations()
        offense_engine.load_all_formations()
        
        # Initialize strategic selector after engines are loaded
        strategic_selector = StrategicPlaySelector(offense_engine, simulator)
        
        print("✅ All formations loaded successfully!")
        print("✅ Strategic Play Selector initialized!")
    except Exception as e:
        print(f"❌ Error loading formations: {e}")

# Pydantic models for request/response
class PlaySimulationRequest(BaseModel):
    offensive_play: Dict
    defensive_scenario: Dict
    minimum_yards: int

class StrategicPlaysRequest(BaseModel):
    scenario: Dict[str, Any]
    minimum_yards: int

class PlayResult(BaseModel):
    success: bool
    yards_gained: int
    outcome_type: str
    appropriateness_category: str
    description: str

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "QB Pre-Snap Simulator API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/defensive-scenario")
async def get_random_defensive_scenario():
    """Get a random defensive scenario"""
    try:
        scenario = defense_engine.get_random_scenario()
        if not scenario:
            raise HTTPException(status_code=500, detail="Could not generate defensive scenario")
        
        # Add minimum yards needed
        minimum_yards = simulator.generate_minimum_yards()
        
        return {
            "scenario": scenario,
            "minimum_yards": minimum_yards,
            "yard_range": simulator.determine_yard_range_category(minimum_yards)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating scenario: {str(e)}")

@app.get("/api/offensive-formations")
async def get_offensive_formations():
    """Get all available offensive formations"""
    try:
        formations = offense_engine.get_available_formations()
        if not formations:
            raise HTTPException(status_code=500, detail="No offensive formations available")
        
        return {"formations": formations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting formations: {str(e)}")

@app.get("/api/offensive-formations/{formation_name}/plays")
async def get_formation_plays(formation_name: str):
    """Get all plays for a specific formation"""
    try:
        plays = offense_engine.get_formation_plays(formation_name)
        if not plays:
            raise HTTPException(status_code=404, detail=f"No plays found for formation: {formation_name}")
        
        return {"formation": formation_name, "plays": plays}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting plays: {str(e)}")

@app.post("/api/strategic-plays")
async def get_strategic_plays(request: StrategicPlaysRequest):
    """Get 5 strategic plays for learner mode"""
    try:
        if strategic_selector is None:
            raise HTTPException(status_code=500, detail="Strategic selector not initialized")
        
        # Use the strategic selector to get 5 plays
        strategic_result = strategic_selector.get_strategic_play_selection(
            request.scenario, 
            request.minimum_yards
        )
        
        # ADD DEBUG LOGGING
        print(f"\n🎯 Strategic Play Selection Debug:")
        print(f"Defense: {request.scenario.get('formation_data', {}).get('formation_name')} - {request.scenario.get('coverage_data', {}).get('name')}")
        print(f"Minimum Yards: {request.minimum_yards}")
        print(f"Category counts: {strategic_result['category_counts']}")
        
        for category, play_eval in strategic_result['strategic_plays'].items():
            if play_eval:
                play_name = play_eval.get('play_data', {}).get('name', 'Unknown')
                formation = play_eval.get('formation_name', 'Unknown')
                appropriateness = play_eval.get('appropriateness_category', 'Unknown')
                print(f"  {category}: {play_name} ({formation}) - {appropriateness}")
            else:
                print(f"  {category}: No play found")
        
        return {
            "strategic_plays": strategic_result['strategic_plays'],
            "category_counts": strategic_result['category_counts'],
            "diversity_info": strategic_result['diversity_info'],
            "total_plays_evaluated": strategic_result['total_plays_evaluated']
        }
        
    except Exception as e:
        print(f"❌ Strategic plays error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating strategic plays: {str(e)}")

@app.post("/api/simulate-play")
async def simulate_play(request: PlaySimulationRequest):
    """Simulate a play and return the result"""
    try:
        # Get full play details for comprehensive analysis
        full_play_details = offense_engine.get_play_full_details(
            request.offensive_play.get('formation'),
            request.offensive_play.get('key')
        )
        
        if full_play_details:
            # Merge basic play info with full details
            comprehensive_play_data = {
                **request.offensive_play,
                **full_play_details
            }
            result = simulator.simulate_play(
                request.defensive_scenario,
                comprehensive_play_data,
                request.minimum_yards
            )
        else:
            # Fallback to basic play data
            result = simulator.simulate_play(
                request.defensive_scenario,
                request.offensive_play,
                request.minimum_yards
            )
        
        return {
            "success": result['overall_success'],
            "yards_gained": result['yards_gained'],
            "yards_needed": result['minimum_yards_needed'],
            "outcome_type": result['outcome_type'],
            "appropriateness_category": result['appropriateness_category'],
            "description": result['description'],
            "yard_range": result['yard_range'],
            "success_rate_used": result['success_rate_used']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating play: {str(e)}")

@app.get("/api/stats")
async def get_api_stats():
    """Get API statistics and loaded data count"""
    try:
        total_def_scenarios = 0
        for formation in defense_engine.formations.values():
            for coverage in formation["coverages"].values():
                total_def_scenarios += len(coverage["blitz_packages"])
        
        total_off_plays = 0
        for formation in offense_engine.formations.values():
            total_off_plays += len(formation.get("passing_plays", {}))
            total_off_plays += len(formation.get("running_plays", {}))
        
        return {
            "defensive_formations": len(defense_engine.formations),
            "offensive_formations": len(offense_engine.formations),
            "total_defensive_scenarios": total_def_scenarios,
            "total_offensive_plays": total_off_plays,
            "total_possible_matchups": total_def_scenarios * total_off_plays
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/api/defensive-formation/{formation_name}/positions")
async def get_formation_positions(formation_name: str, yards_to_go: int = 10):
    """Get player positions for SVG field visualization"""
    try:
        # Import the mobile-friendly field visualizer
        from mobile_field_visualizer import MobileFieldVisualizer
        
        # Create visualizer with yards to go
        visualizer = MobileFieldVisualizer(yards_to_go=yards_to_go)
        
        # Get formation data
        formation_data = visualizer.get_formation_data(formation_name)
        
        # Convert to mobile-friendly format with additional metadata
        players = []
        position_types = {
            # Defensive Line
            'DE_weak': {'pos': 'E', 'type': 'dline', 'label': 'Weak DE'},
            'DE_strong': {'pos': 'E', 'type': 'dline', 'label': 'Strong DE'},
            'DT_weak': {'pos': 'T', 'type': 'dline', 'label': 'Weak DT'},
            'DT_strong': {'pos': 'T', 'type': 'dline', 'label': 'Strong DT'},
            'NT': {'pos': 'N', 'type': 'dline', 'label': 'Nose Tackle'},
            
            # Linebackers
            'WLB': {'pos': 'W', 'type': 'lb', 'label': 'Weak LB'},
            'MLB': {'pos': 'M', 'type': 'lb', 'label': 'Middle LB'},
            'SLB': {'pos': 'S', 'type': 'lb', 'label': 'Strong LB'},
            'OLB_weak': {'pos': 'B', 'type': 'lb', 'label': 'Weak OLB'},
            'OLB_strong': {'pos': 'B', 'type': 'lb', 'label': 'Strong OLB'},
            'ILB_weak': {'pos': 'M', 'type': 'lb', 'label': 'Weak ILB'},
            'ILB_strong': {'pos': 'M', 'type': 'lb', 'label': 'Strong ILB'},
            'MLB_weak': {'pos': 'M', 'type': 'lb', 'label': 'Weak MLB'},
            'MLB_strong': {'pos': 'M', 'type': 'lb', 'label': 'Strong MLB'},
            'ROVER': {'pos': 'R', 'type': 'lb', 'label': 'Rover LB'},
            
            # Secondary
            'CB_weak': {'pos': 'C', 'type': 'db', 'label': 'Weak CB'},
            'CB_strong': {'pos': 'C', 'type': 'db', 'label': 'Strong CB'},
            'FS': {'pos': 'F', 'type': 'db', 'label': 'Free Safety'},
            'SS': {'pos': 'S', 'type': 'db', 'label': 'Strong Safety'},
            'NB': {'pos': '△', 'type': 'db', 'label': 'Nickel Back'},
            'NB_weak': {'pos': '△', 'type': 'db', 'label': 'Weak Nickel'},
            'NB_strong': {'pos': '△', 'type': 'db', 'label': 'Strong Nickel'},
        }
        
        for position_key, (row, col) in formation_data['players'].items():
            if position_key in position_types:
                player_data = position_types[position_key]
                players.append({
                    'id': position_key,
                    'pos': player_data['pos'],
                    'x': col,
                    'y': row,
                    'type': player_data['type'],
                    'label': player_data['label']
                })
        
        return {
            'formation_name': formation_name,
            'yards_to_go': yards_to_go,
            'line_of_scrimmage': formation_data['line_of_scrimmage'],
            'first_down_marker': formation_data['first_down_marker'],
            'players': players,
            'field_dimensions': formation_data['field_dimensions']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting formation positions: {str(e)}")

@app.get("/api/coverage-zones/{coverage_name}")
async def get_coverage_zones(coverage_name: str):
    """Get coverage zone definitions for SVG visualization"""
    try:
        # Define coverage zones - you can expand this based on your needs
        coverage_zones = {
            "cover_2_zone": [
                {
                    "id": "deep_left",
                    "path": "M0,0 L200,0 L200,80 Q200,100 180,120 Q120,140 0,120 Z",
                    "color": "#7c3aed",
                    "opacity": 0.2,
                    "label": "Deep Half (FS)"
                },
                {
                    "id": "deep_right", 
                    "path": "M200,0 L400,0 L400,120 Q280,140 220,120 Q200,100 200,80 Z",
                    "color": "#7c3aed",
                    "opacity": 0.2,
                    "label": "Deep Half (SS)"
                },
                {
                    "id": "hook",
                    "path": "M140,120 Q160,140 180,160 Q200,180 220,160 Q240,140 260,120 Q240,100 220,80 Q200,100 180,80 Q160,100 140,120 Z",
                    "color": "#1d4ed8",
                    "opacity": 0.25,
                    "label": "Hook (MLB)"
                }
            ],
            "cover_3_zone": [
                {
                    "id": "deep_left_third",
                    "path": "M0,0 L133,0 L133,100 Q100,120 50,110 Q0,100 0,80 Z",
                    "color": "#7c3aed",
                    "opacity": 0.2,
                    "label": "Deep Third"
                },
                {
                    "id": "deep_middle_third",
                    "path": "M133,0 L267,0 L267,100 Q233,120 200,110 Q167,120 133,100 Z",
                    "color": "#7c3aed",
                    "opacity": 0.2,
                    "label": "Deep Third (FS)"
                },
                {
                    "id": "deep_right_third",
                    "path": "M267,0 L400,0 L400,80 Q400,100 350,110 Q300,120 267,100 Z",
                    "color": "#7c3aed",
                    "opacity": 0.2,
                    "label": "Deep Third"
                }
            ]
        }
        
        zones = coverage_zones.get(coverage_name, [])
        return {
            "coverage_name": coverage_name,
            "zones": zones
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting coverage zones: {str(e)}")

@app.post("/api/defensive-scenario/enhanced")
async def get_enhanced_defensive_scenario():
    """Get defensive scenario with position data and blitz information"""
    try:
        # Get regular scenario
        scenario = defense_engine.get_random_scenario()
        if not scenario:
            raise HTTPException(status_code=500, detail="Could not generate defensive scenario")
        
        # Add minimum yards
        minimum_yards = simulator.generate_minimum_yards()
        
        # Get formation positions using mobile visualizer
        from mobile_field_visualizer import MobileFieldVisualizer
        visualizer = MobileFieldVisualizer(yards_to_go=minimum_yards)
        formation_name = scenario['formation_name']
        
        # Convert formation name to API format (lowercase, replace spaces with hyphens)
        api_formation_name = formation_name.lower().replace(' defense', '').replace(' ', '-')
        
        # Get positions
        formation_data = visualizer.get_formation_data(api_formation_name)
        
        # Add blitz information to players based on the blitz package
        blitz_data = scenario.get('blitz_data', {})
        blitzer = blitz_data.get('blitzer', 'none')
        
        # Map blitzers (you can expand this based on your blitz package data)
        blitzing_positions = []
        if 'linebacker' in blitzer.lower():
            if 'mike' in blitzer.lower() or 'MLB' in blitzer:
                blitzing_positions.append('MLB')
            if 'weak' in blitzer.lower() or 'WLB' in blitzer:
                blitzing_positions.append('WLB')
            if 'strong' in blitzer.lower() or 'SLB' in blitzer:
                blitzing_positions.append('SLB')
        
        return {
            "scenario": scenario,
            "minimum_yards": minimum_yards,
            "yard_range": simulator.determine_yard_range_category(minimum_yards),
            "field_data": {
                "formation_name": formation_name,
                "line_of_scrimmage": formation_data['line_of_scrimmage'],
                "first_down_marker": formation_data['first_down_marker'],
                "players": formation_data['players'],
                "blitzing_positions": blitzing_positions,
                "field_dimensions": formation_data['field_dimensions']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating enhanced scenario: {str(e)}")

@app.get("/api/library/offensive-formations")
async def get_all_offensive_formations():
    """Get list of all offensive formations with basic info for library browser"""
    try:
        formations_list = []
        
        for formation_key, formation_data in offense_engine.formations.items():
            formation_info = {
                "key": formation_key,
                "name": formation_data.get("formation_name", "Unknown Formation"),
                "personnel": formation_data.get("personnel", "Unknown Personnel"),
                "personnel_package": formation_data.get("personnel_package", ""),
                "description": formation_data.get("description", ""),
                "total_passing_plays": len(formation_data.get("passing_plays", {})),
                "total_running_plays": len(formation_data.get("running_plays", {})),
                "total_plays": len(formation_data.get("passing_plays", {})) + len(formation_data.get("running_plays", {}))
            }
            formations_list.append(formation_info)
        
        # Sort by formation name for consistent ordering
        formations_list.sort(key=lambda x: x["name"])
        
        return {
            "formations": formations_list,
            "total_formations": len(formations_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting offensive formations: {str(e)}")

@app.get("/api/library/offensive-formations/{formation_key}")
async def get_offensive_formation_details(formation_key: str):
    """Get detailed information about a specific offensive formation"""
    try:
        if formation_key not in offense_engine.formations:
            raise HTTPException(status_code=404, detail=f"Formation '{formation_key}' not found")
        
        formation_data = offense_engine.formations[formation_key]
        
        # Process passing plays
        passing_plays = []
        for play_key, play_data in formation_data.get("passing_plays", {}).items():
            passing_play = {
                "key": play_key,
                "name": play_data.get("name", "Unknown Play"),
                "concept": play_data.get("concept", ""),
                "routes": play_data.get("routes", {}),
                "protection": play_data.get("protection", ""),
                "target_yards": play_data.get("target_yards", 0),
                "time_to_throw": play_data.get("time_to_throw", ""),
                "best_against": play_data.get("best_against", []),
                "worst_against": play_data.get("worst_against", []),
                "strengths": play_data.get("strengths", []),
                "weaknesses": play_data.get("weaknesses", [])
            }
            passing_plays.append(passing_play)
        
        # Process running plays
        running_plays = []
        for play_key, play_data in formation_data.get("running_plays", {}).items():
            running_play = {
                "key": play_key,
                "name": play_data.get("name", "Unknown Play"),
                "concept": play_data.get("concept", ""),
                "blocking_scheme": play_data.get("blocking_scheme", ""),
                "ball_carrier": play_data.get("ball_carrier", ""),
                "lead_blocker": play_data.get("lead_blocker", ""),
                "target_gap": play_data.get("target_gap", ""),
                "target_yards": play_data.get("target_yards", 0),
                "best_against": play_data.get("best_against", []),
                "worst_against": play_data.get("worst_against", []),
                "strengths": play_data.get("strengths", []),
                "weaknesses": play_data.get("weaknesses", [])
            }
            running_plays.append(running_play)
        
        return {
            "key": formation_key,
            "name": formation_data.get("formation_name", "Unknown Formation"),
            "personnel": formation_data.get("personnel", ""),
            "personnel_package": formation_data.get("personnel_package", ""),
            "description": formation_data.get("description", ""),
            "formation_strengths": formation_data.get("formation_strengths", []),
            "formation_weaknesses": formation_data.get("formation_weaknesses", []),
            "optimal_situations": formation_data.get("optimal_situations", []),
            "passing_plays": passing_plays,
            "running_plays": running_plays,
            "total_plays": len(passing_plays) + len(running_plays)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting formation details: {str(e)}")

@app.get("/api/library/defensive-formations")
async def get_all_defensive_formations():
    """Get list of all defensive formations with basic info for library browser"""
    try:
        formations_list = []
        
        for formation_key, formation_data in defense_engine.formations.items():
            # Count total coverage packages and blitz packages
            total_coverages = len(formation_data.get("coverages", {}))
            total_blitz_packages = 0
            for coverage in formation_data.get("coverages", {}).values():
                total_blitz_packages += len(coverage.get("blitz_packages", {}))
            
            formation_info = {
                "key": formation_key,
                "name": formation_data.get("formation_name", "Unknown Formation"),
                "personnel": formation_data.get("personnel", "Unknown Personnel"),
                "description": formation_data.get("description", ""),
                "total_coverages": total_coverages,
                "total_blitz_packages": total_blitz_packages
            }
            formations_list.append(formation_info)
        
        # Sort by formation name for consistent ordering
        formations_list.sort(key=lambda x: x["name"])
        
        return {
            "formations": formations_list,
            "total_formations": len(formations_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting defensive formations: {str(e)}")

@app.get("/api/library/defensive-formations/{formation_key}")
async def get_defensive_formation_details(formation_key: str):
    """Get detailed information about a specific defensive formation"""
    try:
        if formation_key not in defense_engine.formations:
            raise HTTPException(status_code=404, detail=f"Formation '{formation_key}' not found")
        
        formation_data = defense_engine.formations[formation_key]
        
        # Process coverage packages
        coverages = []
        for coverage_key, coverage_data in formation_data.get("coverages", {}).items():
            # Process blitz packages for this coverage
            blitz_packages = []
            for blitz_key, blitz_data in coverage_data.get("blitz_packages", {}).items():
                blitz_package = {
                    "key": blitz_key,
                    "name": blitz_data.get("name", "Unknown Blitz"),
                    "blitzer": blitz_data.get("blitzer", ""),
                    "rushers": blitz_data.get("rushers", 4),
                    "coverage_adjustment": blitz_data.get("coverage_adjustment", ""),
                    "run_strengths": blitz_data.get("run_strengths", []),
                    "run_weaknesses": blitz_data.get("run_weaknesses", []),
                    "pass_strengths": blitz_data.get("pass_strengths", []),
                    "pass_weaknesses": blitz_data.get("pass_weaknesses", []),
                    "best_against": blitz_data.get("best_against", [])
                }
                blitz_packages.append(blitz_package)
            
            coverage = {
                "key": coverage_key,
                "name": coverage_data.get("name", "Unknown Coverage"),
                "coverage_type": coverage_data.get("coverage_type", ""),
                "description": coverage_data.get("description", ""),
                "base_strengths": coverage_data.get("base_strengths", []),
                "base_weaknesses": coverage_data.get("base_weaknesses", []),
                "optimal_situations": coverage_data.get("optimal_situations", []),
                "vulnerable_to": coverage_data.get("vulnerable_to", []),
                "blitz_packages": blitz_packages
            }
            coverages.append(coverage)
        
        return {
            "key": formation_key,
            "name": formation_data.get("formation_name", "Unknown Formation"),
            "personnel": formation_data.get("personnel", ""),
            "description": formation_data.get("description", ""),
            "base_strengths": formation_data.get("base_strengths", []),
            "base_weaknesses": formation_data.get("base_weaknesses", []),
            "optimal_situations": formation_data.get("optimal_situations", []),
            "coverages": coverages,
            "total_coverages": len(coverages)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting defensive formation details: {str(e)}")

@app.get("/api/library/search")
async def search_formations_and_plays(
    query: str, 
    formation_type: Optional[str] = None,  # "offensive" or "defensive" 
    category: Optional[str] = None  # "formation", "play", "coverage", etc.
):
    """Search across all formations, plays, and coverage packages"""
    try:
        results = {
            "query": query,
            "offensive_formations": [],
            "defensive_formations": [],
            "offensive_plays": [],
            "coverage_packages": []
        }
        
        query_lower = query.lower()
        
        # Search offensive formations if not restricted to defensive only
        if formation_type != "defensive":
            for formation_key, formation_data in offense_engine.formations.items():
                formation_name = formation_data.get("formation_name", "").lower()
                description = formation_data.get("description", "").lower()
                
                if query_lower in formation_name or query_lower in description:
                    results["offensive_formations"].append({
                        "key": formation_key,
                        "name": formation_data.get("formation_name", ""),
                        "description": formation_data.get("description", ""),
                        "match_type": "formation"
                    })
                
                # Search plays within this formation
                for play_key, play_data in formation_data.get("passing_plays", {}).items():
                    play_name = play_data.get("name", "").lower()
                    concept = play_data.get("concept", "").lower()
                    
                    if query_lower in play_name or query_lower in concept:
                        results["offensive_plays"].append({
                            "key": play_key,
                            "name": play_data.get("name", ""),
                            "concept": play_data.get("concept", ""),
                            "formation_key": formation_key,
                            "formation_name": formation_data.get("formation_name", ""),
                            "type": "passing",
                            "match_type": "play"
                        })
                
                for play_key, play_data in formation_data.get("running_plays", {}).items():
                    play_name = play_data.get("name", "").lower()
                    concept = play_data.get("concept", "").lower()
                    
                    if query_lower in play_name or query_lower in concept:
                        results["offensive_plays"].append({
                            "key": play_key,
                            "name": play_data.get("name", ""),
                            "concept": play_data.get("concept", ""),
                            "formation_key": formation_key,
                            "formation_name": formation_data.get("formation_name", ""),
                            "type": "running",
                            "match_type": "play"
                        })
        
        # Search defensive formations if not restricted to offensive only
        if formation_type != "offensive":
            for formation_key, formation_data in defense_engine.formations.items():
                formation_name = formation_data.get("formation_name", "").lower()
                description = formation_data.get("description", "").lower()
                
                if query_lower in formation_name or query_lower in description:
                    results["defensive_formations"].append({
                        "key": formation_key,
                        "name": formation_data.get("formation_name", ""),
                        "description": formation_data.get("description", ""),
                        "match_type": "formation"
                    })
                
                # Search coverage packages
                for coverage_key, coverage_data in formation_data.get("coverages", {}).items():
                    coverage_name = coverage_data.get("name", "").lower()
                    description = coverage_data.get("description", "").lower()
                    
                    if query_lower in coverage_name or query_lower in description:
                        results["coverage_packages"].append({
                            "key": coverage_key,
                            "name": coverage_data.get("name", ""),
                            "description": coverage_data.get("description", ""),
                            "formation_key": formation_key,
                            "formation_name": formation_data.get("formation_name", ""),
                            "match_type": "coverage"
                        })
        
        # Calculate total results
        total_results = (
            len(results["offensive_formations"]) + 
            len(results["defensive_formations"]) + 
            len(results["offensive_plays"]) + 
            len(results["coverage_packages"])
        )
        
        results["total_results"] = total_results
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching formations: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("🏈 Starting QB Pre-Snap Simulator API...")
    print("📱 This will serve data to your React Native mobile app")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Allow connections from mobile app
        port=8000,
        reload=True  # Auto-reload when code changes
    )