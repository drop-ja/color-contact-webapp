from flask import Flask, jsonify, abort, make_response, render_template, request
import os.path
from PIL import Image
import io
import base64
import time
import urllib.request, json
import ast


app = Flask(__name__)

# アップロード先のフォルダを指定
# UPLOAD_FOLDER = './static/image/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send',methods = ['POST'])
def posttest():
    from flask import request
    img_file = request.files['img_file']
    fileName = img_file.filename
    root, ext = os.path.splitext(fileName)
    ext = ext.lower()
    gazouketori = set([".jpg", ".jpeg", ".jpe", ".jp2", ".png", ".webp", ".bmp", ".pbm", ".pgm", ".ppm",
                      ".pxm", ".pnm",  ".sr",  ".ras", ".tiff", ".tif", ".exr", ".hdr", ".pic", ".dib"])
    if ext not in gazouketori:
        return render_template('index.html',massege = "対応してない拡張子です",color = "red")
    # print("success")

    buf = io.BytesIO()
    image = Image.open(img_file)
    image.save(buf, 'png')
    qr_b64str = base64.b64encode(buf.getvalue()).decode("utf-8")
    qr_b64data = "data:image/png;base64,{}".format(qr_b64str)

    url = "******"#APIのエンドポイント
    method = "POST"
    headers = {"Content-Type" : "application/json"}

    # PythonオブジェクトをJSONに変換する
    obj = {"image" : qr_b64data} 
    json_data = json.dumps(obj).encode("utf-8")


    # httpリクエストを準備してPOST
    rq = urllib.request.Request(url, data=json_data, method=method, headers=headers)
    with urllib.request.urlopen(rq) as response:
        print(response)
        response_body = response.read().decode("utf-8")
        print(response_body)
        print(type(response_body))

        # str = "{'名前':'太郎', '身長':'165', '体重':'60'}"
        response_body = ast.literal_eval(response_body)
        xy_ratio = response_body["xy_ratio"]
        bw_ratio = response_body["bw_ratio"]
        color = response_body["color"]
        sanpakugan = response_body["sanpakugan"]

    if sanpakugan>1:
        sapnakugan_result = "あなたは三白眼の傾向があります"
    else:
        sapnakugan_result = "あなたは三白眼の傾向がありません"

    return render_template('kekka.html', xy=xy_ratio, bw1=bw_ratio[0], bw2=bw_ratio[1], h=color[0], s=color[1], v=color[2], sanpaku=sapnakugan_result, img = qr_b64data)

@app.route('/kekka')
def kekka():
    return render_template('kekka.html')

# エラーハンドリング
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
@app.errorhandler(413)
def oversize(error):
    return render_template('index.html',massege = "画像サイズが大きすぎます",color = "red")
@app.errorhandler(400)
def nosubmit(error):
    return render_template('index.html',massege = "画像を送信してください",color = "red")
@app.errorhandler(503)
def all_error_handler(error):
     return 'InternalServerError\n', 503

if __name__ == '__main__':
    app.run()
