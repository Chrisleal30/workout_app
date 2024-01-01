from flask import Flask, render_template, session
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key


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


# Function to calculate the number of specific workout types since the start date
def count_workout_type_since_start(workout_type, start_date, today):
    count = 0
    for i in range((today - start_date).days + 1):
        if workout_schedule[(start_date + timedelta(days=i)).weekday()] == workout_type:
            count += 1
    return count

# Function to count the number of completed full body progression cycles
def count_full_body_cycles(start_date, end_date):
    full_body_count = count_workout_type_since_start("Full Body", start_date, end_date)
    cycles_completed = full_body_count // len(full_body_progression)
    return cycles_completed

# Update the current stage of the exercise
def update_current_stage(current_stage, progression_list):
    return (current_stage + 1) % len(progression_list)

# Get the workout for a given day, including logic for advancing stages
def get_workout_for_day(day, start_date):
    workout_type = workout_schedule[day.weekday()]

    # Retrieve current stages from session
    current_push_up_stage = session.get('current_push_up_stage', 2)
    current_pull_up_stage = session.get('current_pull_up_stage', 4)
    current_split_squat_stage = session.get('current_split_squat_stage', 0)

    if workout_type == "Full Body":
        count = count_workout_type_since_start(workout_type, start_date, day)
        cycle_length = len(full_body_progression)
        index = (count - 1) % cycle_length

        # Calculate the number of completed cycles
        completed_cycles = (count - 1) // cycle_length

        # Update the stages based on the number of completed cycles
        for i in range(completed_cycles):
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

    return workout_type, workout_details

@app.route('/adjust_stage/<exercise>/<direction>')
def adjust_stage(exercise, direction):
    # Validate input
    if exercise not in ['push_up', 'pull_up', 'split_squat']:
        return "Invalid exercise", 400
    if direction not in ['increment', 'decrement']:
        return "Invalid direction", 400

    # Adjust the stage
    key = f'current_{exercise}_stage'
    current_stage = session.get(key, default_stages[exercise])
    if direction == 'increment':
        current_stage = (current_stage + 1) % len(progression_lists[exercise])
    else:
        current_stage = (current_stage - 1) % len(progression_lists[exercise])
    session[key] = current_stage

    return "Stage adjusted", 200

@app.route('/')
def index():
    # Initialize session variables if they do not exist
    if 'current_push_up_stage' not in session:
        session['current_push_up_stage'] = 2  # Default initial stage
    if 'current_pull_up_stage' not in session:
        session['current_pull_up_stage'] = 4  # Default initial stage
    if 'current_split_squat_stage' not in session:
        session['current_split_squat_stage'] = 0  # Default initial stage

    today = datetime.now()

    # Determine workout type for today without affecting progression stages
    workout_type_for_today = workout_schedule[today.weekday()]
    
    if workout_type_for_today == "Full Body":
        start_date = datetime(2023, 12, 20)  # Start date for Full Body
    elif workout_type_for_today == "Endurance":
        start_date = datetime(2023, 12, 28)  # Start date for Endurance
    else:
        start_date = datetime(2023, 12, 20)  # Default start date or handle differently for Rest Days

    workout_type, workout_details = get_workout_for_day(today, start_date)

    return render_template('index.html', date=today.strftime("%Y-%m-%d"), workout_type=workout_type,
                           workout_details=workout_details,
                           current_push_up_stage=current_push_up_stage,
                           current_pull_up_stage=current_pull_up_stage,
                           current_split_squat_stage=current_split_squat_stage)

if __name__ == '__main__':
    app.run()