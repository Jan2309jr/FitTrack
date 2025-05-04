from flask import Flask, request, jsonify, send_file, session, render_template, redirect
from fpdf import FPDF
from io import BytesIO
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Important for session management

class UserData:
    def __init__(self, user_id, username, email, gender, age, height, weight, bmi, fitness_goal, target_weight, meals, workouts):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.gender = gender
        self.age = age
        self.height = height
        self.weight = weight
        self.bmi = bmi
        self.fitness_goal = fitness_goal
        self.target_weight = target_weight
        self.meals = meals
        self.workouts = workouts

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'fitness_goal': self.fitness_goal,
            'target_weight': self.target_weight,
            'meals': self.meals,
            'workouts': self.workouts
        }

class ReportGenerator:
    def __init__(self, user_data):
        self.user_data = user_data
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)

    def add_heading(self, title, level=1):
        if level == 1:
            self.pdf.set_font("Arial", 'B', size=16)
        else:
            self.pdf.set_font("Arial", 'B', size=14)
        self.pdf.cell(200, 10, txt=title, ln=1, align="C")
        self.pdf.ln(2)
        self.pdf.set_font("Arial", size=12)

    def add_section_heading(self, title):
        self.pdf.set_font("Arial", 'B', size=12)
        self.pdf.cell(200, 10, txt=title, ln=1)
        self.pdf.set_font("Arial", size=12)

    def add_paragraph(self, text):
        self.pdf.multi_cell(190, 8, txt=text)
        self.pdf.ln(2)

    def add_list_item(self, text):
        self.pdf.cell(10, 5, txt="-")
        self.pdf.cell(180, 5, txt=text, ln=1)

    def generate_personal_info(self):
        self.add_section_heading("Personal Information")
        self.add_list_item(f"Name: {self.user_data.username}")
        self.add_list_item(f"Email: {self.user_data.email}")
        self.add_list_item(f"Gender: {self.user_data.gender}")
        self.add_list_item(f"Age: {self.user_data.age} years")
        self.add_list_item(f"Height: {self.user_data.height} cm")
        self.add_list_item(f"Weight: {self.user_data.weight} kg")
        self.add_list_item(f"BMI: {self.user_data.bmi}")
        self.pdf.ln(2)

    def generate_fitness_goals(self):
        self.add_section_heading("Fitness Goals")
        self.add_list_item(f"Current Goal: {self.user_data.fitness_goal}")
        self.add_list_item(f"Target Weight: {self.user_data.target_weight} kg")
        self.pdf.ln(2)

    def generate_nutrition_summary(self):
        self.add_section_heading("Nutrition Summary")
        total_calories = sum(meal.get('calories', 0) for meal in self.user_data.meals)
        total_protein = sum(meal.get('protein', 0) for meal in self.user_data.meals)
        total_carbs = sum(meal.get('carbs', 0) for meal in self.user_data.meals)
        self.add_list_item(f"Total Calories: {total_calories} kcal")
        self.add_list_item(f"Total Protein: {total_protein} g")
        self.add_list_item(f"Total Carbs: {total_carbs} g")
        self.pdf.ln(2)

    def generate_activity_summary(self):
        self.add_section_heading("Activity Summary")
        total_exercises = len(self.user_data.workouts)
        total_duration = sum(workout.get('duration', 0) for workout in self.user_data.workouts)
        total_calories_burned = sum(workout.get('calories_burned', 0) for workout in self.user_data.workouts)
        self.add_list_item(f"Exercises Logged: {total_exercises}")
        self.add_list_item(f"Total Duration: {total_duration} minutes")
        self.add_list_item(f"Total Calories Burned: {total_calories_burned} kcal")
        self.pdf.ln(2)

    def generate_report(self):
        self.add_heading("FitTrack Fitness Report")
        self.generate_personal_info()
        self.generate_fitness_goals()
        self.generate_nutrition_summary()
        self.generate_activity_summary()
        buffer = BytesIO()
        self.pdf.output(buffer, 'S').encode('latin-1')
        buffer.seek(0)
        return buffer

# Dummy user data (replace with actual database or data retrieval)
users_data = {
    1: UserData(
        user_id=1,
        username="John Doe",
        email="john.doe@example.com",
        gender="Male",
        age=30,
        height=180,
        weight=75,
        bmi=23.1,
        fitness_goal="Weight Loss",
        target_weight=70,
        meals=[
            {"name": "Breakfast", "calories": 350, "protein": 15, "carbs": 40, "fat": 15},
            {"name": "Lunch", "calories": 500, "protein": 25, "carbs": 60, "fat": 20}
        ],
        workouts=[
            {"type": "Cardio", "name": "Running", "duration": 30, "calories_burned": 300},
            {"type": "Strength", "name": "Weight Lifting", "duration": 45, "calories_burned": 250}
        ]
    ),
    2: UserData(
        user_id=2,
        username="Jane Smith",
        email="jane.smith@example.com",
        gender="Female",
        age=25,
        height=165,
        weight=60,
        bmi=22.0,
        fitness_goal="Muscle Gain",
        target_weight=65,
        meals=[
            {"name": "Breakfast", "calories": 400, "protein": 20, "carbs": 45, "fat": 15},
            {"name": "Lunch", "calories": 550, "protein": 30, "carbs": 65, "fat": 20}
        ],
        workouts=[
            {"type": "Strength", "name": "Squats", "duration": 60, "calories_burned": 350}
        ]
    )
}

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/user/<int:user_id>')
def get_user_data(user_id):
    user = users_data.get(user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'message': 'User not found'}), 404

@app.route('/generate_report/<int:user_id>')
def generate_fitness_report(user_id):
    user = users_data.get(user_id)
    if user:
        report_generator = ReportGenerator(user)
        pdf_buffer = report_generator.generate_report()
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'fitness_report_user_{user_id}.pdf'
        )
    return jsonify({'message': 'User data not found for report generation'}), 404

if __name__ == '__main__':
    app.run(debug=True)