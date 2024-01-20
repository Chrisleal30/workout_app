from flask import Flask, render_template, session
from datetime import datetime, timedelta
from pytz import timezone


app = Flask(__name__)
app.secret_key = 'your_secret_key'


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
    "Elevated Inverted Row", "Scapular Pull-ups Assisted", "Scapular Pull-ups Dead-hang", "Chair Assisted Pull-up",
    "Negative Pull-up", "Jump Pull-up", "Banded Pull-up", "Pull-up"
]

pistol_squat_progression = [
    "One-leg box squat", "Raised One-leg box squat", 
    "Raised Pistol squat progression (swings)"
]

# Initial progression stages
current_push_up_stage = 2  # Example initial stage
current_pull_up_stage = 4  # Example initial stage
current_pistol_squat_stage = 0  # Example initial stage

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
def get_workout_for_day(day, start_date, current_push_up_stage, current_pull_up_stage, current_pistol_squat_stage):
    workout_type = workout_schedule[day.weekday()]

    # Retrieve stage changes
    change_push_up_stage = session.get('change_push_up_stage', 0)
    change_pull_up_stage = session.get('change_pull_up_stage', 0)
    change_pistol_squat_stage = session.get('change_pistol_squat_stage', 0)
    change_full_body_progression = session.get('change_full_body_progression', 0)
    change_endurance_progression = session.get('change_endurance_progression', 0)
    
    if workout_type == "Full Body":
        count = count_workout_type_since_start(workout_type, start_date, day)
        cycle_length = len(full_body_progression)
        index = ((count - 1) + change_full_body_progression) % cycle_length

        # Calculate the number of completed cycles
        completed_cycles = (count - 1) // cycle_length

        #Exercise cycle length
        push_up_cycle_length = len(push_up_progression)
        pull_up_cycle_length = len(pull_up_progression)
        pistol_squat_cycle_length = len(pistol_squat_progression)
        
        # Initial progression stages
        i_push_up_stage = 2  # Example initial stage
        i_pull_up_stage = 4  # Example initial stage
        i_pistol_squat_stage = 0  # Example initial stage
        
        #Exercise stage index (The number of cycles completed + the initial exercise stage) 
        current_push_up_stage = (completed_cycles + i_push_up_stage + change_push_up_stage) % push_up_cycle_length
        current_pull_up_stage = (completed_cycles + i_pull_up_stage + change_pull_up_stage) % pull_up_cycle_length
        current_pistol_squat_stage = (completed_cycles + i_pistol_squat_stage + change_pistol_squat_stage) % pistol_squat_cycle_length
        

        sets_reps = full_body_progression[index]
        push_exercise = push_up_progression[current_push_up_stage]
        pull_exercise = pull_up_progression[current_pull_up_stage]
        leg_exercise = pistol_squat_progression[current_pistol_squat_stage]

        workout_details = {
            'sets_reps': sets_reps,
            'Push': push_exercise,
            'Pull': pull_exercise,
            'Legs': leg_exercise
        }
    
    elif workout_type == "Endurance":
        count = count_workout_type_since_start(workout_type, start_date, day)
        index = ((count - 1) + change_endurance_progression) % len(endurance_progression)
        sets_reps = endurance_progression[index]
        workout_details = sets_reps
    else:
        workout_details = None  # No details for rest days

    return workout_type, workout_details, current_push_up_stage, current_pull_up_stage, current_pistol_squat_stage

@app.route('/adjust_stage/<stage>/<direction>')
def adjust_stage(stage, direction):
    # Validate input
    if stage not in ['push', 'pull', 'legs', 'full_body', 'endurance']:
        return "Invalid stage", 400
    if direction not in ['increment', 'decrement']:
        return "Invalid direction", 400


    # Define the session keys for each stage type
    session_keys = {
        'push': 'change_push_up_stage',
        'pull': 'change_pull_up_stage',
        'legs': 'change_pistol_squat_stage',
        'full_body': 'change_full_body_progression',
        'endurance': 'change_endurance"progression'
    }

    # Adjust the stage
    key = session_keys[stage]
    changed_stage = session.get(key, 0)  # Default stage can be adjusted as needed
    if direction == 'increment':
        changed_stage += 1
    elif direction == 'decrement':
        changed_stage -= 1
    session[key] = changed_stage
    session.modified = True  # Mark the session as modified

    return "Stage adjusted", 200

@app.route('/')
def index():
    global current_push_up_stage, current_pull_up_stage, current_pistol_squat_stage
    
    cst = timezone('US/Central')
    today = datetime.now(cst).date() + timedelta(days=2)

    # Determine workout type for today without affecting progression stages
    workout_type_for_today = workout_schedule[today.weekday()]
    
    if workout_type_for_today == "Full Body":
        start_date = cst.localize(datetime(2023, 12, 20)).date()  # Start date for Full Body
    elif workout_type_for_today == "Endurance":
        start_date = cst.localize(datetime(2023, 12, 28)).date()  # Start date for Endurance
    else:
        start_date = cst.localize(datetime(2023, 12, 20)).date()  # Default start date or handle differently for Rest Days

    workout_type, workout_details, current_push_up_stage, current_pull_up_stage, current_pistol_squat_stage = get_workout_for_day(today, start_date, current_push_up_stage, current_pull_up_stage, current_pistol_squat_stage)

    return render_template('index.html', date=today.strftime("%Y-%m-%d"), workout_type=workout_type, workout_details=workout_details)

if __name__ == '__main__':
    app.run()
