from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

saved_surveys = []

QUESTION_TEMPLATES = {
    "rating": [
        "How satisfied are you with {topic}?",
        "How would you rate the quality of {topic}?",
        "How would you rate the service related to {topic}?",
        "How useful do you find {topic}?",
        "How would you rate your overall experience with {topic}?",
    ],
    "yes-no": [
        "Do you think {topic} meets your expectations?",
        "Would you recommend {topic} to others?",
        "Do you face any problem with {topic}?",
        "Is {topic} easy to use or access?",
        "Are you satisfied with {topic}?",
    ],
    "mcq": [
        "Which feature of {topic} do you like the most?",
        "What is your main reason for using {topic}?",
        "Which area of {topic} needs improvement?",
        "How often do you use {topic}?",
        "Which option best describes your experience with {topic}?",
    ],
    "short": [
        "What improvement would you suggest for {topic}?",
        "What problem do you face while using {topic}?",
        "What do you like most about {topic}?",
        "Write your feedback about {topic}.",
        "What changes should be made in {topic}?",
    ],
}


def build_question(topic, question_type, index):
    template = QUESTION_TEMPLATES[question_type][index % len(QUESTION_TEMPLATES[question_type])]
    question = {
        "text": template.format(topic=topic),
        "type": question_type,
        "options": [],
    }

    if question_type == "mcq":
        question["options"] = ["Excellent", "Good", "Average", "Poor"]
    elif question_type == "rating":
        question["options"] = ["1", "2", "3", "4", "5"]
    elif question_type == "yes-no":
        question["options"] = ["Yes", "No"]

    return question


def generate_questions(topic, count, selected_type):
    question_types = ["rating", "yes-no", "mcq", "short"]
    questions = []

    for index in range(count):
        question_type = question_types[index % len(question_types)] if selected_type == "mixed" else selected_type
        questions.append(build_question(topic, question_type, index))

    return questions


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/api/generate", methods=["POST"])
def generate_survey():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    topic = data.get("topic", "").strip()
    question_count = int(data.get("questionCount", 5))
    question_type = data.get("questionType", "mixed")

    if not title or not topic:
        return jsonify({"error": "Survey title and topic are required."}), 400

    question_count = max(3, min(question_count, 15))
    survey = {
        "id": int(datetime.now().timestamp() * 1000),
        "title": title,
        "topic": topic,
        "createdAt": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
        "questions": generate_questions(topic, question_count, question_type),
    }

    return jsonify(survey)


@app.route("/api/surveys", methods=["GET"])
def get_surveys():
    return jsonify(saved_surveys)


@app.route("/api/surveys", methods=["POST"])
def save_survey():
    survey = request.get_json() or {}

    if not survey.get("title") or not survey.get("questions"):
        return jsonify({"error": "Valid survey data is required."}), 400

    saved_surveys.insert(0, survey)
    return jsonify({"message": "Survey saved successfully.", "survey": survey}), 201


@app.route("/api/surveys", methods=["DELETE"])
def clear_surveys():
    saved_surveys.clear()
    return jsonify({"message": "All saved surveys cleared."})


if __name__ == "__main__":
    app.run(debug=True)
