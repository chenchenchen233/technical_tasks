from flask import Flask, jsonify, json
import requests
import re

app = Flask(__name__)
BASE_URL = "http://localhost:5000"


def get_messages():
    """
    get list of IDs from /messages endpoint
    :return: json, all IDs
    """
    try:
        response = requests.get(f"{BASE_URL}/messages")
        return response.json()
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None




def get_message_by_id(id_: int):
    """
    get the body of message by ID
    :param id_: id
    :return: str, message
    """
    try:
        response = requests.get(f"{BASE_URL}/message/{id_}")
        return response.json()['body']
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


def extract_url(msg: str):
    """
    extract URL from the message
    :param msg: message to be parsed
    :return:  str, URL
    """
    url_format = r"http[s]?://\S+"
    match = re.search(url_format, msg)
    if match:
        return match.group(0)
    else:
        return None


def get_log_file(url_log: str):
    """

    :param url_log:
    :return: str, log file text
    """
    try:
        response = requests.get(url_log)
        return response.text
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


def parse_log(id_:int, log_text:str):
    """

    :param id_: ID
    :param log_text: log
    :return: str, errors
    """
    errors = []
    lines = log_text.split("\n")
    for line in lines:
        contents = line.split(": ")
        if contents[0] == "ERROR":
            error = {"ID": id_}
            timestamp, error_msg = contents[1].split(",")
            error["error message"] = error_msg
            error["timestamp"] = timestamp
            errors.append(error)
    return errors

def parse_log_with_tracestack(id_: int, log_text: str):
    """
    extract error timestamp, error message from the log content
    :param log_text:
    :return: list of errors
    """
    errors = []
    lines = log_text.split("\n")
    i = 0
    while i < len(lines):
        contents = lines[i].split(": ")
        if contents[0] == "ERROR":
            error = {"ID": id_}
            timestamp, error_msg = contents[1].split(",")
            error["error message"] = error_msg
            error["timestamp"] = timestamp
            i += 1
            trace_stack = ""
            while lines[i] != "":
                trace_stack += lines[i] + "\n"
                i += 1
            error["trace stack"] = trace_stack
            errors.append(error)
        else:
            i += 1
            continue
    return errors


@app.route('/report', methods=['GET'])
def get_report():
    """

    :return:
    """
    ids = get_messages()
    errors = []
    for id_ in ids:
        message = get_message_by_id(id_)
        url = extract_url(message)
        log = get_log_file(url)
        errors.extend(parse_log(id_, log))
    return json.dumps(errors)


if __name__ == '__main__':
    app.run(port=5001, debug=True)
