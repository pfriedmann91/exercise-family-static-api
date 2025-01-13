"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def get_all_members():
        members = jackson_family.get_all_members()
        if not members: 
            return jsonify ({"error": "not found"}), 404
        return jsonify(members), 200

@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
        member= jackson_family.get_member(member_id)
        if member:
            return jsonify(member), 200
        return jsonify ({"error": "not found"}), 404

@app.route('/member', methods=['POST'])
def add_member():
    try:
        new_member = request.get_json()
        if not new_member or not all(key in new_member for key in ["id", "first_name", "age", "lucky_numbers"]):
            raise ValueError("Faltan datos. Se requieren 'id', 'first_name', 'age' y 'lucky_numbers'.")

        if not isinstance(new_member["id"], int):
            raise TypeError("id debe ser un número entero.")

        if not isinstance(new_member["first_name"], str):
            raise TypeError("first_name debe ser un texto.")

        if not isinstance(new_member["age"], int) or new_member["age"] <= 0:
            raise ValueError("age debe ser un número entero positivo.")

        if not isinstance(new_member["lucky_numbers"], list) or not all(isinstance(num, int) for num in new_member["lucky_numbers"]):
            raise TypeError("lucky_numbers debe ser una lista de números enteros.")

        jackson_family.add_member(new_member)
        return jsonify({"message": "miembro agregado"}), 200

    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": "error del servidor.", "detalle": str(e)}), 500



@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    deleted = jackson_family.delete_member(member_id)
    if deleted:
        return jsonify({"eliminado": True}), 200
    return jsonify({"error": "not found"}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
