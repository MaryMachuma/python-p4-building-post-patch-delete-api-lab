#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return "Index for Bakery API"

# GET /bakeries
@app.route('/bakeries')
def bakeries():
    bakeries = []
    for bakery in Bakery.query.all():
        bakery_dict = bakery.to_dict()
        bakeries.append(bakery_dict)

    response = make_response(
        bakeries,
        200
    )

    return response

# GET and PATCH /bakeries/<int:id>
@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id_endpoint(id):
    bakery = Bakery.query.filter(Bakery.id == id).first()

    if bakery is None:
        response_body = {
            "message": "This record does not exist in our database. Please try again."
        }
        response = make_response(response_body, 404)
        return response

    if request.method == 'GET':
        bakery_dict = bakery.to_dict()

        response = make_response(
            bakery_dict,
            200
        )

        return response

    elif request.method == 'PATCH':
        for attr in request.form:
            if attr == 'name':  # Only allow updating the name as per lab requirements
                setattr(bakery, attr, request.form.get(attr))

        db.session.add(bakery)
        db.session.commit()

        bakery_dict = bakery.to_dict()

        response = make_response(
            bakery_dict,
            200
        )

        return response

# GET and POST /baked_goods (consolidated route)
@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods_endpoint():
    if request.method == 'GET':
        baked_goods = []
        for baked_good in BakedGood.query.all():
            baked_good_dict = baked_good.to_dict()
            baked_goods.append(baked_good_dict)

        response = make_response(
            baked_goods,
            200
        )

        return response

    elif request.method == 'POST':
        try:
            new_baked_good = BakedGood(
                name=request.form.get("name"),
                price=int(request.form.get("price")),
                bakery_id=int(request.form.get("bakery_id")),
            )

            db.session.add(new_baked_good)
            db.session.commit()

            baked_good_dict = new_baked_good.to_dict()

            response = make_response(
                baked_good_dict,
                201
            )

            return response
        except (ValueError, TypeError) as e:
            response_body = {
                "message": "Invalid input data. Please ensure price and bakery_id are valid integers."
            }
            return make_response(response_body, 400)

# DELETE /baked_goods/<int:id>
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def baked_good_by_id(id):
    baked_good = BakedGood.query.filter(BakedGood.id == id).first()

    if baked_good is None:
        response_body = {
            "message": "This record does not exist in our database. Please try again."
        }
        response = make_response(response_body, 404)
        return response

    db.session.delete(baked_good)
    db.session.commit()

    response_body = {
        "delete_successful": True,
        "message": "BakedGood deleted."
    }

    response = make_response(
        response_body,
        200
    )

    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)