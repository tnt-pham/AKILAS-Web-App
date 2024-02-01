import logging
import re

from flask import Flask, Markup, render_template, request
from nltk import sent_tokenize
import requests

from discoursesegmenter import DiscourseSegmenter


app = Flask(__name__)
app.secret_key = "UP33tx-4%"


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(message)s")
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)

setup_logger("log_app", "log_app.log")
logger_app = logging.getLogger("log_app")


@app.route("/")
def index():
    """Renders index.html for the root route

    Returns:
        str: The rendered HTML page.
    """
    return render_template("index.html")


@app.route("/feedback", methods=["POST", "GET"])
def generate_feedback():
    """Generates feedback for user input

    Returns:
        str: The rendered HTML page.
    """
    logger_app.info(f"TEST: {request.form}")
    user_input = request.form
    logger_app.info(f"USER INPUT: {user_input}")
    answer_feedback_list = []
    essay_list = []
    segmented_texts = []
    text = ""

    # RTA Task 1
    if user_input.get("topic", "0") != "0":  # 1, 2 or 3
        logger_app.info("AUFGABE 1")
        topic = user_input["topic"]
        answers = concatenated_answers()
        overview = is_answered_overview(answers)
        # dict only has one key "0"
        feedback = request_for_answer_feedback(answers, topic)["0"]
        answer_feedback_list = reformat_answer_feedback(feedback, overview)
        logger_app.info(str(request_for_answer_feedback(answers, topic)))

    # RTA Task 2
    if user_input["essay_text_input"] or user_input["essay_file_input"]:
        logger_app.info("AUFGABE 2")
        if user_input["essay_text_input"]:
            text = user_input["essay_text_input"]
        elif user_input["essay_file_input"]:
            file_input = user_input["essay_file_input"]
            text = read_file(file_input, encoding="utf-8")
        text = preprocess_newlines(text)

        # if segmentation option is selected
        if user_input.get("segmentation", "0") == "1":
            segmented_texts = []
            for essay in text.split("\n\n"):
                ds = DiscourseSegmenter(essay)
                segmented_text = ds.get_segmented_text(sep='\n')
                segmented_text = ds.convert_umlaut(segmented_text)
                segmented_texts.append(segmented_text.strip())
            text = "\n\n".join(segmented_texts)

        else:
            text = sent_split_text(text).strip()
        text = clean_pb_format(text)
        logger_app.info(f"TEXT: {text}")
        essay_dict = request_for_essay_annotation(text)
        essay_dict = replace_pb(essay_dict)
        essay_list = process_essay_annotation(essay_dict)
    # arguments can be accessed in HTML file with Jinja2
    return render_template("index.html",
                           answer_feedback_list=answer_feedback_list,
                           text=text,
                           essay_list=essay_list,
                           segmented_texts=segmented_texts,
                           **user_input)


##### TASK 1 FUNCTIONS ######

def reformat_answer_feedback(feedback, is_answered_list):
    """Reformats feedback text, so that the response to each question
    can be accessed.

    Args:
        feedback (str): The feedback containing responses to questions
            as one single string.
        is_answered_list (list): A list indicating which questions are
            answered, e.g. [1, 0, 1, 1].

    Returns:
        list: A list containing feedback for each answered question.
            Each element is a list of sentences (str).
    """
    answer_list = []
    pattern = re.compile(r"(?:In Bezug auf Frage 1:\\n(.*?))?"
                         r"(?:Zu Frage 2:\\n(.*?))?"
                         r"(?:Bzgl. Frage 3:\\n(.*?))?"
                         r"(?:Zu Frage 4:\\n(.*?))?$", re.DOTALL)
    matches = pattern.search(feedback)
    if matches:
        feedback_1 = matches.group(1).strip() if matches.group(1) else ""
        feedback_2 = matches.group(2).strip() if matches.group(2) else ""
        feedback_3 = matches.group(3).strip() if matches.group(3) else ""
        feedback_4 = matches.group(4).strip() if matches.group(4) else ""
    feedback_split = [feedback_1, feedback_2, feedback_3, feedback_4]

    for i, state in enumerate(is_answered_list, start=1):
        if state:
            answer_list.append(feedback_split.pop(0))
        else:
            if i == 2 and request.form["topic"] == "2":
                answer_list.append("Diese Frage kann mit den Informationen aus"
                                   " dem Artikel nicht behandelt werden.")
            else:
                answer_list.append("Du hast diese Frage nicht beantwortet.")

    # sentence splitter
    for i in range(len(answer_list)):
        # answer_list contains lists with each sentence as one element
        answer_list[i] = sent_tokenize(answer_list[i])
    return answer_list


