import functions_framework
from google.cloud import storage
from flask import Flask, send_file, jsonify, request
import tempfile
from flasgger import Swagger

# Flask app pour Swagger
app = Flask(__name__)
swagger = Swagger(app)

bucket_name = "meteo_opendata"
folder_prefix = "meteo/"

@app.route("/get_meteo_data", methods=["GET"])

@swag_from({
    'tags': ['Meteo'],
    'parameters': [
        {
            'name': 'filename',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Nom du fichier à télécharger depuis le bucket GCS (dossier meteo/)'
        }
    ],
    'responses': {
        200: {
            'description': 'Fichier téléchargé avec succès (retourné en pièce jointe)'
        },
        400: {
            'description': "Paramètre manquant"
        },
        404: {
            'description': "Fichier non trouvé"
        },
        500: {
            'description': "Erreur serveur"
        }
    }
})

def get_transport_data():
    try:
        filename = request.args.get("filename")
        if not filename:
            return jsonify({"error": "Missing 'filename' parameter"}), 400

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"{folder_prefix}{filename}")

        if not blob.exists():
            return jsonify({"error": f"File '{filename}' not found in folder 'meteo/'"}), 404

        # fichier temporaire
        tmp = tempfile.NamedTemporaryFile(delete=False)
        blob.download_to_filename(tmp.name)

        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handler Cloud Functions
@functions_framework.http
def main(request):
    return app(request.environ, start_response)

# pour test en local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

