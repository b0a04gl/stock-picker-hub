from flask import Flask, request, jsonify, render_template

from service import DataService

app = Flask(__name__)

data_service = DataService(redis_host='localhost', redis_port=6379, redis_db=0)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/screener/list', methods=['GET'])
def list_screeners():
    try:

        stock_data = data_service.retrieve_screeners()

        return jsonify({"success": True, "data": stock_data.to_dict(orient='records')})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)})


@app.route('/screener/retrieve', methods=['GET'])
def get_screener():
    try:
        screener_id = request.args.get('screener_id')

        stock_data = data_service.retrieve_data_for_screener(screener_id)

        return jsonify({"success": True, "data": stock_data.to_dict(orient='records')})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)})


@app.route('/screener/create', methods=['POST'])
def create_screener():
    try:
        request_data = request.get_json()
        conditions = request_data['conditions']
        screener_id = data_service.store_screen(conditions)

        stock_data = data_service.retrieve_data_for_screener(screener_id)

        return jsonify({"success": True, "data": stock_data.to_dict(orient='records')})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
