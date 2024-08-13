"""
This is a client application, which parses the error messages and send message id, timestamp, error, and stack trace as
results to the /report endpoint.
"""

import logging
import re

import requests

BASE_URL = "http://localhost:5000"


def send_request(url: str) -> requests.Response | None:
    """
    send request to url link, fetch data if it response
    :param url:
    :return:
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            return None
    except requests.exceptions.RequestException as e:
        logging.exception(e)
        return None


def get_messages() -> list | None:
    """
    get list of IDs from /messages endpoint
    :return: json, all IDs
    """
    response = send_request(f"{BASE_URL}/messages")
    if response:
        return response.json()
    else:
        return None


def get_message_by_id(msg_id: int) -> str | None:
    """
    get the body of message by ID
    :param msg_id:
    :return:  message
    """
    response = send_request(f"{BASE_URL}/message/{msg_id}")
    if response:
        return response.json()['body']
    else:
        return None


def extract_url(msg: str) -> str | None:
    """
    extract URL from the message
    :param msg: message to be parsed
    :return:   URL
    """
    url_format = r"http[s]?://\S+"
    match = re.search(url_format, msg)
    if match:
        return match.group(0)
    else:
        return None


def get_log_file(log_url: str):
    """

    :param log_url:
    :return:  log file text
    """
    response = send_request(log_url)
    if response:
        with open("tmp.txt", 'w') as file:
            file.writelines(response.text)


def parse_log(msg_id: int) -> list:
    """

    :param msg_id:
    :param log_text: log
    :return: errors
    """
    errors = []
    with open("tmp.txt", "r") as f:
        lines = f.read().splitlines()
    for line in lines:
        contents = line.split(": ")
        if contents[0] == "ERROR":
            error = {"ID": msg_id}
            timestamp, error_msg = contents[1].split(",")
            error["error message"] = error_msg
            error["timestamp"] = timestamp
            errors.append(error)
    return errors


def parse_log_with_stacktraces(msg_id: int) -> list:
    """
    extract error timestamp, error message from the log content
    :param msg_id:
    :return: list of errors
    """
    errors = []
    with open("tmp.txt", "r") as f:
        lines = f.read().splitlines()
    i = 0
    while i < len(lines):
        contents = lines[i].split(": ")
        if contents[0] == "ERROR":
            error = {"ID": msg_id}
            timestamp, error_msg = contents[1].split(" - ")
            error["error message"] = error_msg
            error["timestamp"] = timestamp
            i += 1
            stack_trace = ""
            while lines[i] != "":
                stack_trace += lines[i] + "\n"
                i += 1
            error["stack traces"] = stack_trace
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
        get_log_file(url)
        errors.extend(parse_log_with_stacktraces(id_))
    try:
        response = requests.post(f"{BASE_URL}/report", json={"errors": errors})
        print(response)
    except requests.exceptions.RequestException as e:
        logging.exception(e)


if __name__ == '__main__':
    post_report()