def is_answered_overview(answers):
    """Determines which questions are answered based on given answers

    Args:
        answers (str): A string containing answers to multiple
            questions separated by two newline characters.

    Returns:
        list: A list of integers indicating whether each question is
            answered (1) or not (0).
    """
    answered_questions = []
    for answer in answers.split("\n\n"):
        if answer == "DUMMY":
            answered_questions.append(0)
        else:
            answered_questions.append(1)
    if request.form["topic"] == "2":  # key always exists
        answered_questions.insert(1, 0)  # list should consist of 4 elements
    return answered_questions  # e.g. [1, 0, 0, 1]


def concatenated_answers():
    """Concatenates and reformats user input from textareas

    Takes user input from textareas, removes unnecessary formatting,
    and concatenates the answers. If a textarea is empty, a default
    "DUMMY" answer is used instead.

    Returns:
        str: Concatenated and reformatted answers.
    """
    user_input = request.form
    textarea_names = ["question_1_input", "question_2_input",
                      "question_3_input", "question_4_input"]
    #  key always exists because topic selection is required
    if user_input["topic"] == "2":
        textarea_names.remove("question_2_input")
    answers = ""
    for question in textarea_names:
        # if textarea is empty, then the value is an empty string
        if user_input.get(question, ""):
            reformatted_answer = ""
            for bullet_point in user_input[question].split("\n"):
                bullet_point = bullet_point.strip('-')
                bullet_point = bullet_point.strip()
                if bullet_point:
                    reformatted_answer += bullet_point + "\n"
            if not reformatted_answer.strip():  # for example "- "
                reformatted_answer = "DUMMY\n"
        else:  # empty string
            reformatted_answer = "DUMMY\n"
        answers += reformatted_answer + "\n"
    answers = answers.strip()
    return answers


##### TASK 2 FUNCTIONS ######

def clean_pb_format(text):
    """Cleans the "<PB>" format in the given text

    Args:
        text (str): The input text that might contain invalid
            "<PB>" format.

    Returns:
        str: The cleaned text with corrected "<PB>" format.
    """
    text = text.replace("\n<PB >\n", "<PB>\n")
    text = text.replace("\n<PB>", "<PB>\n")
    text = text.replace("< PB >", "<PB>")
    return text


def preprocess_newlines(text):
    """Preprocesses the newline characters in the given text

    Args:
        text (str): The input text with newline characters.

    Returns:
        str: The text after preprocessing, ensuring consistent
            newline usage.
    """
    text = text.replace("\r\n", "\n")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text


def sent_split_text(text):
    """Splits the input text into essays and sentences

    Args:
        text (str): The input text containing essays separated by two
            newline characters.

    Returns:
        str: The text after splitting into essays and sentences.
    """
    essays = text.split("\n\n")
    sent_split = ""
    for essay in essays:
        sentences = sent_tokenize(essay)
        sent_split += "\n".join(sentences) + "\n\n"
    return sent_split


def read_file(file, encoding="utf-8"):
    """Reads and returns the content of a file

    Args:
        file (str): The path or name of the file to be read.
        encoding (str): The encoding for reading the file.
            Defaults to "utf-8".

    Returns:
        str: The content of the file.
    """
    with open(file, 'r', encoding=encoding) as read_f:
        text = ""
        for line in read_f:
            text += line
    return text


def replace_pb(essay_dict):
    """Replaces "<PB>" tags in the essay annotation dict with HTML
    line breaks

    Args:
        essay_dict (dict): A dictionary containing the essay annotation.

    Returns:
        dict: The modified essay_dict with "<PB>" tags replaced
            with HTML line breaks.
    """
    for essay in essay_dict.keys():
        for sent in essay_dict[essay]["essay_analysis"].keys():
            sent_dict = essay_dict[essay]["essay_analysis"][sent]
            if sent_dict["text"].startswith("<PB>"):
                sent_dict["tokens"]["0"] = ""
                sent_dict["tokens"]["1"] = Markup("<br>")
                sent_dict["tokens"]["2"] = ""
            if sent_dict["text"].endswith("<PB>"):
                token_index = len(sent_dict["tokens"]) - 1
                sent_dict["tokens"][str(token_index)] = ""
                sent_dict["tokens"][str(token_index - 1)] = Markup("<br>")
                sent_dict["tokens"][str(token_index - 2)] = ""
    return essay_dict


