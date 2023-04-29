from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Product Page</h1>'

@app.route('/product/<product_id>')
def product(product_id):
    product_list = [
        ["1","ノートパソコンA","Core i5","¥68,500"],
        ["2","ノートパソコンB","AMD Ryzen 5","¥81,300"],
        ["3","ノートパソコンC","CeleronN4020","¥64,300"]
    ]
    
    for product in product_list:
        if product_id == product[0]:
            break
    return "Product Name : {0} <br> CPU : {1} <br> Price : {2}".format(product[1],product[2],product[3])
        

if __name__ == '__main__':
    app.run(debug=True)