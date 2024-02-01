from flask import Flask, request, render_template, redirect
from yaml import load, Loader
import random

with open("settings.yml") as settingsfile:
    settings = load(settingsfile, Loader=Loader)

app = Flask(__name__)

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
    for i in range(totalquestions):
        x = random.randint(minvalue, maxvalue)
        y = random.randint(minvalue, maxvalue)
        operation = random.choice(operations)
        if enablenegatives == False and y > x:
            x, y = y, x
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
        user_answer = int(request.form['answer'])
        actual_answer = questions[current_question_index]['answer']
        
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
    app.run(debug=True, port=8000)
