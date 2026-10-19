from flask import Flask, render_template, request, jsonify, session
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "guessify-local-demo-key-change-before-deploy")

def reset_game():
    session["secret_number"] = random.randint(1, 100)
    session["attempts_left"] = 7
    session["game_over"] = False
    session["won"] = False

@app.route("/")
def home():
    reset_game()
    return render_template("index.html")

@app.route("/guess", methods=["POST"])
def make_guess():
    data = request.get_json(silent=True) or {}
    try:
        number = int(data.get("guess"))
    except (TypeError, ValueError):
        return jsonify(ok=False, message="Please enter a whole number."), 400

    if not 1 <= number <= 100:
        return jsonify(ok=False, message="Enter a number from 1 to 100."), 400
    if session.get("game_over", True):
        return jsonify(ok=False, message="This round has ended. Start a new game to play again."), 400

    secret = session["secret_number"]
    session["attempts_left"] -= 1
    left = session["attempts_left"]

    if number == secret:
        session["game_over"] = True
        session["won"] = True
        message = f"Excellent! {secret} is correct. You cracked the code!"
    elif left == 0:
        session["game_over"] = True
        session["won"] = False
        message = f"Out of attempts! The secret number was {secret}. Try another round."
    elif number < secret:
        message = "A little low — try a higher number."
    else:
        message = "A little high — try a lower number."

    return jsonify(ok=True, message=message, attempts_left=left,
                   game_over=session["game_over"], won=session["won"])

@app.route("/new-game", methods=["POST"])
def new_game():
    reset_game()
    return jsonify(ok=True, attempts_left=7, message="New round started. Good luck!")

if __name__ == "__main__":
    app.run(debug=True)
