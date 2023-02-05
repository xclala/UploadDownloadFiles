from flask import Flask, render_template, request, session, abort, send_file, flash, url_for
from flask_wtf.csrf import CSRFProtect
from waitress import serve
from os import path, urandom, scandir
from uuid import uuid4

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(666)
CSRFProtect(app)


def secure_filename(filename):
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    :param filename: the filename to secure
    """
    from unicodedata import normalize
    from re import compile
    import os
    _filename_ascii_strip_re = compile(r"[^A-Za-z0-9_\u4E00-\u9FBF.-]")
    _windows_device_files = (
        "CON",
        "AUX",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "LPT1",
        "LPT2",
        "LPT3",
        "PRN",
        "NUL",
    )
    filename = normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("utf-8")

    for sep in path.sep, path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(
        filename.split()))).strip("._")

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (os.name == "nt" and filename
            and filename.split(".")[0].upper() in _windows_device_files):
        filename = f"_{filename}"

    return filename

def login():
    if request.method == 'POST':
        password = app.config['password']
        if session.get("password") == password or request.form['passwd'] == password:
            if request.form['passwd'] == password:
                session['password'] = request.form['passwd']
            if app.config['mode'] == 'upload':
                return url_for('upload_view')
            elif app.config['mode'] == 'download':
                return url_for('filelist')
            else:
                ...
                #之后继续编既上传又下载的情况
        elif session.get(
                "password") != password or request.form['passwd'] != password:
            flash("密码错误！")
    return render_template('login.html')

def upload_view():
    if session.get("password") == app.config['password']:
        if request.method == 'POST':
            for f in request.files.getlist('file'):
                if secure_filename(f.filename) == "":
                    flash("请先选择文件！")
                    return render_template("upload.html")
                if path.exists("共享的文件/" + secure_filename(f.filename)):
                    f.save("共享的文件/" + uuid4().hex +
                            path.splitext(f.filename)[1])
                else:
                    f.save("共享的文件/" + secure_filename(f.filename))
            flash("文件成功上传！")
        return render_template('upload.html')
    return url_for('login')


def delete_session():
    session.clear()
    session.pop("password", None)
    flash("成功退出登录！")
    return url_for('login')


def filelist():
    if session.get("password") == app.config['password']:
        filelist = []
        for fl in scandir("共享的文件"):
            if fl.is_file():
                filelist.append(fl.name)
        return render_template("download.html", filelist=filelist)
    return url_for('login')


def download_file(filename):
    if app.config['password'] == session.get('password'):
        filepath = path.join("共享的文件/", secure_filename(filename))
        if path.exists(filepath) and path.isfile(filepath):
            return send_file(filepath)
        abort(404)
    return url_for('login')


def upload(port, thread, pw):
    app.config['password'] = pw
    app.config['mode'] = 'upload'
    app.add_url_rule('/', view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/del_session', view_func=delete_session, methods=['GET'])
    serve(app, port=port, threads=thread)


def download(port, thread, pw):
    app.config['password'] = pw
    app.config['mode'] = 'download'
    app.add_url_rule("/", view_func=login, methods=['GET', 'POST'])
    app.add_url_rule("/filelist/<filename>",
                     view_func=download_file,
                     methods=['GET'])
    app.add_url_rule('/del_session', view_func=delete_session, methods=['GET'])
    serve(app, port=port, threads=thread)


def upload_download(port, thread, pw):
    app.config['password'] = pw
    app.config['mode'] = 'upload_download'
    app.add_url_rule('/', view_func=login, methods=['GET', 'POST'])
    app.add_url_rule("/filelist/<filename>",
                    view_func=download_file,
                    methods=['GET'])
    app.add_url_rule('/del_session', view_func=delete_session, methods=['GET'])
    serve(app, port=port, threads=thread)
#upload() download() upload_download() 这3个函数之后用类重构