import math
from haversine import haversine, Unit

# UNSW Kensington campus buildings with their coordinates
# Format: {building_code: {"name": building_name, "coordinates": (latitude, longitude)}}
# GPS coordinates for more accurate mapping
# pip install haversine
buildings = {
    "J17": {"name": "Ainsworth Building", "coordinates": (-33.918517519993465, 151.23151583001268)},
    "H6": {"name": "Tyree Energy Technologies Building", "coordinates": (-33.91762963446875, 151.22674975329997)},
    "E8": {"name": "Chemical Sciences", "coordinates": (-33.9173, 151.2307)},
    "K15": {"name": "Electrical Engineering", "coordinates": (-33.9168, 151.2283)},
    "H13": {"name": "Science and Engineering Building", "coordinates": (-33.9189, 151.2277)},
    "F8": {"name": "Mathews Building", "coordinates": (-33.9184, 151.2335)},
    "E26": {"name": "Science and Engineering Building", "coordinates": (-33.9192, 151.2317)},
    "D9": {"name": "Quadrangle Building", "coordinates": (-33.917079138644446, 151.23056358735758)},
    "H10": {"name": "Sam Cracknell Pavilion", "coordinates": (-33.9200, 151.2280)},
    "F21": {"name": "UNSW Library", "coordinates": (-33.91736698535717, 151.23343618608945)},
    "F20": {"name": "Wallace Wurth Building", "coordinates": (-33.9182, 151.2326)},
    "G17": {"name": "Law Building", "coordinates": (-33.9177, 151.2295)},
    "E4": {"name": "Civil Engineering Building", "coordinates": (-33.9156, 151.2305)},
    "D10": {"name": "Chancellery", "coordinates": (-33.9154, 151.2325)},
    "H8": {"name": "John Niland Scientia Building", "coordinates": (-33.9168, 151.2260)},
    "K17": {"name": "School of Computer Science and Engineering", "coordinates": (-33.91866127702827, 151.2309250200572)},
    "G6": {"name": "The Square House", "coordinates": (-33.9160275054492, 151.22637472446445)},
    "F10": {"name": "Michael Birt Arcade", "coordinates": (-33.9166, 151.2310)},
    "D2": {"name": "AGSM Building", "coordinates": (-33.918028625320794, 151.23683833156448)},
    "J14": {"name": "Keith Burrows Theatre", "coordinates": (-33.9181394558123, 151.2302026932067)},
    "D23": {"name": "Mathews Theatres", "coordinates": (-33.91708922725474, 151.2342204993276)},
    "F23": {"name": "Mathews Theatres", "coordinates": (-33.91758430549228, 151.23514248898576)},
    "M15": {"name": "Rupert Myers Building", "coordinates": (-33.91871302947675, 151.23052416334914)},
    "E19": {"name": "Patricia O'Shane Building", "coordinates": (-33.91709506702178, 151.23248880538088)},
    "B16": {"name": "Colombo Theatre", "coordinates": (-33.915871204382775, 151.231540087025175)},
    "F10": {"name": "June Griffith Building", "coordinates": (-33.91675795632593, 151.2289202109714)},
    "K15": {"name": "Old Main Building", "coordinates": (-33.91765269713936, 151.23082591731696)},

}

def calculate_distance(point1, point2):
    """Calculate distance between two GPS coordinates using haversine library."""

    distance_km = haversine(point1, point2, unit=Unit.KILOMETERS)
    return distance_km * 1000 

def find_nearest_buildings(location, n=5):
    """Find the n nearest buildings to the given location."""
    distances = []
    
    for code, building in buildings.items():
        distance = calculate_distance(location, building["coordinates"])
        distances.append((code, building["name"], distance))
    
    distances.sort(key=lambda x: x[2])
    
    return distances[:n]


def main():
    print("UNSW Kensington Campus Navigator")
    print("--------------------------------")
    

    try:
        input_location = input("Enter location (building code or 'coord' for coordinates): ").strip()
        
        if input_location.lower() == "coord":

            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            user_location = (lat, lon)
            location_type = f"coordinates ({lat}, {lon})"
        elif input_location in buildings:

            user_location = buildings[input_location]["coordinates"]
            location_type = f"Building {input_location} ({buildings[input_location]['name']})"
        else:
            print(f"Building code {input_location} not found. Available building codes:")
            for code in sorted(buildings.keys()):
                print(f"{code}: {buildings[code]['name']}")
            return
    except ValueError:
        print("Invalid input. Please enter a valid building code or 'coord' for coordinates.")
        return
    

    try:
        num_results = int(input("How many nearest buildings to show? (default: 5): ") or "5")
    except ValueError:
        num_results = 5
    
   
    nearest = find_nearest_buildings(user_location, num_results)
    
    print(f"\nNearest buildings to {location_type}:")
    print("-" * 60)
    print(f"{'Building Code':<15}{'Building Name':<35}{'Distance':<15}")
    print("-" * 60)
    
    for code, name, distance in nearest:
        print(f"{code:<15}{name:<35}{distance:.2f} meters")

if __name__ == "__main__":
    main()