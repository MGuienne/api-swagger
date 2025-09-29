import functions_framework
from google.cloud import storage
from flask import Flask
from flask import send_file, request, jsonify
from flasgger import Swagger
import tempfile

# Création de l'app Flask manuellement
app = Flask(__name__)
swagger = Swagger(app)

@app.route("/get_transport_data", methods=["GET"])
def get_transport_data():
    try:
        filename = request.args.get("filename")
        if not filename:
            return jsonify({"error": "Missing 'filename' parameter"}), 400

        bucket_name = "transport_bucket_1"
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(filename)

        if not blob.exists():
            return jsonify({"error": f"File '{filename}' not found"}), 404

        # Download blob into a temp file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        blob.download_to_filename(tmp.name)

        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@functions_framework.http
def main(request):
    return app(request.environ, start_response=lambda *args: None)

