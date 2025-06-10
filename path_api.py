from flask import Flask, request, jsonify
import subprocess
import os
import re
import time

from py_fumen_util import disassemble, assemble, join, split as fumensplit, mirror as flip
from py_fumen_py import decode as pydecode, encode as pyencode, Field, Page

from bs4 import BeautifulSoup

import requests
from datetime import datetime, timezone
import traceback

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

LOGGING_WEBHOOK = "https://discord.com/api/webhooks/1133978189455183925/HKHuA3a2IyyZW5b7O575zzPw94YGO2vs_x7ENMhZmqrJDDuy-F88ysznSqpyIwQ-HJ2X"
ERROR_WEBHOOK = "https://discord.com/api/webhooks/1138280771199701012/HCaIdRH_W584KwoMzspKJVGfBK12NYzPBea71iBcthAf7zYk0fhp80W-3nvL5MLYdPht"

def log_to_discord(content, is_error=False):
    webhook = ERROR_WEBHOOK if is_error else LOGGING_WEBHOOK
    try:
        requests.post(webhook, json={"content": content})
    except Exception as e:
        print("Failed to log to Discord:", e)

def is_valid_fumen(fumen):
    try:
        pydecode(fumen)
        return True
    except:
        return False
    
def sanitize_string(s, max_length=500):
    s = re.sub(r'[^a-zA-Z0-9:/_\-=,+\[\]\*\!,\^]', '', s)
    return s[:max_length]

def get_kicks(game):
    kicks = "tetrio180"
    if game == "jstris": kicks = "jstris180"
    if game == "tetrio": kicks = "tetrio180"
    if game == "nokicks": kicks = "nokicks"
    if game == "srs": kicks = "srs"
    if game == "nullpomino": kicks = "nullpomino180"
    return kicks

def get_180(game):
    result = "180"
    if game == "jstris": result = "180"
    if game == "tetrio": result = "180"
    if game == "nokicks": result = "softdrop"
    if game == "srs": result = "softdrop"
    if game == "nullpomino": result = "180"
    return result

