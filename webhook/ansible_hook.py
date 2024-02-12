from flask import Flask
import subprocess

HTTP_METHODS = ['GET', 'POST']

app = Flask(__name__)

def run_command():
    return subprocess.Popen("echo 'cd ~/Picture_Classify_Hub && ansible-playbook ./ansible/playfile/main.yml' > /usr/pipe", shell=True, stdout=subprocess.PIPE).stdout.read()

@app.route('/', methods=['GET'])
def index():
    return "Running!"

@app.route('/webhook', methods=['GET'])
def webhook_listener():
    rez = run_command()
    return rez


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