def process_essay_annotation(essay_dict):
    """Organize essay annotations into an embedded list

    Args:
        essay_dict (dict): A dictionary containing the essay annotation.

    Returns:
        list: An embedded list of essays, each represented as a list of
            sentences. Each sentence is a list of 3-string-element lists
            [token, content zone label, attribution label].
            The last element of each essay is a 3-string-tuple
            containing the feedback text.

    Example:
        [
            [
                [["Meiner", "own", "source"], ["Meinung", "own", "source"], ...],
                [["Nächster", "own", "source"], ["Satz", "own", "source"], ...], ...
                ...,
                [("Das ist ein Feedback.", "[FEEDBACK]", "")]
            ],
            [
                [["Nächster", "own", "source"]], [["Essay", "own", "source"]],...
                ...,
                [("Das ist Feedback für Essay 2.", "[FEEDBACK]", "")]
            ]
        ]
    """
    essay_list = []
    # essay key is number (str) that starts from "0"
    for essay in sorted(essay_dict.keys(), key=lambda x: int(x)):
        essay_list.append([])
        # sent key is number (str) that starts from "0"
        for sent in sorted(essay_dict[essay]["essay_analysis"].keys(),
                           key=lambda x: int(x)):
            sent_dict = essay_dict[essay]["essay_analysis"][sent]
            # sentence will be filled with tokens
            essay_list[int(essay)].append([])
            # token key is number (str) that starts from "0"
            for token in sorted(sent_dict["tokens"].keys(),
                                key=lambda x: int(x)):
                # "content_zone" key has a one-element-list as a value
                essay_list[int(essay)][int(sent)].append([
                        sent_dict["tokens"][token],
                        sent_dict["annotation"]["content_zone"][0]["label"],
                        ""
                    ])
            for attribution_span in reversed(sent_dict["annotation"]["attribution"]):
                # content_zone is the same for one sentence
                # but attribution can be different in a single sentence
                # merge tokens with same attribution:
                merged_tokens = [
                        "",
                        sent_dict["annotation"]["content_zone"][0]["label"],
                        ""
                    ]
                for i in range(attribution_span["end_token_id"],
                               attribution_span["start_token_id"] - 1,
                               -1):
                    merged_tokens[0] = (sent_dict["tokens"][str(i)]
                                        + " " + merged_tokens[0])
                    # delete single tokens without attribution that
                    # have been created in the loop before
                    del essay_list[int(essay)][int(sent)][i]
                merged_tokens[0] = merged_tokens[0].rstrip()
                merged_tokens[2] = attribution_span["label"]
                essay_list[int(essay)][int(sent)].insert(i, merged_tokens)
        essay_list[int(essay)].append([(f"Feedback: {essay_dict[essay]['feedback_text']}",
                                        "[FEEDBACK]",
                                        "")])
    return essay_list


##### SERVER REQUESTS #####

def request_for_answer_feedback(text, topic, port=5678):
    """Sends a POST-request to the specified API link to get
    feedback for the answers

    Args:
        text (str): The answers for which feedback is requested.
        topic (str): The topic number. Ranges from 1 to 3.
        port (int): The port number of the API server. Defaults to 5678.

    Returns:
        dict: A dictionary containing the feedback response.
    """
    response = requests.post(
                    f"http://localhost:{port}/api/task-1",
                    json={
                        "text": text,
                        "topic": topic
                    }
                )
    if not response.ok:
        logger_app.error("Request für Task 1 hat nicht funktioniert.")
        response.raise_for_status()
    return response.json()


def request_for_essay_annotation(text, port=5678):
    """Sends a POST-request to the specified API link to get
    annotations and feedback for the given text

    Args:
        text (str): The essays for which annotations and feedback
            is requested.
        port (int): The port number of the API server. Defaults to 5678.

    Returns:
        dict: A dictionary containing the annotation and feedback.
    """
    response = requests.post(
                    f"http://localhost:{port}/api/task-2",
                    json={
                        "text": text
                    }
                )
    if not response.ok:
        logger_app.error("Request für Task 2 hat nicht funktioniert.")
        response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    app.run(debug=True)
