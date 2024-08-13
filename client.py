"""
文件开头可以写类似于这样的doc string，简要描述该文件是干什么的
"""

from flask import Flask, jsonify, json  # 这个用不到，建议删除
import requests
import re
# import顺序应该是内置库在上，第三方库在下

app = Flask(__name__)  # 这个用不到，建议删除
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


def get_message_by_id(id_: int):  # id的命名，建议写成message_id
    # return的typing也建议写一下,类似于这样：
    # def get_message_by_id(message_id:int)->Dict[str,Any]:
    #    ...
    """
    get the body of message by ID
    :param id_: id
    :return: str, message
    """
    try:
        response = requests.get(f"{BASE_URL}/message/{id_}")
        return response.json()["body"]
    except requests.exceptions.RequestException as e:
        # 这样的try except 重复出现了多次，建议统一封装一下
        print("An error occurred:", e)  # 错误就打log，不建议用print
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


def get_log_file(url_log: str):  # 命名：url_log-> log_url
    """

    :param url_log:
    :return: str, log file text
    """
    try:
        response = requests.get(url_log)  #
        return response.text
        # 看server.py文件，这里拿到的应该是文件，而不是直接的text
        # 建议测试一下；如果是文件，可保存成tmp file
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


def parse_log(id_: int, log_text: str):
    """

    :param id_: ID
    :param log_text: log
    :return: str, errors
    """
    # error的结构应该是什么样？建议定义一个dataclass，类似于：
    # @dataclasses.dataclass
    # class ErrorLog:
    #    log_id:int
    #    timestamp:int
    #    error_msg:str
    #    traceback:Optional[str]
    # 这样errors的类型应该就是List[ErrorLog]
    errors = []
    lines = log_text.split("\n")  # 这里应该是readline，而不是手动分割
    for line in lines:
        contents = line.split(": ")
        if contents[0] == "ERROR":
            error = {"ID": id_}
            timestamp, error_msg = contents[1].split(",")
            error["error message"] = error_msg
            error["timestamp"] = timestamp
            # traceback 建议直接在这里顺便加到error里
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
            # 这里出现了与 parse_log一样的重复代码
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


def post_report():  # 命名：建议改成 report_log之类
    """

    :return:
    """
    ids = get_messages()
    errors = []
    for id_ in (
        ids
    ):  # id_ 这种命名风格在python中不常见，可改为_id,或者使用更有意义的名称：message_id
        message = get_message_by_id(id_)
        url = extract_url(message)
        log = get_log_file(url)
        errors.extend(parse_log_with_stacktraces(id_, log))
    try:
        response = requests.post(f"{BASE_URL}/report", json=json.dumps(errors))
        # 这里不建议把error直接json.dumps，不然结构不清晰，建议构件一个数据结构，类似于这样：
        # {errors: [
        #    {
        #        id:1,
        #        message: xxx,
        #        traceback: xxx
        #    }
        # ]}，直接把这个json report就行，也不用json.dumps
        print(response)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    post_report()
