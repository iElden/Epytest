#!/usr/bin/env python3
from flask import Flask, request, render_template
import json
import subprocess
import shutil
import os
from execute_test import execute_test

app = Flask(__name__)
GIT_URL = "git@git.epitech.eu:/{}@epitech.eu/{}"
DELIVERY_ERROR = "DELIVERY ERROR\n\nclone returned {0.returncode}\n{0.stdout}"
BUILD_ERROR = "BUILD ERROR\n\n{}\n\n-----------------------\nCoding style:\n\n{}"
NO_ERROR = "Tests:\n\n{}\n\n-----------------------\nCoding style:\n\n{}"

with open("banned.json") as fd:
    banned = json.load(fd)

def render_main_page(result="", login="", prj=None):
    return render_template("index.html", ls_prj=os.listdir("tests/"),
                           result=result,
                           login=login, prj="Selectionnez un projet ...")
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_main_page()
    elif request.method == 'POST':
        login = request.form.get('login')
        if not login: return "Aucun login donné", 400
        login = login.split('@')[0]
        prj = request.form.get('project_name')
        if not prj : return "Aucun projet spécifié", 400
        if login in banned:
            return ('Banned', 403)
        if prj not in os.listdir('tests/'):
            return ('Test not found', 404)
        return render_main_page(login=login, prj=prj, result=test_project(login, prj))


def test_project(login, prj):
    try: os.mkdir('repo/' + login)
    except FileExistsError: pass
    try: shutil.rmtree('{}'.format('repo/' + login))
    except FileNotFoundError: pass
    # delivery
    r = subprocess.run(['git', 'clone', GIT_URL.format(login, prj), 'repo/' + login],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       timeout=10)
    if r.returncode:
        return DELIVERY_ERROR.format(r)
    # load test rule
    with open('tests/' + prj) as fd:
        js = json.load(fd)
    norminette_log = norminette('repo/' + login)
    # build
    mkrule = js.get('makerule', ['make', 're']) + ['-C', 'repo/' + login]
    r = subprocess.run(mkrule, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, timeout=10)
    if r.returncode and not js.get('ignoreBuildFail', False):
        return BUILD_ERROR.format(r.stdout, norminette_log)
    # tests
    global_settings = js['global_settings']
    tests = js['tests']
    return NO_ERROR.format('\n'.join([f'{test["name"]}: ' + execute_test(**{**global_settings, **test}, login='repo/'+login+'/') for test in tests]),
                           norminette_log)
    
def norminette(folder, whitelist=None, traceback=False):
    r = subprocess.run(['norminette', '-csvA' + (traceback and 't' or ''), '-i4', folder],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
    if r.returncode not in [0, 1] or traceback :
        return r.stdout
    else:
        return norminette(folder, whitelist=whitelist, traceback=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=42421)
