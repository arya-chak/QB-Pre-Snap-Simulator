"""
Updated Field Visualizer with Dynamic Line of Scrimmage
Author: Arya Chakraborty

Creates visual X's and O's representations of defensive formations using ASCII/text graphics.
Shows base defensive alignments with dynamic line of scrimmage based on field position.
"""

import streamlit as st

class FieldVisualizer:
    def __init__(self, yards_to_go=10):
        """Initialize the field visualizer with yards to go"""
        self.field_width = 53  # Standard field width in characters
        self.field_height = 20  # Visible field depth
        
        # Calculate line of scrimmage position based on field situation
        self.yards_to_go = yards_to_go
        self.line_of_scrimmage = 10  # Base position for display
        
        # Calculate where the first down marker should be
        self.first_down_marker = max(0, min(self.field_height - 1, 
                                          self.line_of_scrimmage - yards_to_go))
        
        # Defensive position symbols
        self.symbols = {
            # Defensive Line
            'DE': 'E',      # Defensive End
            'DT': 'T',      # Defensive Tackle  
            'NT': 'N',      # Nose Tackle
            
            # Linebackers
            'OLB': 'B',     # Outside Linebacker
            'ILB': 'M',     # Inside Linebacker
            'MLB': 'M',     # Middle Linebacker
            'WLB': 'W',     # Weak Linebacker
            'SLB': 'S',     # Strong Linebacker
            
            # Defensive Backs
            'CB': 'C',      # Cornerback
            'FS': 'F',      # Free Safety
            'SS': 'S',      # Strong Safety
            'NB': '△',      # Nickel Back
            'DB': '◯',      # Dime Back
            
            # Special
            'SPY': '●',     # Spy linebacker
            'ROVER': 'R'    # Rover
        }
    
    def update_yards_to_go(self, yards_to_go):
        """Update the yards to go and recalculate first down marker"""
        self.yards_to_go = yards_to_go
        # Recalculate first down marker
        self.first_down_marker = max(0, min(self.field_height - 1, 
                                          self.line_of_scrimmage - self.yards_to_go))
    
    def create_empty_field(self):
        """Create an empty field grid with dynamic markers"""
        field = []
        for row in range(self.field_height):
            field.append([' '] * self.field_width)
        
        # Add line of scrimmage
        for col in range(self.field_width):
            if col % 5 == 0:
                field[self.line_of_scrimmage][col] = '|'
            else:
                field[self.line_of_scrimmage][col] = '-'
        
        # Add first down marker (if different from LOS)
        if self.first_down_marker != self.line_of_scrimmage and self.first_down_marker >= 0:
            for col in range(self.field_width):
                if col % 5 == 0:
                    field[self.first_down_marker][col] = '╫'  # Different symbol for first down
                else:
                    field[self.first_down_marker][col] = '═'
        
        # Add hash marks
        left_hash = 16
        right_hash = 36
        for row in range(self.field_height):
            if row != self.line_of_scrimmage and row != self.first_down_marker:
                field[row][left_hash] = '.'
                field[row][right_hash] = '.'
        
        return field
    
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
            # Defensive Line (on LOS)
            'DE_weak': (self.line_of_scrimmage, 20),      # Weak DE
            'DT_weak': (self.line_of_scrimmage, 23),      # Weak DT
            'DT_strong': (self.line_of_scrimmage, 29),    # Strong DT
            'DE_strong': (self.line_of_scrimmage, 32),    # Strong DE
            
            # Linebackers (2-3 yards back)
            'WLB': (self.line_of_scrimmage - 3, 18),      # Weak LB
            'MLB': (self.line_of_scrimmage - 3, 26),      # Middle LB
            'SLB': (self.line_of_scrimmage - 3, 34),      # Strong LB
            
            # Secondary (5-7 yards back)
            'CB_weak': (self.line_of_scrimmage - 6, 12),  # Weak CB
            'FS': (self.line_of_scrimmage - 8, 26),       # Free Safety
            'SS': (self.line_of_scrimmage - 6, 36),       # Strong Safety
            'CB_strong': (self.line_of_scrimmage - 6, 40) # Strong CB
        }
    
    def _get_3_4_alignment(self):
        """3-4 Defense base alignment"""
        return {
            # Defensive Line (fewer down linemen)
            'DE_weak': (self.line_of_scrimmage, 21),      # Weak DE
            'NT': (self.line_of_scrimmage, 26),           # Nose Tackle
            'DE_strong': (self.line_of_scrimmage, 31),    # Strong DE
            
            # Linebackers (more linebackers)
            'OLB_weak': (self.line_of_scrimmage - 2, 17), # Weak OLB
            'ILB_weak': (self.line_of_scrimmage - 3, 23), # Weak ILB
            'ILB_strong': (self.line_of_scrimmage - 3, 29), # Strong ILB
            'OLB_strong': (self.line_of_scrimmage - 2, 35), # Strong OLB
            
            # Secondary
            'CB_weak': (self.line_of_scrimmage - 6, 12),  # Weak CB
            'FS': (self.line_of_scrimmage - 8, 26),       # Free Safety
            'SS': (self.line_of_scrimmage - 6, 36),       # Strong Safety
            'CB_strong': (self.line_of_scrimmage - 6, 40) # Strong CB
        }
    
    def _get_5_2_alignment(self):
        """5-2 Defense base alignment"""
        return {
            # Defensive Line (5 down linemen)
            'DE_weak': (self.line_of_scrimmage, 19),      # Weak DE
            'DT_weak': (self.line_of_scrimmage, 22),      # Weak DT
            'NT': (self.line_of_scrimmage, 26),           # Nose Tackle
            'DT_strong': (self.line_of_scrimmage, 30),    # Strong DT
            'DE_strong': (self.line_of_scrimmage, 33),    # Strong DE
            
            # Linebackers (only 2)
            'MLB_weak': (self.line_of_scrimmage - 3, 23), # Weak MLB
            'MLB_strong': (self.line_of_scrimmage - 3, 29), # Strong MLB
            
            # Secondary
            'CB_weak': (self.line_of_scrimmage - 6, 12),  # Weak CB
            'FS': (self.line_of_scrimmage - 8, 26),       # Free Safety
            'SS': (self.line_of_scrimmage - 6, 36),       # Strong Safety
            'CB_strong': (self.line_of_scrimmage - 6, 40) # Strong CB
        }
    
    def _get_4_4_alignment(self):
        """4-4 Defense base alignment"""
        return {
            # Defensive Line
            'DE_weak': (self.line_of_scrimmage, 20),      # Weak DE
            'DT_weak': (self.line_of_scrimmage, 24),      # Weak DT
            'DT_strong': (self.line_of_scrimmage, 28),    # Strong DT
            'DE_strong': (self.line_of_scrimmage, 32),    # Strong DE
            
            # Linebackers (4 linebackers)
            'OLB_weak': (self.line_of_scrimmage - 2, 17), # Weak OLB
            'ILB_weak': (self.line_of_scrimmage - 3, 23), # Weak ILB
            'ILB_strong': (self.line_of_scrimmage - 3, 29), # Strong ILB
            'OLB_strong': (self.line_of_scrimmage - 2, 35), # Strong OLB
            
            # Secondary (only 3 DBs)
            'CB_weak': (self.line_of_scrimmage - 6, 12),  # Weak CB
            'FS': (self.line_of_scrimmage - 8, 26),       # Free Safety
            'CB_strong': (self.line_of_scrimmage - 6, 40) # Strong CB
        }
    
    def _get_46_alignment(self):
        """46 Defense base alignment"""
        return {
            # Defensive Line
            'DE_weak': (self.line_of_scrimmage, 19),      # Weak DE
            'DT_weak': (self.line_of_scrimmage, 23),      # Weak DT
            'DT_strong': (self.line_of_scrimmage, 29),    # Strong DT
            'DE_strong': (self.line_of_scrimmage, 33),    # Strong DE
            
            # Linebackers (6 linebackers!)
            'OLB_weak': (self.line_of_scrimmage - 1, 16), # Weak OLB
            'ILB_weak': (self.line_of_scrimmage - 2, 21), # Weak ILB
            'MLB': (self.line_of_scrimmage - 3, 26),      # Middle LB
            'ILB_strong': (self.line_of_scrimmage - 2, 31), # Strong ILB
            'OLB_strong': (self.line_of_scrimmage - 1, 36), # Strong OLB
            'ROVER': (self.line_of_scrimmage - 2, 38),    # Rover LB
            
            # Secondary (only 1 safety!)
            'CB_weak': (self.line_of_scrimmage - 6, 12),  # Weak CB
            'FS': (self.line_of_scrimmage - 8, 26),       # Free Safety
            'CB_strong': (self.line_of_scrimmage - 6, 40) # Strong CB
        }
    
    def _get_nickel_alignment(self):
        """Nickel Defense base alignment"""
        return {
            # Defensive Line
            'DE_weak': (self.line_of_scrimmage, 20),      # Weak DE
            'DT_weak': (self.line_of_scrimmage, 24),      # Weak DT
            'DT_strong': (self.line_of_scrimmage, 28),    # Strong DT
            'DE_strong': (self.line_of_scrimmage, 32),    # Strong DE
            
            # Linebackers (only 2)
            'MLB_weak': (self.line_of_scrimmage - 3, 23), # Weak MLB
            'MLB_strong': (self.line_of_scrimmage - 3, 29), # Strong MLB
            
            # Secondary (5 DBs)
            'CB_weak': (self.line_of_scrimmage - 6, 10),  # Weak CB
            'NB': (self.line_of_scrimmage - 4, 20),       # Nickel Back
            'FS': (self.line_of_scrimmage - 8, 26),       # Free Safety
            'SS': (self.line_of_scrimmage - 6, 35),       # Strong Safety
            'CB_strong': (self.line_of_scrimmage - 6, 42) # Strong CB
        }
    
    def _get_dime_alignment(self):
        """Dime Defense base alignment"""
        return {
            # Defensive Line
            'DE_weak': (self.line_of_scrimmage, 21),      # Weak DE
            'DT_weak': (self.line_of_scrimmage, 25),      # Weak DT
            'DT_strong': (self.line_of_scrimmage, 27),    # Strong DT
            'DE_strong': (self.line_of_scrimmage, 31),    # Strong DE
            
            # Linebackers (only 1!)
            'MLB': (self.line_of_scrimmage - 3, 26),      # Middle LB
            
            # Secondary (6 DBs)
            'CB_weak': (self.line_of_scrimmage - 6, 8),   # Weak CB
            'NB_weak': (self.line_of_scrimmage - 4, 18),  # Weak Nickel
            'NB_strong': (self.line_of_scrimmage - 4, 34), # Strong Nickel
            'CB_strong': (self.line_of_scrimmage - 6, 44), # Strong CB
            'FS': (self.line_of_scrimmage - 8, 22),       # Free Safety
            'SS': (self.line_of_scrimmage - 8, 30)        # Strong Safety
        }
    
    def place_defenders(self, field, alignment):
        """Place defensive players on the field"""
        position_types = {
            # Defensive Line
            'DE_weak': 'E', 'DE_strong': 'E',
            'DT_weak': 'T', 'DT_strong': 'T',
            'NT': 'N',
            
            # Linebackers
            'WLB': 'W', 'MLB': 'M', 'SLB': 'S',
            'OLB_weak': 'B', 'OLB_strong': 'B',
            'ILB_weak': 'M', 'ILB_strong': 'M',
            'MLB_weak': 'M', 'MLB_strong': 'M',
            'ROVER': 'R',
            
            # Secondary
            'CB_weak': 'C', 'CB_strong': 'C',
            'FS': 'F', 'SS': 'S',
            'NB': '△', 'NB_weak': '△', 'NB_strong': '△'
        }
        
        for position, (row, col) in alignment.items():
            if 0 <= row < self.field_height and 0 <= col < self.field_width:
                symbol = position_types.get(position, '?')
                field[row][col] = symbol
        
        return field
    
    def render_field(self, field, formation_name, coverage_name="Base Coverage", show_labels=True):
        """Render the field as text with optional labels and yards to go info"""
        if show_labels:
            field_text = f"**{formation_name} - {coverage_name}**\n"
            field_text += f"*{self.yards_to_go} yards to go*\n\n"
        else:
            field_text = f"**Defensive Formation**\n"
            field_text += f"*{self.yards_to_go} yards to go*\n\n"
        field_text += "```\n"
        
        # Add yard markers
        field_text += "    "
        for col in range(0, self.field_width, 10):
            field_text += f"{col:2d}        "
        field_text += "\n"
        
        # Render field rows
        for row_idx, row in enumerate(field):
            field_text += f"{row_idx:2d}  "
            field_text += "".join(row)
            
            # Add row labels
            if row_idx == self.line_of_scrimmage:
                field_text += "  ← Line of Scrimmage"
            elif row_idx == self.first_down_marker and self.first_down_marker != self.line_of_scrimmage:
                field_text += f"  ← First Down ({self.yards_to_go} yards)"
            elif row_idx == self.line_of_scrimmage - 8:
                field_text += "  ← Deep Secondary"
            elif row_idx == self.line_of_scrimmage - 3:
                field_text += "  ← Linebackers"
            
            field_text += "\n"
        
        field_text += "```\n"
        return field_text
    
    def get_legend(self, formation_name):
        """Get legend for defensive positions"""
        legends = {
            "4-3": {
                "Defensive Line": "E = DE, T = DT",
                "Linebackers": "W = WLB, M = MLB, S = SLB", 
                "Secondary": "C = CB, F = FS, S = SS"
            },
            "3-4": {
                "Defensive Line": "E = DE, N = NT",
                "Linebackers": "B = OLB, M = ILB",
                "Secondary": "C = CB, F = FS, S = SS"
            },
            "5-2": {
                "Defensive Line": "E = DE, T = DT, N = NT",
                "Linebackers": "M = MLB",
                "Secondary": "C = CB, F = FS, S = SS"
            },
            "4-4": {
                "Defensive Line": "E = DE, T = DT",
                "Linebackers": "B = OLB, M = ILB",
                "Secondary": "C = CB, F = FS"
            },
            "46": {
                "Defensive Line": "E = DE, T = DT",
                "Linebackers": "B = OLB, M = MLB, R = Rover",
                "Secondary": "C = CB, F = FS"
            },
            "nickel": {
                "Defensive Line": "E = DE, T = DT",
                "Linebackers": "M = MLB",
                "Secondary": "C = CB, △ = Nickel, F = FS, S = SS"
            },
            "dime": {
                "Defensive Line": "E = DE, T = DT",
                "Linebackers": "M = MLB",
                "Secondary": "C = CB, △ = Nickel, F = FS, S = SS"
            }
        }
        
        return legends.get(formation_name, legends["4-3"])
    
    def display_defensive_formation(self, formation_name, coverage_name="Base Coverage", show_labels=True):
        """Main function to display a defensive formation with optional labels"""
        # Create empty field
        field = self.create_empty_field()
        
        # Get alignment for this formation
        alignment = self.get_defensive_alignment(formation_name, coverage_name)
        
        # Place defenders
        field = self.place_defenders(field, alignment)
        
        # Render field with optional labels
        field_display = self.render_field(field, formation_name.replace('-', ' ').title(), coverage_name, show_labels)
        
        # Get legend
        legend = self.get_legend(formation_name)
        
        return field_display, legend

def main():
    """Test the field visualizer with dynamic yards to go"""
    st.set_page_config(page_title="Dynamic Field Visualizer Test", layout="wide")
    
    st.title("🏈 Dynamic Defensive Formation Visualizer")
    
    # Yards to go control
    yards_to_go = st.slider("Yards to Go", 1, 20, 10)
    
    # Create visualizer with dynamic yards to go
    visualizer = FieldVisualizer(yards_to_go=yards_to_go)
    
    # Formation selection
    formations = ["4-3", "3-4", "5-2", "4-4", "46", "nickel", "dime"]
    selected_formation = st.selectbox("Select Formation:", formations)
    
    # Display formation
    field_display, legend = visualizer.display_defensive_formation(selected_formation)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(field_display)
    
    with col2:
        st.markdown("**Legend:**")
        for category, symbols in legend.items():
            st.write(f"**{category}:** {symbols}")
        
        st.markdown("**Field Markers:**")
        st.write("**─** = Line of Scrimmage")
        st.write("**═** = First Down Marker")
        st.write("**|** = 5-yard markers")
        st.write("**.** = Hash marks")

if __name__ == "__main__":
    main()