# Client Application
## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Code Explanation](#code-explanation)


## Overview 
 This project is a client application for extracting error messages(id, error, timestamp, stack traces) and sending them to /report endpoint
## Installation
install dependencies

```
pip install -r requirements.txt
```

## usage
```
python client.py
```
## code-explanation

the main program performs the following steps:

1. **Retrieve All IDs**: It first fetches all IDs from the /messages endpoint.
2. **Fetch Message**s: For each ID, it retrieves the corresponding message from the /message/<message-id> endpoint.
3. **Extract URLs** : The program then extracts URL links from each message.
4. **Fetch Logs**: For each extracted URL, it fetches the logs and saves them to a temporary file.
5. **Parse Logs**: The logs are parsed to extract timestamps, error messages, and stack traces.
Send Report: 
6. **Send to server**: all results are sent to the /report endpoint.

There may be a potential misunderstanding regarding the inclusion of stack traces in the report. I'm uncertain whether stack traces need to be included. As a result, I wrote two versions of the log parsing function:

* ```parse_log_with_stacktraces(msg_id)``` :This version extracts stack traces.

* ```parse_log(msg_id)```: This version does not extract stack traces.





