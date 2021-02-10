from flask import Flask, jsonify, abort, make_response,render_template,url_for,request,redirect,send_file
import os.path
from imagenet import imagenet
from PIL import Image
import io
import qrcode as qr
import base64
from keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from keras.models import load_model
import json

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
with open('./model/imagenet_class_index.json',encoding="utf-8") as f:
    zisyo = json.load(f)
    zisyo = {item["en"]: item["ja"] for item in zisyo}
model = MobileNet(input_shape=(128,128,3), alpha=1.0, depth_multiplier=1, dropout=1e-3, include_top=True, weights=None, input_tensor=None, pooling=None, classes=1000)
model.load_weights("./model/kerasmobilenet.h5")
bunrui = imagenet(model)
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/send',methods = ['post'])
def posttest():
    img_file = request.files['img_file']
    fileName = img_file.filename
    root, ext = os.path.splitext(fileName)
    ext = ext.lower()
    gazouketori = set([".jpg", ".jpeg", ".jpe", ".jp2", ".png", ".webp", ".bmp", ".pbm", ".pgm", ".ppm",
                      ".pxm", ".pnm",  ".sr",  ".ras", ".tiff", ".tif", ".exr", ".hdr", ".pic", ".dib"])
    if ext not in gazouketori:
        return render_template('index.html',massege = "対応してない拡張子です",color = "red")
    print("success")
    try:
        desc, score =  bunrui.predict(img_file)
        for i in range(5):
            desc[i] = [i+1,zisyo[desc[i]],round(score[i],1)]
    except:
        return render_template('index.html',massege = "解析出来ませんでした",color = "red")
    buf = io.BytesIO()
    image = Image.open(img_file)
    image.save(buf, 'png')
    qr_b64str = base64.b64encode(buf.getvalue()).decode("utf-8")
    qr_b64data = "data:image/png;base64,{}".format(qr_b64str)
    return render_template('kekka.html',namae = desc ,img = qr_b64data)

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