def get_discord_user_info(token):
    try:
        response = requests.get(
            "https://discord.com/api/users/@me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        response.raise_for_status()
        user = response.json()
        user_id = user.get("id", "guest")
        username = f"{user.get('username', 'guest')}"
        return user_id, username
    except:
        return "guest", "guest"


@app.route('/run', methods=['POST'])
def run_path_sfinder():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    fumen = data.get('fumen', '')
    if not is_valid_fumen(fumen):
        return jsonify({"error": "invalid fumen"}), 400
    clear_lines = data.get('clearLines', 0)
    queue = sanitize_string(data.get('queue', ''))
    game = sanitize_string(data.get('game', '')).lower()
    command_type = data.get('command', '')
    access_token = data.get('accessToken')
    # tokenType = data.get('tokenType')

    current_time = datetime.now(timezone.utc)
    request_data = dict(data)  # make a shallow copy
    request_data.pop("accessToken", None)
    request_data.pop("tokenType", None)
    request_summary = str(request_data)

    # userid = get_discord_user_id(access_token) if access_token else "guest"
    userid, username = get_discord_user_info(access_token) if access_token else ("guest", "guest")

    print(userid)
    
    user_folder = f"__userdata/{userid}"

    # Create the folder if it doesn't exist
    os.makedirs(user_folder, exist_ok=True)

    result = ""
    
    if command_type == 'path':
        if not isinstance(clear_lines, int) or clear_lines < 0:
            return jsonify({"error": "clearLines must be a non-negative integer"}), 400

        errorfile = f"__userdata/{userid}/error.txt"
        outputbase = f"__userdata/{userid}/path" #it'll go into path_unique
        outputfile = f"__userdata/{userid}/ezsfinder.txt"

        command = (
            f"java -jar sfinder.jar path "
            f"--tetfu '{fumen}' "
            f"--patterns '{queue}' "
            f"--clear {clear_lines} "
            f"-K +{get_kicks(game)} "
            f"-d {get_180(game)} "
            f"-o {outputbase} > {outputfile} 2> {errorfile}"
        )

        print(command)

        try:
            subprocess.run(command, shell=True, timeout=600, check=True)
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": f"Java process failed", "details": str(e)}), 500
        except subprocess.TimeoutExpired:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "Java process timed out"}), 504
        
        try:
            with open(outputbase + "_unique.html", 'r') as f:
                file_contents = f.read()
                soup = BeautifulSoup(file_contents, 'html.parser')
                link = soup.find('a')
                if link:
                    href = link.get('href')
                    result = href
        except FileNotFoundError:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "Output file not found"}), 500

    if command_type == 'minimals':
        if not isinstance(clear_lines, int) or clear_lines < 0:
            return jsonify({"error": "clearLines must be a non-negative integer"}), 400


        errorfile = f"__userdata/{userid}/error.txt"
        covercsv = f"__userdata/{userid}/cover.csv"
        outputfile = f"__userdata/{userid}/ezsfinder.txt"

        command = (
            f"java -jar sfinder.jar path -f csv -k pattern "
            f"--tetfu '{fumen}' "
            f"--patterns '{queue}' "
            f"--clear {clear_lines} "
            f"-K +{get_kicks(game)} "
            f"-d {get_180(game)} "
            f"-o {covercsv} > {outputfile} 2> {errorfile}"
        )

        print(command)

        try:
            subprocess.run(command, shell=True, timeout=600, check=True)
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": f"Java process failed", "details": str(e)}), 500
        except subprocess.TimeoutExpired:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "Java process timed out"}), 504
        
        command = f"npx sfinder-minimal {covercsv} > {outputfile}"

        try:
            subprocess.run(command, shell=True, timeout=600, check=True)
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": f"minimals process failed", "details": str(e)}), 500
        except subprocess.TimeoutExpired:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "minimals process timed out"}), 504

        command = f"python3 true_minimal_no_tiny.py > {outputfile}"

        try:
            subprocess.run(command, shell=True, timeout=600, check=True)
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": f"Java process failed", "details": str(e)}), 500
        except subprocess.TimeoutExpired:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "Java process timed out"}), 504
        
        minimallink = open(outputfile).read().splitlines()[1]
        result = minimallink

    if command_type == 'percent':
        errorfile = f"__userdata/{userid}/error.txt"

        command = f"java -jar sfinder.jar percent --tetfu {fumen} --patterns {queue} --clear {clear_lines} -K +{get_kicks(game)} -d {get_180(game)} -fc -1 > __userdata/{userid}/ezsfinder.txt 2> {errorfile}"

        print(command)

        try:
            subprocess.run(command, shell=True, timeout=600, check=True)
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": f"Java process failed", "details": str(e)}), 500
        except subprocess.TimeoutExpired:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "Java process timed out"}), 504
        
        output = open(f"__userdata/{userid}/ezsfinder.txt").read()
        solverate = (output[output.find("success"):output.find("success") + 20].split()[2])

        result = f"The chance of solving the setup is {solverate}."

    if command_type == 'ren':
        errorfile = f"__userdata/{userid}/error.txt"
        outputbase = f"__userdata/{userid}/ren.html"
        outputfile = f"__userdata/{userid}/ezsfinder.txt"

        command = (
            f"java -jar sfinder.jar ren "
            f"--tetfu '{fumen}' "
            f"--patterns '{queue}' "
            f"-K +{get_kicks(game)} "
            f"-d {get_180(game)} "
            f"-o {outputbase} > {outputfile} 2> {errorfile}"
        )

        print(command)

        try:
            subprocess.run(command, shell=True, timeout=600, check=True)
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": f"Java process failed", "details": str(e)}), 500
        except subprocess.TimeoutExpired:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "Java process timed out"}), 504
        
        try:
            with open(outputbase, 'r') as f:
                file_contents = f.read()
                soup = BeautifulSoup(file_contents, 'html.parser')
                # links -> result
                top_section = soup.find("section") # highest combo section
                links = top_section.find_all("a")
                link_list = [a['href'] for a in links]
                result = link_list
        except FileNotFoundError:
            error_trace = traceback.format_exc()
            logging_message = (
                f"{current_time} - {username} ({userid}) ran **ERROR** on \"The Site\":\n"
                f"`{request_summary}`\n"
                f"Error was:\n```\n{error_trace}\n```"
            )
            log_to_discord(logging_message, is_error=True)
            return jsonify({"error": "Output file not found"}), 500


    logging_message = f"{current_time} - {username} ({userid}) ran command on \"The Site\":\n`{request_summary}`"
    log_to_discord(logging_message)
    return jsonify({"result": result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)