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
max_dividend = settings.get("max_dividend", maxvalue)  # Limit for dividend
max_divisor = settings.get("max_divisor", maxvalue)  # Limit for divisor
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
        
        # For division problems, ensure the smaller number is the divisor
        if operation == "/":
            # Limit both the dividend and divisor
            x = random.randint(minvalue, min(max_dividend, maxvalue))  # Ensure the dividend doesn't exceed max_dividend
            y = random.randint(minvalue, min(max_divisor, maxvalue))  # Ensure the divisor doesn't exceed max_divisor

            # Randomly decide if the division will have a remainder or not
            has_remainder = random.choice([True, False])  # Randomly choose if the division has a remainder
            
            if has_remainder:
                # Ensure division has a remainder by making sure x is not divisible by y
                while x % y == 0:  # Ensure that x is not evenly divisible by y
                    x = random.randint(minvalue, min(max_dividend, maxvalue))  # Ensure the dividend is within the limit
                    y = random.randint(minvalue, min(max_divisor, maxvalue))  # Ensure the divisor is within the limit
            else:
                # Ensure division is exact (no remainder)
                while x % y != 0:  # Ensure that x is evenly divisible by y
                    x = random.randint(minvalue, min(max_dividend, maxvalue))  # Ensure the dividend is within the limit
                    y = random.randint(minvalue, min(max_divisor, maxvalue))  # Ensure the divisor is within the limit
            
            # Ensure the smaller number is the divisor (outside the square)
            if x < y:
                x, y = y, x  # Swap x and y if x is smaller (make y the divisor)
            
            quotient = x // y  # Integer division (quotient)
            remainder = x % y  # The remainder, 0 if no remainder exists
            
            # The problem presented to the user
            question = {'problem': f"What is the quotient and remainder when dividing {x} by {y}?"}
            question['answer'] = (quotient, remainder)  # Store as tuple (quotient, remainder)
        
        else:
            question = {'problem': f'{x} {operation} {y}'}
        
            if operation == "+":
                question['answer'] = x + y
            elif operation == "-":
                question['answer'] = x - y
            elif operation == "x":
                question['answer'] = x * y
        
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
        if 'What is the quotient and remainder' in questions[current_question_index]['problem']:
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
