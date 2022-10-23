import models
from db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema
from sqlalchemy.exc import SQLAlchemyError

blue_print = Blueprint("stores", __name__, description="Operations on stores")


@blue_print.route("/store/<string:store_id>")
class Store(MethodView):
    @blue_print.response(200, StoreSchema)
    def get(self, store_id):
        """
        Get specific store
        :param store_id: int
        """
        store = models.StoreModel.query.get_or_404(store_id)
        return store

    @blue_print.response(200, StoreSchema)
    def delete(self, store_id):
        """
        Delete specific store
        :param store_id: int
        """
        store = models.StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"Message": "Item has been deleted"}, 200


@blue_print.route("/store")
class StoreList(MethodView):
    @blue_print.response(200, StoreSchema(many=True))
    def get(self):
        """
        Get all stores
        """
        return models.StoreModel.query.all()

    @blue_print.arguments(StoreSchema)
    def post(self, validated_json_data):
        """
        Add new store
        :param validated_json_data: dict
        """
        store = models.StoreModel(**validated_json_data)
        try:
            db.session.add(store)
            db.session.commit()
        except SQLAlchemyError as msg:
            return abort(500, message="Error occured while creating a new store, \n reason: %s" % msg)

        return store
