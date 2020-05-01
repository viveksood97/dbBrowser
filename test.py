from flask import Flask, render_template, request, jsonify, make_response,Markup
from flask import send_file
app = Flask(__name__)
@app.route('/')
def home():
   
    return render_template('test.html')



if __name__ == '__main__':
    app.run(use_reloader= True,debug=True,host='0.0.0.0', port=8011,threaded=True)