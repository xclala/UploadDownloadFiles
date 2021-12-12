from os import system, path, urandom, getcwd, mkdir
from flask import Flask, redirect
from flask_wtf.csrf import CSRFProtect
from waitress import serve
from argparse import ArgumentParser

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(666)
CSRFProtect(app)
parser = ArgumentParser()  #一定要在导入upload和download之前
parser.add_argument('-p', '--port', type=int)  #一定要在导入upload和download之前
parser.add_argument('-t', '--thread', type=int)  #一定要在导入upload和download之前
parser.add_argument('--upload', action="store_true")  #一定要在导入upload和download之前
parser.add_argument('--download',
                    action="store_true")  #一定要在导入upload和download之前
port = str(parser.parse_args().port)  #一定要在导入upload和download之前
threads = parser.parse_args().thread  #一定要在导入upload和download之前
if port is None:
    port = int(input("端口：（默认80端口）"))  #一定要在导入upload和download之前
if threads is None:
    threads = input("线程数：（默认4个）")  #一定要在导入upload和download之前
if parser.parse_args().upload:
    if parser.parse_args().download:
        _ = '0'  #一定要在导入upload和download之前
    else:
        _ = '1'  #一定要在导入upload和download之前
if parser.parse_args().download:
    _ = '2'  #一定要在导入upload和download之前
if not parser.parse_args().upload:
    if not parser.parse_args().download:
        _ = input("让别人上传输入 1，让别人下载输入 2，既上传又下载输入 0：")  #一定要在导入upload和download之前
if _ == '1':
    if not path.exists(path.join(getcwd(), "别人上传的文件")):
        mkdir("别人上传的文件")
    from upload import app as upload
    system("title 上传文件")

    @app.errorhandler(404)
    def notfound(_):
        return redirect("/")

    app.register_blueprint(upload)
    if port == '':
        print("在浏览器中输入您的ip地址即可上传。")
    else:
        print("在浏览器中输入您的ip地址:" + port + "即可上传。")
elif _ == '2':
    if not path.exists(path.join(getcwd(), "让别人下载的文件")):
        mkdir("让别人下载的文件")
    from download import app as download
    system("title 下载文件")
    app.register_blueprint(download)
    if port == '':
        print("在浏览器中输入您的ip地址即可下载。")
    else:
        print("在浏览器中输入您的ip地址:" + port + "即可下载。")
elif _ == '0':
    from upload import app as upload
    from download import app as download
    system("title 上传和下载文件")
    if not path.exists(path.join(getcwd(), "别人上传的文件")):
        mkdir("别人上传的文件")
    if not path.exists(path.join(getcwd(), "让别人下载的文件")):
        mkdir("让别人下载的文件")
    app.register_blueprint(upload)
    app.register_blueprint(download, url_prefix='/filelist')
    if port == '':
        print("在浏览器中输入您的ip地址即可上传和下载。")
    else:
        print("在浏览器中输入您的ip地址:" + port + "即可下载。")
if __name__ == "__main__":
    if port == '':
        if threads == '':
            serve(app, host='0.0.0.0', port=80)
        else:
            serve(app, host='0.0.0.0', port=80, threads=threads)
    else:
        if threads == '':
            serve(app, host='0.0.0.0', port=port)
        else:
            serve(app, host='0.0.0.0', port=port, threads=threads)
