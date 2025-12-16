#!/usr/bin/env python3
"""
Elite Exobiologist Route Sorter (EERS)
A tool I originally made for myself, but I decided to share with fellow CMDR's! 
The tool uses the data from wanderer-toolbox.com's billionaires boulevard and
fetches coordinates from edsm.net to create
the shortest possible route to each star system using a greedy algo.
Let me know if anything breaks or if you want anything else added :)
My first github program so be nice! And remember to fly safe out there CMDR's! 
Happy hunting!
"""

import os
import sys
import time
import math
import requests
from typing import List, Tuple, Dict, Optional, Any


def load_target_data_with_bodies(filename: str) -> Dict[str, str]:
    """
    Reads system and body names from the included system data file.
    
    Args:
        filename: Path to the file (format: System Name | Body String)
        
    Returns:
        A dictionary mapping {System Name: Body String}.
    """
    system_body_map = {}
    try:
        # Check if the file exists before attempting to open it
        if not os.path.exists(filename):
            print(f"Error: Input file '{filename}' not found.")
            return {}

        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                
                # Skips coments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Splits using the pipe character (|)
                parts = line.split('|', 1) # Split only once
                
                if len(parts) == 2:
                    system_name = parts[0].strip()
                    body_name = parts[1].strip()
                    
                    if system_name:
                        # Store the clean system name and its planet body string
                        system_body_map[system_name] = body_name
        
        if not system_body_map:
            print(f"Warning: No valid 'System | Body' pairs found in {filename}.")
            
        return system_body_map
        
    except Exception as e:
        print(f"Error reading file '{filename}': {str(e)}")
        return {}


def fetch_system_coordinates(system_name: str) -> Optional[Tuple[float, float, float]]:
    """
    Fetches X, Y, Z coordinates for a star system from the EDSM API.
    """
    url = "https://www.edsm.net/api-v1/system"
    params = {
        "systemName": system_name,
        "showCoordinates": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        data = response.json()
        
        if data and "coords" in data:
            return (
                float(data["coords"]["x"]),
                float(data["coords"]["y"]),
                float(data["coords"]["z"])
            )
        else:
            print(f"Warning: System '{system_name}' not found or has no coordinates in EDSM database.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"API Error: Failed to fetch coordinates for '{system_name}': {str(e)}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Data Error: Invalid data received for '{system_name}': {str(e)}")
        return None


def calculate_distance(coords1: Tuple[float, float, float], 
                       coords2: Tuple[float, float, float]) -> float:
    """
    Calculates the 3D Euclidean distance between two points in LY.
    """
    x1, y1, z1 = coords1
    x2, y2, z2 = coords2
    
    # Euclidean distance formula: sqrt((x2-x1)² + (y2-y1)² + (z2-z1)²)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def sort_exobio_systems() -> None:
    """
    Main function to sort systems using the greedy algorithm
    """
    INPUT_FILE = "target_data_input.txt"

    # Read starting system from user
    start_system = input("Enter your starting system: ").strip()
    if not start_system:
        print("Error: Starting system cannot be empty.")
        return
    
    # Load target systems and body map
    system_body_map = load_target_data_with_bodies(INPUT_FILE)
    if not system_body_map:
        print("Error: No target systems available. Please check your input file.")
        return
    
    # Prepare the list of systems for the greedy algorithm (the keys)
    unvisited_systems_list = list(system_body_map.keys())
    
    # Fetch coordinates for starting system
    print(f"Fetching coordinates for starting system '{start_system}'...")
    start_coords = fetch_system_coordinates(start_system)
    if not start_coords:
        print(f"Error: Could not fetch coordinates for starting system '{start_system}'.")
        return
    time.sleep(0.2)
    
    # Initialize variables for the greedy algorithm
    current_system = start_system
    current_coords = start_coords
    route = []
    total_distance = 0.0
    
    # Dictionary to store coordinates for systems we've visited already
    coords_cache = {start_system: start_coords}
    
    print("\nCalculating optimal route using Greedy Algorithm...")
    
    # Greedy algo main loop
    while unvisited_systems_list:
        closest_system = None
        closest_distance = float('inf')
        closest_coords = None
        system_to_remove = None # Temporary variable to track the system to remove
        
        # We iterate over a copy of the list because we need to remove skipped systems
        for system in list(unvisited_systems_list):
            
            # --- Coordinate Lookup/Fetch ---
            system_coords = coords_cache.get(system)
            if not system_coords:
                # Fetch coordinates if not in cache
                print(f"Fetching coordinates for '{system}'...")
                system_coords = fetch_system_coordinates(system)
                time.sleep(0.2) # Delay to prevent API rate limiting
                
                if system_coords:
                    coords_cache[system] = system_coords
                else:
                    # If coordinates fail, remove this system from the route
                    print(f"Warning: Skipping system '{system}' due to missing coordinates.")
                    unvisited_systems_list.remove(system)
                    continue # Skip to the next system in the list
            
            # --- Distance Calculation ---
            distance = calculate_distance(current_coords, system_coords)
            
            # Update closest system if this one is closer
            if distance < closest_distance:
                closest_system = system
                closest_distance = distance
                closest_coords = system_coords
                system_to_remove = system

        # If we found a closest system, add it to our route
        if closest_system:
            route.append((current_system, closest_system, closest_distance))
            total_distance += closest_distance
            
            # Update current position
            current_system = closest_system
            current_coords = closest_coords
            
            # Remove the visited system from unvisited list
            unvisited_systems_list.remove(system_to_remove)
        else:
            # If the list is not empty but we found no closest system, it means 
            # all remaining systems failed coordinate lookup.
            if unvisited_systems_list:
                print("Warning: All remaining systems failed coordinate lookup. Route calculation incomplete.")
            break
    
    # --- Display the final route with Target Bodies ---
    
    systems_in_route = len(route)
    total_targets = len(system_body_map)
    
    print("\n=== Elite Exobiologist Route Sorter Results ===")
    print(f"Starting System: {start_system}")
    print(f"Total Target Systems in File: {total_targets}")
    print(f"Systems Included in Route: {systems_in_route}")
    
    print("\nOptimized Route (Greedy Algorithm):")
    
    # Define header format with fixed-width columns
    # Adjust widths as necessary for the longer system names
    header_format = "{:<5} {:<30} → {:<30} {:<25} {:>12}"
    
    header_str = header_format.format("Step", "From System", "To System", "Target Bodies", "Distance (LY)")
    print("=" * len(header_str))
    print(header_str)
    print("=" * len(header_str))
    
    for i, (from_sys, to_sys, dist) in enumerate(route, 1):
        # Retrieve the planet/body string for the destination system (to_sys)
        target_bodies = system_body_map.get(to_sys, "N/A") 
        
        # Use f-string formatting for aligned columns
        print(header_format.format(
            i, 
            from_sys, 
            to_sys, 
            target_bodies, 
            f"{dist:.2f}"
        ))
    
    print("=" * len(header_str))
    print(f"\nTotal Greedy Distance: {total_distance:.2f} LY")
    print("==========================================================================")


if __name__ == "__main__":
    print("Elite Exobiologist Route Sorter (EERS)")
    print("--------------------------------------")
    sort_exobio_systems()