import json
import os

def grid_to_pixels(grid_str, char_map, width=32, height=32):
    lines = [line for line in grid_str.strip().split('\n') if line]
    
    # Pad or trim to fit height
    if len(lines) > height:
        lines = lines[:height]
    
    # Center vertically if smaller
    top_pad = (height - len(lines)) // 2
    
    pixel_rows = []
    
    # Add top padding
    for _ in range(top_pad):
        pixel_rows.append(["bg"] * width)
        
    for line in lines:
        row = []
        # Pad line to match width logic if needed, but we assume fixed width in string or pad with bg
        # Let's map char by char
        # Center horizontally
        content_len = len(line)
        left_pad = (width - content_len) // 2
        
        row_keys = ["bg"] * left_pad
        
        for char in line:
            if char in char_map:
                row_keys.append(char_map[char])
            else:
                row_keys.append("bg")
                
        # Fill remaining right
        while len(row_keys) < width:
            row_keys.append("bg")
            
        pixel_rows.append(row_keys[:width])
        
    # Add bottom padding
    while len(pixel_rows) < height:
        pixel_rows.append(["bg"] * width)
        
    return pixel_rows

def save_pet(filename, data):
    path = os.path.join("assets", "pets", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Generated {path}")

# ==========================================
# DOG DESIGN (Shiba Inu Style)
# ==========================================
dog_palette = {
    "bg": [0, 0, 0, 0],
    "fur": [210, 105, 30, 255],      # Chocolate/Orange
    "light": [245, 222, 179, 255],   # Wheat/Cream
    "dark": [139, 69, 19, 255],      # SaddleBrown
    "eye": [0, 0, 0, 255],
    "nose": [50, 50, 50, 255],
    "pink": [255, 182, 193, 255],    # Tongue/Ear
    "collar": [220, 20, 60, 255]     # Crimson
}

dog_map = {
    " ": "bg",
    "F": "fur",
    "L": "light",
    "D": "dark",
    ".": "eye",
    "^": "nose",
    "p": "pink",
    "c": "collar"
}

# Shiba Idle 1
dog_idle1 = """
        DD      DD
       DFFD    DFFD
      DFFFFD  DFFFFD
      DFFFFFFFFFFFFD
     DFFFFFFFFFFFFFFD
     DFFFFFFFFFFFFFFD
    DFFFFL..FF..LFFFFD
    DFFFFL..FF..LFFFFD
    DFFFFLLLLLLLLFFFFD
    DFFFFLL^LL^LLFFFFD
     DFFFFLLppLLFFFFD
     DFFFFFLLLLFFFFFD
      DFFFFFFFFFFFFD
      DccccccccccD
     DFFFFFFFFFFFFD
    DFFFFFFFFFFFFFFD
    DFFFFFFFFFFFFFFD
    DFFFFLLLLLLFFFFD
   DFFFFFLLLLLLFFFFFD
   DFFFFFLLLLLLFFFFFD
   DFFFFFLLLLLLFFFFFD
    DDDDLLLLLLLLDDDD
       DDDD  DDDD
"""

# Shiba Idle 2 (Ear twitch + Tail wag/Tongue)
dog_idle2 = """
        DD      DD
       DFFD    DFFD
      DFFFFD  DFFFFD
      DFFFFFFFFFFFFD
     DFFFFFFFFFFFFFFD
     DFFFFFFFFFFFFFFD
    DFFFFL..FF..LFFFFD
    DFFFFL..FF..LFFFFD
    DFFFFLLLLLLLLFFFFD
    DFFFFLL^LL^LLFFFFD
     DFFFFLLppLLFFFFD
     DFFFFFLLppFFFFFD
      DFFFFFppFFFFFD
      DccccccccccD
     DFFFFFFFFFFFFD
    DFFFFFFFFFFFFFFD
    DFFFFFFFFFFFFFFD
    DFFFFLLLLLLFFFFD
   DFFFFFLLLLLLFFFFFD
   DFFFFFLLLLLLFFFFFD
   DFFFFFLLLLLLFFFFFD
    DDDDLLLLLLLLDDDD
       DDDD  DDDD
"""

# ==========================================
# CAT DESIGN (Grey Tabby)
# ==========================================
cat_palette = {
    "bg": [0, 0, 0, 0],
    "fur": [119, 136, 153, 255],     # LightSlateGray
    "dark": [47, 79, 79, 255],       # DarkSlateGray
    "white": [240, 248, 255, 255],   # AliceBlue
    "eye": [50, 205, 50, 255],       # LimeGreen
    "nose": [255, 192, 203, 255],    # Pink
    "ear": [255, 182, 193, 255]      # LightPink
}

cat_map = {
    " ": "bg",
    "F": "fur",
    "D": "dark",
    "W": "white",
    ".": "eye",
    "^": "nose",
    "i": "ear"
}

# Cat Idle 1
cat_idle1 = """
       D        D
      DFD      DFD
     DFiFD    DFiFD
    DFFiFFDDDDFFiFFD
    DFFFFFFFFFFFFFFD
    DFFFFFFFFFFFFFFD
    DFFD........DFFD
    DFFD........DFFD
    DFFD..DDDD..DFFD
     DFFFFFFFFFFFFD
     DFFFF^FF^FFFFD
      DFFFFWWFFFFD
      DFFFFWWFFFFD
     DFFFFWWWWFFFFD
    DFFFFFWWWWFFFFFD
    DFFFFFWWWWFFFFFD
    DFFFFFWWWWFFFFFD
   DFFFFFFWWWWFFFFFFD
   DFFFFFFWWWWFFFFFFD
    DDDDDDWWWWDDDDDD
         DD  DD
"""

# Cat Idle 2 (Blink + Tail)
cat_idle2 = """
       D        D
      DFD      DFD
     DFiFD    DFiFD
    DFFiFFDDDDFFiFFD
    DFFFFFFFFFFFFFFD
    DFFFFFFFFFFFFFFD
    DFFD........DFFD
    DFFDDDDDDDDDDFFD
    DFFD..DDDD..DFFD
     DFFFFFFFFFFFFD
     DFFFF^FF^FFFFD
      DFFFFWWFFFFD
      DFFFFWWFFFFD
     DFFFFWWWWFFFFD
    DFFFFFWWWWFFFFFD
    DFFFFFWWWWFFFFFD
    DFFFFFWWWWFFFFFD D
   DFFFFFFWWWWFFFFFFDD
   DFFFFFFWWWWFFFFFFD
    DDDDDDWWWWDDDDDD
         DD  DD
"""

# ==========================================
# RABBIT DESIGN (White Bunny)
# ==========================================
rabbit_palette = {
    "bg": [0, 0, 0, 0],
    "fur": [255, 255, 255, 255],
    "shadow": [220, 220, 220, 255],
    "ear": [255, 192, 203, 255],     # Pink
    "eye": [0, 0, 0, 255],
    "nose": [255, 105, 180, 255],    # HotPink
    "carrot": [255, 140, 0, 255],    # DarkOrange
    "green": [34, 139, 34, 255]      # ForestGreen
}

rabbit_map = {
    " ": "bg",
    "F": "fur",
    "S": "shadow",
    "i": "ear",
    ".": "eye",
    "^": "nose",
    "C": "carrot",
    "g": "green"
}

# Rabbit Idle 1
rabbit_idle1 = """
       SS      SS
      SiiS    SiiS
      SiiS    SiiS
      SiiS    SiiS
      SiiS    SiiS
      SFiiS  SFiiS
      SFFFFSSFFFFS
     SFFFFFFFFFFFFS
     SFFFFFFFFFFFFS
     SFFFF.FF.FFFFS
     SFFFF.FF.FFFFS
      SFFFF^^FFFFS
      SFFFFFFFFFFS
     SFFFFFFFFFFFFS
    SFFFFFFFFFFFFFFS
    SFFFFFFFFFFFFFFS
   SFFFFFFFFFFFFFFFFS
   SFFFFFFFFFFFFFFFFS
   SFFFFFFFFFFFFFFFFS
    SFFFFS    SFFFFS
    SSSSSS    SSSSSS
"""

# Rabbit Idle 2 (Ear flop)
rabbit_idle2 = """
       SS
      SiiS
      SiiS     SS
      SiiS    SiiS
      SiiS    SiiS
      SFiiS   SiiS
      SFFFFSSSFiiS
     SFFFFFFFFFFFFS
     SFFFFFFFFFFFFS
     SFFFF.FF.FFFFS
     SFFFF.FF.FFFFS
      SFFFF^^FFFFS
      SFFFFFFFFFFS
     SFFFFFFFFFFFFS
    SFFFFFFFFFFFFFFS
    SFFFFFFFFFFFFFFS
   SFFFFFFFFFFFFFFFFS
   SFFFFFFFFFFFFFFFFS
   SFFFFFFFFFFFFFFFFS
    SFFFFS    SFFFFS
    SSSSSS    SSSSSS
"""

def main():
    # Generate Dog
    dog_data = {
        "size": [32, 32],
        "palette": dog_palette,
        "frames": [
            {"name": "idle1", "pixels": grid_to_pixels(dog_idle1, dog_map)},
            {"name": "idle2", "pixels": grid_to_pixels(dog_idle2, dog_map)}
        ]
    }
    save_pet("pixel_dog.json", dog_data)
    
    # Generate Cat
    cat_data = {
        "size": [32, 32],
        "palette": cat_palette,
        "frames": [
            {"name": "idle1", "pixels": grid_to_pixels(cat_idle1, cat_map)},
            {"name": "idle2", "pixels": grid_to_pixels(cat_idle2, cat_map)}
        ]
    }
    save_pet("pixel_cat.json", cat_data)
    
    # Generate Rabbit
    rabbit_data = {
        "size": [32, 32],
        "palette": rabbit_palette,
        "frames": [
            {"name": "idle1", "pixels": grid_to_pixels(rabbit_idle1, rabbit_map)},
            {"name": "idle2", "pixels": grid_to_pixels(rabbit_idle2, rabbit_map)}
        ]
    }
    save_pet("pixel_rabbit.json", rabbit_data)

if __name__ == "__main__":
    main()
