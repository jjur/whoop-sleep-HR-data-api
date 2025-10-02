#!/usr/bin/env python3
"""
Example showing how to use the comprehensive cycle data with all metrics.

This example demonstrates accessing:
- Recovery metrics (HRV, Resting HR, Recovery Score)
- Sleep metrics (Score, Duration, Stages, Respiratory Rate, Sleep Need)
- Strain metrics (Day Strain, Calories, Heart Rate)
- Activity/Workout details
"""

from whoop_data import (
    WhoopClient, 
    get_cycle_data,
    save_to_json,
    set_debug_logging
)

# Enable debug logging to see API calls
set_debug_logging()

# Initialize client
client = WhoopClient(username="your_email@example.com", password="your_password")

# Get comprehensive cycle data for the last 7 days
print("\n=== Getting Comprehensive Cycle Data ===")
cycles = get_cycle_data(client=client)

print(f"\nRetrieved {len(cycles)} cycles\n")

# Display detailed metrics for each cycle
for i, cycle in enumerate(cycles, 1):
    print(f"\n{'='*60}")
    print(f"Cycle {i}: {cycle['date']}")
    print(f"{'='*60}")
    
    # Recovery Metrics
    recovery = cycle['recovery']
    print(f"\n[RECOVERY METRICS]")
    print(f"   Recovery Score: {recovery['score']}%")
    print(f"   HRV: {recovery['hrv']} ms")
    print(f"   Resting Heart Rate: {recovery['resting_hr']} bpm")
    
    # Sleep Metrics
    print(f"\n[SLEEP METRICS]")
    for sleep in cycle['sleep']:
        if sleep['score']:
            hours = sleep['quality_duration'] / 3600000 if sleep['quality_duration'] else 0
            print(f"   Sleep Score: {sleep['score']}%")
            print(f"   Sleep Duration: {hours:.2f} hours")
            if sleep['sleep_efficiency'] is not None:
                print(f"   Sleep Efficiency: {sleep['sleep_efficiency']:.1f}%")
            if sleep['respiratory_rate'] is not None:
                print(f"   Respiratory Rate: {sleep['respiratory_rate']:.1f} breaths/min")
            if sleep['disturbances'] is not None:
                print(f"   Disturbances: {sleep['disturbances']}")
            
            # Sleep stages breakdown
            if sleep['slow_wave_sleep_duration']:
                deep_hours = sleep['slow_wave_sleep_duration'] / 3600000
                light_hours = sleep['light_sleep_duration'] / 3600000 if sleep['light_sleep_duration'] else 0
                rem_hours = sleep['rem_sleep_duration'] / 3600000 if sleep['rem_sleep_duration'] else 0
                wake_hours = sleep['wake_duration'] / 3600000 if sleep['wake_duration'] else 0
                
                print(f"\n   Sleep Stages:")
                print(f"      Deep (SWS): {deep_hours:.2f} hours")
                print(f"      Light: {light_hours:.2f} hours")
                print(f"      REM: {rem_hours:.2f} hours")
                print(f"      Awake: {wake_hours:.2f} hours")
            
            # Sleep need and debt
            if sleep['sleep_need']:
                need_hours = sleep['sleep_need'] / 3600000
                debt_pre_hours = sleep['debt_pre'] / 3600000 if sleep['debt_pre'] else 0
                debt_post_hours = sleep['debt_post'] / 3600000 if sleep['debt_post'] else 0
                print(f"\n   Sleep Need: {need_hours:.2f} hours")
                print(f"   Sleep Debt (before): {debt_pre_hours:.2f} hours")
                print(f"   Sleep Debt (after): {debt_post_hours:.2f} hours")
    
    # Strain Metrics
    strain = cycle['strain']
    print(f"\n[STRAIN METRICS]")
    print(f"   Day Strain: {strain['day_strain']:.1f}")
    print(f"   Average Heart Rate: {strain['day_avg_heart_rate']} bpm")
    print(f"   Max Heart Rate: {strain['day_max_heart_rate']} bpm")
    if strain['day_kilojoules']:
        calories = strain['day_kilojoules'] / 4.184  # Convert kJ to calories
        print(f"   Calories: {calories:.0f} cal")
    
    # Workout/Activity Details
    if cycle['workouts']:
        print(f"\n[WORKOUTS] ({len(cycle['workouts'])} activities):")
        for workout in cycle['workouts']:
            print(f"   - Activity ID: {workout['id']}")
            print(f"     Sport ID: {workout['sport_id']}")
            print(f"     Strain: {workout['strain']:.1f}")
            print(f"     Avg HR: {workout['avg_heart_rate']} bpm")
            print(f"     Max HR: {workout['max_heart_rate']} bpm")
            if workout['distance_meter']:
                distance_km = workout['distance_meter'] / 1000
                print(f"     Distance: {distance_km:.2f} km")
            if workout['kilojoules']:
                workout_calories = workout['kilojoules'] / 4.184
                print(f"     Calories: {workout_calories:.0f} cal")

# Save to JSON for further analysis
print(f"\n{'='*60}")
print("Saving comprehensive data to cycles.json...")
save_to_json(cycles, "cycles.json")
print("[OK] Data saved successfully!")

# Get sports history
print(f"\n{'='*60}")
print("\n=== Sports History ===")
sports = client.get_sports_history()
print(f"\nYou have tracked {len(sports)} different sport types:")
for sport in sports[:10]:  # Show first 10
    print(f"   - Sport ID {sport.get('id')}: {sport.get('name', 'Unknown')}")
if len(sports) > 10:
    print(f"   ... and {len(sports) - 10} more")

print(f"\n{'='*60}")
print("[DONE] All complete!")

