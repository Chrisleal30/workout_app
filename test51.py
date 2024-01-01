
from datetime import datetime, timedelta


# Define the workout schedule
workout_schedule = {
    0: "Full Body",
    1: "Endurance",
    2: "Full Body",
    3: "Endurance",
    4: "Full Body",
    5: "Rest Day",
    6: "Rest Day"
}

# Define the progression pattern for full body workouts
full_body_progression = [
    (4, 4, 4), (5, 4, 4), (5, 5, 5), (6, 5, 5), (6, 6, 6), (7, 6, 6), (7, 7, 7)
]

# Define the progression pattern for endurance workouts
endurance_progression = [
    "Run 1 min, Walk 1 min, Repeat x 10",
    "Run 2 mins, Walk 4 mins, Repeat x 5",
    "Run 2 mins, Walk 4 mins, Repeat x 5",
    "Run 3 mins, Walk 3 mins, Repeat x 4",
    "Run 3 mins, Walk 3 mins, Repeat x 4",
    "Run 5 mins, Walk 3 mins, Repeat x 3",
    "Run 7 mins, Walk 2 mins, Repeat x 3",
    "Run 8 mins, Walk 2 mins, Repeat x 3",
    "Run 8 mins, Walk 2 mins, Repeat x 3",
    "Run 8 mins, Walk 2 mins, Repeat x 3",
    "Run 10 mins, Walk 2 mins, Repeat x 2, Run 5 mins",
    "Run 8 mins, Walk 2 mins, Repeat x 3",
    "Run 9 mins, Walk 1 min, Repeat x 3",
    "Run 12 mins, Walk 2 mins, Repeat x 2, Run 5 mins",
    "Run 8 mins, Walk 2 mins, Repeat x 3",
    "Run 15 mins, Walk 1 min, Repeat x 2",
    "Run 8 mins, Walk 2 mins, Repeat x 3"
]

# Exercise progressions
push_up_progression = [
    "Wall Push-up", "Incline Push-up", "Knee Push-up", 
    "Single Knee Push-up", "Single Knee Elevated Push-up", 
    "Push-up Negatives", "Half-rep Push-up", "Push-up"
]

pull_up_progression = [
    "Wall Pull-up", "Inverted Row (low)", "Inverted Row (high)",
    "Elevated Inverted Row", "Scapular Pull-ups", "Chair Assisted Pull-up",
    "Negative Pull-up", "Jump Pull-up", "Banded Pull-up", "Pull-up"
]

split_squat_progression = [
    "One-leg box squat", "Raised One-leg box squat", 
    "Raised Pistol squat progression (swings)"
]

# Initial progression stages
current_push_up_stage = 2  # Example initial stage
current_pull_up_stage = 4  # Example initial stage
current_split_squat_stage = 0  # Example initial stage

# Function to calculate the number of specific workout types since the start date
def count_workout_type_since_start(workout_type, start_date, today):
    count = 0
    for i in range((today - start_date).days + 1):
        if workout_schedule[(start_date + timedelta(days=i)).weekday()] == workout_type:
            count += 1
    return count

# Update the current stage of the exercise
def update_current_stage(current_stage, progression_list):
    return (current_stage + 1) % len(progression_list)

# Get the workout for a given day, including logic for advancing stages
def get_workout_for_day(day, start_date, current_push_up_stage, current_pull_up_stage, current_split_squat_stage):
    workout_type = workout_schedule[day.weekday()]

    if workout_type == "Full Body":
        count = count_workout_type_since_start(workout_type, start_date, day)
        cycle_length = len(full_body_progression)
        index = (count - 1) % cycle_length

        # Calculate the number of completed cycles
        completed_cycles = (count - 1) // cycle_length

        # Update the stages based on the number of completed cycles
        for _ in range(completed_cycles):
            current_push_up_stage = update_current_stage(current_push_up_stage, push_up_progression)
            current_pull_up_stage = update_current_stage(current_pull_up_stage, pull_up_progression)
            current_split_squat_stage = update_current_stage(current_split_squat_stage, split_squat_progression)

        sets_reps = full_body_progression[index]
        push_exercise = push_up_progression[current_push_up_stage]
        pull_exercise = pull_up_progression[current_pull_up_stage]
        leg_exercise = split_squat_progression[current_split_squat_stage]

        workout_details = {
            'sets_reps': sets_reps,
            'Push': push_exercise,
            'Pull': pull_exercise,
            'Legs': leg_exercise
        }
    elif workout_type == "Endurance":
        count = count_workout_type_since_start(workout_type, start_date, day)
        index = (count - 1) % len(endurance_progression)
        sets_reps = endurance_progression[index]
        workout_details = sets_reps
    else:
        workout_details = None  # No details for rest days

    return workout_type, workout_details, current_push_up_stage, current_pull_up_stage, current_split_squat_stage

# Initialize current stages (as in your Flask app)
current_push_up_stage = 2
current_pull_up_stage = 4
current_split_squat_stage = 0

# Modify your test function to use global variables
def test_for_day(day):
    global current_push_up_stage, current_pull_up_stage, current_split_squat_stage

    workout_type, workout_details, current_push_up_stage, current_pull_up_stage, current_split_squat_stage = get_workout_for_day(
        day, datetime(2023, 12, 20), current_push_up_stage, current_pull_up_stage, current_split_squat_stage
    )
    print(f"Day {day.strftime('%Y-%m-%d')}: {workout_type}, {workout_details}")

# Main testing loop for the next 65 days
start_date = datetime.now()
for i in range(65):  # 65 days
    day = start_date + timedelta(days=i)
    test_for_day(day)


