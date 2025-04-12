from flask import Flask, request, jsonify, abort
import logging
from functools import wraps

app = Flask(__name__)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Request Validation Middleware ---
def validate_json(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                logger.warning("Invalid request: Content-Type not JSON")
                abort(400, description="Request must be JSON")
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                logger.warning(f"Missing fields: {missing_fields}")
                abort(400, description=f"Missing fields: {', '.join(missing_fields)}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- IELTS Speaking Answer Endpoint ---
@app.route('/api/submit-answer', methods=['POST'])
@validate_json(['name', 'answer'])
def submit_answer():
    data = request.get_json()
    name = data['name']
    answer = data['answer']

    logger.info(f"Answer submitted | Name: {name} | Answer: {answer}")
    return jsonify({"message": f"Thank you {name}, your answer was recorded."}), 200

# --- Error Handlers ---
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"400 Error: {str(error)}")
    return jsonify({"error": "Bad Request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Error: {str(error)}")
    return jsonify({"error": "Not Found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"500 Error: {str(error)}", exc_info=True)
    return jsonify({"error": "Internal Server Error", "message": "Something went wrong."}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.exception("Unhandled Exception: %s", error)
    return jsonify({"error": "Unexpected Error", "message": "An unexpected error occurred."}), 500

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
