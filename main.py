#无法上传多个文件
from os import abort, system, path, urandom, getcwd, mkdir, listdir, walk
from flask import Flask, render_template, request, session, send_file, abort
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from uuid import uuid4

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(666)
CSRFProtect(app)
port = input("端口：（默认80端口）")
h = input("需要上传文件的主机的ip地址：（0.0.0.0表示所有主机）（默认0.0.0.0）")
_ = input("让别人 上传/下载（上传输入 1，下载输入 2）")
if _ == '1':
    from getpass import getpass
    pw = getpass("密码：")
    system("title 上传文件")
    if port == '':
        print("在浏览器中输入您的ip地址即可上传。（80端口不需要输入冒号和端口）")
    else:
        print("在浏览器中输入您的ip地址:" + port + "即可上传。（80端口不需要输入冒号和端口）")
    if not path.exists(path.join(getcwd(), "别人上传的文件")):
        mkdir("别人上传的文件")

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if session.get("password") is None:
                p = request.form['passwd']
                if p == pw:
                    for f in request.files.getlist('file'):
                        session['password'] = pw
                        if path.exists("别人上传的文件/" +
                                       secure_filename(f.filename)):
                            f.save("别人上传的文件/" + uuid4().hex +
                                   path.splitext(f.filename)[1])
                        else:
                            f.save("别人上传的文件/" + secure_filename(f.filename))
                    return render_template('upload.html',
                                           alert_message="文件成功上传！")
                else:
                    return render_template('index.html',
                                           alert_message="密码错误！！！")
            else:
                for f in request.files.getlist('file'):
                    if path.exists("别人上传的文件/" + secure_filename(f.filename)):
                        f.save("别人上传的文件/" + uuid4().hex +
                               path.splitext(f.filename)[1])
                    else:
                        f.save("别人上传的文件/" + secure_filename(f.filename))
                    return render_template('upload.html',
                                           alert_message="文件成功上传！")
        else:
            return render_template('index.html')

    @app.route('/del_session', methods=['GET'])
    def delete_session():
        if request.method == 'GET':
            session.clear()
            session.pop("password", None)
            return render_template("index.html", alert_message="成功退出登录！")
elif _ == '2':

    @app.route('/', methods=['GET'])
    def file_list():
        if request.method == 'GET':
            for ___, _________, fl in walk("让别人下载的文件"):
                if fl != []:
                    return render_template("filelist.html", filelist=fl)
                else:
                    return render_template("filelist.html", filelist="")

    @app.route('/<filename>', methods=['GET'])
    def download_file(filename):
        if request.method == 'GET':
            from io import BytesIO
            from mimetypes import guess_type
            filepath = path.join("让别人下载的文件/", filename)
            if path.exists(filepath):
                if path.isfile(filepath):
                    with open(filepath, 'rb') as file_object:
                        return send_file(BytesIO(file_object.read()),
                                         mimetype=guess_type(filepath)[0])
                else:
                    abort(404)
            else:
                abort(404)


if port == '':
    if h == '':
        app.run(debug=False, port=80, host='0.0.0.0')
    else:
        app.run(debug=False, port=80, host=h)
else:
    if h == '':
        app.run(debug=False, port=port, host='0.0.0.0')
    else:
        app.run(debug=False, port=port, host=h)
