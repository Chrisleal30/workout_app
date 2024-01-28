from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from pytz import timezone


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wod.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Defining the db model
class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    change_push_up_stage = db.Column(db.Integer, default=0)
    change_pull_up_stage = db.Column(db.Integer, default=0)
    change_split_squat_stage = db.Column(db.Integer, default=0)
    change_full_body_progression = db.Column(db.Integer, default=0)
    change_endurance_progression = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.user_id}>'

# Initializing the db
with app.app_context():
    db.create_all()



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
    "Run 8 mins, Walk 2 mins, Repeat x 3",
    "Run 1 min, Walk 1 min, Repeat x 15",
    "Run 2 mins, Walk 4 mins, Repeat x 8",
    "Run 2 mins, Walk 4 mins, Repeat x 8",
    "Run 3 mins, Walk 3 mins, Repeat x 7",
    "Run 3 mins, Walk 3 mins, Repeat x 7",
    "Run 5 mins, Walk 3 mins, Repeat x 5",
    "Run 7 mins, Walk 2 mins, Repeat x 5",
    "Run 8 mins, Walk 2 mins, Repeat x 5",
    "Run 8 mins, Walk 2 mins, Repeat x 5",
    "Run 8 mins, Walk 2 mins, Repeat x 5",
    "Run 10 mins, Walk 2 mins, Repeat x 4, Run 5 mins",
    "Run 8 mins, Walk 2 mins, Repeat x 5",
    "Run 9 mins, Walk 1 min, Repeat x 5",
    "Run 12 mins, Walk 2 mins, Repeat x 4, Run 5 mins",
    "Run 8 mins, Walk 2 mins, Repeat x 5",
    "Run 15 mins, Walk 1 min, Repeat x 4",
    "Run 8 mins, Walk 2 mins, Repeat x 5"
]

# Exercise progressions
push_up_progression = [
    "Wall Push-up", "Incline Push-up", "Knee Push-up", 
    "Single Knee Push-up", "Single Knee Elevated Push-up", 
    "Push-up Negatives", "Half-rep Push-up", "Push-up", "Push-up 5lbs",
    "Push-up 10lbs", "Push-up 15lbs", "Push-up 20lbs"
]

pull_up_progression = [
    "Wall Pull-up", "Inverted Row (low)", "Inverted Row (high)",
    "Elevated Inverted Row", "Scapular Pull-ups Assisted", "Scapular Pull-ups Dead-hang", "Chair Assisted Pull-up",
    "Negative Pull-up", "Jump Pull-up", "Banded Pull-up", "Pull-up", "Pull-up 5lbs", "Pull-up 10lbs", "Pull-up 15lbs"
]

split_squat_progression = [
    "One-leg box squat", "Raised One-leg box squat", 
    "ATG Split Squat LVL1", "ATG Split Squat LVL1 Loaded", "ATG Split Squat LVL2", "ATG Split Squat LVL2 Loaded", 
    "ATG Split Squat LVL3", "ATG Split Squat LVL3 Loaded", 'ATG Split Squat', "ATG Split Squat Loaded"
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
    user_id = 1

    # Fetch user progress from the database
    user_progress = UserProgress.query.filter_by(user_id=user_id).first()

    if not user_progress:
        # No record found, so create a new one with default values
        user_progress = UserProgress(user_id=user_id)
        db.session.add(user_progress)
        db.session.commit()
    
    # Use the values from the database
    change_push_up_stage = user_progress.change_push_up_stage
    change_pull_up_stage = user_progress.change_pull_up_stage
    change_split_squat_stage = user_progress.change_split_squat_stage
    change_full_body_progression = user_progress.change_full_body_progression
    change_endurance_progression = user_progress.change_endurance_progression

    if workout_type == "Full Body":
        count = count_workout_type_since_start(workout_type, start_date, day)
        cycle_length = len(full_body_progression)
        index = ((count - 1) + change_full_body_progression) % cycle_length

        # Calculate the number of completed cycles
        completed_cycles = (count - 1) // cycle_length

        #Exercise cycle length
        push_up_cycle_length = len(push_up_progression)
        pull_up_cycle_length = len(pull_up_progression)
        split_squat_cycle_length = len(split_squat_progression)
        
        # Initial progression stages
        i_push_up_stage = 2  # Example initial stage
        i_pull_up_stage = 4  # Example initial stage
        i_split_squat_stage = 0  # Example initial stage
        
        #Exercise stage index (The number of cycles completed + the initial exercise stage) 
        current_push_up_stage = (completed_cycles + i_push_up_stage + change_push_up_stage) % push_up_cycle_length
        current_pull_up_stage = (completed_cycles + i_pull_up_stage + change_pull_up_stage) % pull_up_cycle_length
        current_split_squat_stage = (completed_cycles + i_split_squat_stage + change_split_squat_stage) % split_squat_cycle_length
        

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
        index = ((count - 1) + change_endurance_progression) % len(endurance_progression)
        sets_reps = endurance_progression[index]
        workout_details = sets_reps
    else:
        workout_details = None  # No details for rest days

    return workout_type, workout_details, current_push_up_stage, current_pull_up_stage, current_split_squat_stage

@app.route('/adjust_stage/<stage>/<direction>')
def adjust_stage(stage, direction):
    user_id = 1  # Replace with actual user identification mechanism

    # Fetch the user's progress or create a new entry if it doesn't exist
    progress = UserProgress.query.filter_by(user_id=user_id).first()
    if not progress:
        progress = UserProgress(user_id=user_id)
        db.session.add(progress)

    # Adjust the stage based on the input
    if stage == 'push':
        progress.change_push_up_stage += 1 if direction == 'increment' else -1
    if stage == 'pull':
        progress.change_pull_up_stage += 1 if direction == 'increment' else -1
    if stage == 'legs':
        progress.change_split_squat_stage += 1 if direction == 'increment' else -1
    if stage == 'full_body':
        progress.change_full_body_progression += 1 if direction == 'increment' else -1
    if stage == 'endurance':
        progress.change_endurance_progression += 1 if direction == 'increment' else -1
    # Similar adjustments for other stages

    db.session.commit()

    return "Stage adjusted", 200

@app.route('/')
def index():
    global current_push_up_stage, current_pull_up_stage, current_split_squat_stage
    
    cst = timezone('US/Central')
    today = datetime.now(cst).date() + timedelta(days=0)

    # Determine workout type for today without affecting progression stages
    workout_type_for_today = workout_schedule[today.weekday()]
    
    if workout_type_for_today == "Full Body":
        start_date = cst.localize(datetime(2023, 12, 20)).date()  # Start date for Full Body
    elif workout_type_for_today == "Endurance":
        start_date = cst.localize(datetime(2023, 12, 28)).date()  # Start date for Endurance
    else:
        start_date = cst.localize(datetime(2023, 12, 20)).date()  # Default start date or handle differently for Rest Days

    workout_type, workout_details, current_push_up_stage, current_pull_up_stage, current_split_squat_stage = get_workout_for_day(today, start_date, current_push_up_stage, current_pull_up_stage, current_split_squat_stage)

    return render_template('index.html', date=today.strftime("%Y-%m-%d"), workout_type=workout_type, workout_details=workout_details)

if __name__ == '__main__':
    app.run()