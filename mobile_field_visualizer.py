"""
Mobile Field Visualizer - Streamlit-free version for API usage
Author: Arya Chakraborty

Creates positional data for defensive formations without any Streamlit dependencies.
This version is optimized for mobile API consumption.
"""

class MobileFieldVisualizer:
    def __init__(self, yards_to_go=10):
        """Initialize the field visualizer with yards to go"""
        self.field_width = 35
        self.field_height = 15
        self.yards_to_go = yards_to_go
        self.line_of_scrimmage = 8
        self.first_down_marker = max(0, min(self.field_height - 1, 
                                          self.line_of_scrimmage - yards_to_go))
    
    def update_yards_to_go(self, yards_to_go):
        """Update the yards to go and recalculate first down marker"""
        self.yards_to_go = yards_to_go
        self.first_down_marker = max(0, min(self.field_height - 1, 
                                          self.line_of_scrimmage - yards_to_go))
    
    def get_defensive_alignment(self, formation_name, coverage_name="base"):
        """Get base defensive alignment for a formation"""
        alignments = {
            "4-3": self._get_4_3_alignment(),
            "3-4": self._get_3_4_alignment(), 
            "5-2": self._get_5_2_alignment(),
            "4-4": self._get_4_4_alignment(),
            "46": self._get_46_alignment(),
            "nickel": self._get_nickel_alignment(),
            "dime": self._get_dime_alignment()
        }
        return alignments.get(formation_name, self._get_4_3_alignment())
    
    def _get_4_3_alignment(self):
        """4-3 Defense base alignment"""
        return {
            'DE_weak': (self.line_of_scrimmage, 13),
            'DT_weak': (self.line_of_scrimmage, 15),
            'DT_strong': (self.line_of_scrimmage, 19),
            'DE_strong': (self.line_of_scrimmage, 21),
            'WLB': (self.line_of_scrimmage - 3, 12),
            'MLB': (self.line_of_scrimmage - 3, 17),
            'SLB': (self.line_of_scrimmage - 3, 22),
            'CB_weak': (self.line_of_scrimmage - 6, 8),
            'FS': (self.line_of_scrimmage - 8, 17),
            'SS': (self.line_of_scrimmage - 6, 24),
            'CB_strong': (self.line_of_scrimmage - 6, 26)
        }
    
    def _get_3_4_alignment(self):
        """3-4 Defense base alignment"""
        return {
            'DE_weak': (self.line_of_scrimmage, 14),
            'NT': (self.line_of_scrimmage, 17),
            'DE_strong': (self.line_of_scrimmage, 20),
            'OLB_weak': (self.line_of_scrimmage - 2, 11),
            'ILB_weak': (self.line_of_scrimmage - 3, 15),
            'ILB_strong': (self.line_of_scrimmage - 3, 19),
            'OLB_strong': (self.line_of_scrimmage - 2, 23),
            'CB_weak': (self.line_of_scrimmage - 6, 8),
            'FS': (self.line_of_scrimmage - 8, 17),
            'SS': (self.line_of_scrimmage - 6, 24),
            'CB_strong': (self.line_of_scrimmage - 6, 26)
        }
    
    def _get_5_2_alignment(self):
        """5-2 Defense base alignment"""
        return {
            'DE_weak': (self.line_of_scrimmage, 12),
            'DT_weak': (self.line_of_scrimmage, 14),
            'NT': (self.line_of_scrimmage, 17),
            'DT_strong': (self.line_of_scrimmage, 20),
            'DE_strong': (self.line_of_scrimmage, 22),
            'MLB_weak': (self.line_of_scrimmage - 3, 15),
            'MLB_strong': (self.line_of_scrimmage - 3, 19),
            'CB_weak': (self.line_of_scrimmage - 6, 8),
            'FS': (self.line_of_scrimmage - 8, 17),
            'SS': (self.line_of_scrimmage - 6, 24),
            'CB_strong': (self.line_of_scrimmage - 6, 26)
        }
    
    def _get_4_4_alignment(self):
        """4-4 Defense base alignment"""
        return {
            'DE_weak': (self.line_of_scrimmage, 13),
            'DT_weak': (self.line_of_scrimmage, 15),
            'DT_strong': (self.line_of_scrimmage, 19),
            'DE_strong': (self.line_of_scrimmage, 21),
            'OLB_weak': (self.line_of_scrimmage - 2, 11),
            'ILB_weak': (self.line_of_scrimmage - 3, 15),
            'ILB_strong': (self.line_of_scrimmage - 3, 19),
            'OLB_strong': (self.line_of_scrimmage - 2, 23),
            'CB_weak': (self.line_of_scrimmage - 6, 8),
            'FS': (self.line_of_scrimmage - 8, 17),
            'CB_strong': (self.line_of_scrimmage - 6, 26)
        }
    
    def _get_46_alignment(self):
        """46 Defense base alignment - 4 DL, 6 LB, 1 DB"""
        return {
            # Defensive Line (4 players)
            'DE_weak': (self.line_of_scrimmage, 12),       # Weak DE
            'DT_weak': (self.line_of_scrimmage, 15),       # Weak DT  
            'DT_strong': (self.line_of_scrimmage, 19),     # Strong DT
            'DE_strong': (self.line_of_scrimmage, 22),     # Strong DE
        
            # Linebackers (6 players) 
            'OLB_weak': (self.line_of_scrimmage - 1, 10),  # Weak OLB
            'ILB_weak': (self.line_of_scrimmage - 2, 13),  # Weak ILB
            'MLB': (self.line_of_scrimmage - 3, 17),       # Middle LB
            'ILB_strong': (self.line_of_scrimmage - 2, 21), # Strong ILB
            'OLB_strong': (self.line_of_scrimmage - 1, 24), # Strong OLB
            'ROVER': (self.line_of_scrimmage - 2, 26),     # Rover LB
        
            # Secondary (1 player only!)
            'FS': (self.line_of_scrimmage - 8, 17),        # Free Safety (ONLY DB)
            # Removed CB_weak and CB_strong - 46 Defense has NO cornerbacks!
    }
    
    def _get_nickel_alignment(self):
        """Nickel Defense base alignment"""
        return {
            'DE_weak': (self.line_of_scrimmage, 13),
            'DT_weak': (self.line_of_scrimmage, 15),
            'DT_strong': (self.line_of_scrimmage, 19),
            'DE_strong': (self.line_of_scrimmage, 21),
            'MLB_weak': (self.line_of_scrimmage - 3, 15),
            'MLB_strong': (self.line_of_scrimmage - 3, 19),
            'CB_weak': (self.line_of_scrimmage - 6, 7),
            'NB': (self.line_of_scrimmage - 4, 13),
            'FS': (self.line_of_scrimmage - 8, 17),
            'SS': (self.line_of_scrimmage - 6, 23),
            'CB_strong': (self.line_of_scrimmage - 6, 27)
        }
    
    def _get_dime_alignment(self):
        """Dime Defense base alignment"""
        return {
            'DE_weak': (self.line_of_scrimmage, 14),
            'DT_weak': (self.line_of_scrimmage, 16),
            'DT_strong': (self.line_of_scrimmage, 18),
            'DE_strong': (self.line_of_scrimmage, 20),
            'MLB': (self.line_of_scrimmage - 3, 17),
            'CB_weak': (self.line_of_scrimmage - 6, 6),
            'NB_weak': (self.line_of_scrimmage - 4, 12),
            'NB_strong': (self.line_of_scrimmage - 4, 22),
            'CB_strong': (self.line_of_scrimmage - 6, 28),
            'FS': (self.line_of_scrimmage - 8, 15),
            'SS': (self.line_of_scrimmage - 8, 19)
        }
    
    def get_formation_data(self, formation_name, coverage_name="base"):
        """Get all formation data for mobile API"""
        alignment = self.get_defensive_alignment(formation_name, coverage_name)
        
        return {
            'formation_name': formation_name,
            'yards_to_go': self.yards_to_go,
            'line_of_scrimmage': self.line_of_scrimmage,
            'first_down_marker': self.first_down_marker,
            'players': alignment,
            'field_dimensions': {
                'width': self.field_width,
                'height': self.field_height
            }
        }