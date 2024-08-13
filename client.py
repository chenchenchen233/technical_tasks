from flask import Flask, jsonify, json # 这个用不到，建议删除
import requests
import re
# import顺序应该是内置库在上，第三方库在下

app = Flask(__name__) # 这个用不到，建议删除
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


def parse_log(id_: int, log_text: str):
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


def parse_log_with_stacktraces(msg_id: int, log_text: str):
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
            error = {"ID": msg_id}
            timestamp, error_msg = contents[1].split(" - ")
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


def post_report():
    """

    :return:
    """
    ids = get_messages()
    errors = []
    for id_ in ids:
        message = get_message_by_id(id_)
        url = extract_url(message)
        log = get_log_file(url)
        errors.extend(parse_log_with_stacktraces(id_, log))
    try:
        response = requests.post(f"{BASE_URL}/report", json=json.dumps(errors))
        # 这里不建议把error直接打包，不然结构不清晰，建议构件一个数据结构，类似于这样：
        # {errors: [
        #    {
        #        id:1,
        #        level: ERROR,
        #        message: xxx,
        #        traceback: xxx
        #    }
        # ]}，直接把这个json report就行，也不用json.dumps
        print(response)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


if __name__ == '__main__':
    post_report()
