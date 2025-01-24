from flask import Flask, request, render_template, redirect
from yaml import load, Loader
import random

# Load settings from YAML file
with open("settings.yml") as settingsfile:
    settings = load(settingsfile, Loader=Loader)

app = Flask(__name__)

# Initialize global variables
questions = []
operations = settings["operations"]
enablenegatives = settings["enable_negatives"]
totalquestions = settings["total_questions"]
maxvalue = settings["max_value"]
minvalue = settings["min_value"]
current_question_index = 0
num_correct = 0
num_wrong = 0

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route('/reset')
def reset():
    global questions
    global current_question_index
    global num_correct
    global num_wrong
    questions = []
    
    # Generate questions
    for i in range(totalquestions):
        x = random.randint(minvalue, maxvalue)
        y = random.randint(minvalue, maxvalue)
        operation = random.choice(operations)
        
        # Ensure that the smaller number comes first in the division problem
        if operation == "/":
            if x < y:
                x, y = y, x  # Swap x and y if x is smaller than y (so y comes first)
        
        if enablenegatives == False and y > x and operation in ["-", "/"]:
            x, y = y, x
        
        question = {'problem': f'{x} {operation} {y}'}
        
        if operation == "+":
            question['answer'] = x + y
        elif operation == "-":
            question['answer'] = x - y
        elif operation == "x":
            question['answer'] = x * y
        elif operation == "/":
            # Ensure division is valid for long division: x should be divisible by y
            while x % y != 0:  # Ensure that x is divisible by y without a remainder
                x = random.randint(minvalue, maxvalue)
                y = random.randint(minvalue, maxvalue)
                
            quotient = x // y  # Integer division (quotient)
            remainder = x % y  # This should always be zero for exact division
            
            # The problem presented to the user
            question['problem'] = f"{y} ÷ {x} = ? with remainder ?"
            question['answer'] = (quotient, remainder)  # Store as tuple
            
        questions.append(question)

    current_question_index = 0
    num_correct = 0
    num_wrong = 0
    return redirect("/play")

reset()

@app.route('/play', methods=['GET', 'POST'])
def index():
    global current_question_index, num_correct, num_wrong

    if request.method == 'POST':
        # Check if it's a division problem
        if '÷' in questions[current_question_index]['problem']:
            # Get both quotient and remainder from the user
            try:
                user_quotient = int(request.form['quotient'])
                user_remainder = int(request.form['remainder'])
            except ValueError:
                return "Invalid input. Please enter valid numbers for both quotient and remainder."

            actual_quotient, actual_remainder = questions[current_question_index]['answer']
            
            # Check if both quotient and remainder are correct
            if user_quotient == actual_quotient and user_remainder == actual_remainder:
                num_correct += 1
            else:
                num_wrong += 1
        else:
            # Get the answer for non-division problems
            try:
                user_answer = int(request.form['answer'])
            except ValueError:
                return "Invalid input. Please enter a valid number for the answer."

            actual_answer = questions[current_question_index]['answer']
            
            # Check if the answer is correct
            if user_answer == actual_answer:
                num_correct += 1
            else:
                num_wrong += 1
        
        current_question_index += 1
        
        if current_question_index < len(questions):
            problem = questions[current_question_index]['problem']
            return render_template('play.html', problem=problem, current_question_index=current_question_index, totalquestions=totalquestions)
        else:
            return render_template('results.html', num_correct=num_correct, num_wrong=num_wrong)

    if current_question_index < len(questions):
        problem = questions[current_question_index]['problem']
        return render_template('play.html', problem=problem, current_question_index=current_question_index, totalquestions=totalquestions)
    else:
        return render_template('results.html', num_correct=num_correct, num_wrong=num_wrong)

@app.route("/cheat")
def rickroll():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if __name__ == '__main__':
    app.run()
