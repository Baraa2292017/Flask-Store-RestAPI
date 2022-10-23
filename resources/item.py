import models
from db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

blue_print = Blueprint("items", __name__, description="Operations on items")


@blue_print.route("/item/<string:item_id>")
class Item(MethodView):
    @jwt_required()
    @blue_print.response(200, ItemSchema)
    def get(self, item_id):
        """
        Get specific item
        :param item_id: int
        """
        item = models.ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    @blue_print.response(200, ItemSchema)
    def delete(self, item_id):
        """
        delete an item
        :param item_id: int
        """
        item = models.ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"Message": "Item has been deleted"}, 200

    @jwt_required()
    @blue_print.arguments(ItemUpdateSchema)
    @blue_print.response(200, ItemSchema)
    def put(self, validated_json_data, item_id):
        """
        Update item price or name
        :param validated_json_data: dict - the validated json data done by marshmallow library
        :param item_id: int
        """
        item = models.ItemModel.query.get(item_id)
        if item:
            item.price = validated_json_data['price']
            item.name = validated_json_data['name']
        else:
            item = models.ItemModel(id=item_id, **validated_json_data)
        db.session.add(item)
        db.session.commit()

        return item


@blue_print.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blue_print.response(200, ItemSchema(many=True))
    def get(self):
        """
        Get all items
        """
        return models.ItemModel.query.all()

    @jwt_required(fresh=True)
    @blue_print.arguments(ItemSchema)
    @blue_print.response(200, ItemSchema)
    def post(self, validated_json_data):
        """
        Add new item
        :param validated_json_data: dict - the validated json data done by marshmallow library
        """
        item = models.ItemModel(**validated_json_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as msg:
            print(msg)
            abort(500, message='Error occured while trying to create new item in post')

        return item
