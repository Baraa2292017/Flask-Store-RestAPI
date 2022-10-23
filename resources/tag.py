from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
import models
from schemas import TagSchema

blue_print = Blueprint("Tags", "tag", description="Operations on tag table")


@blue_print.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blue_print.response(200, TagSchema(many=True))
    def get(self, store_id):
        """"
        Get tags that are registered within a store
        """
        store = models.StoreModel.query.get_or_404(store_id)
        # tags is a lazy dynamic which means we need to query, so we call .all(
        return store.tags.all()

    @blue_print.arguments(TagSchema)
    @blue_print.response(201, TagSchema)
    def post(self, validated_json_data, store_id):
        """
        Create a new tag and assign it to the store
        """
        # since in our TagSchema passing store_id is optional we do not wanna risk so we re-pass it
        tag = models.TagModel(store_id=store_id, **validated_json_data)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as msg:
            abort(500, message="Creating a new tag for the store has failed, reason=%s" % msg)

        return tag


@blue_print.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blue_print.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = models.ItemModel.query.get_or_404(item_id)
        tag = models.TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as msg:
            abort(500, message="Error occurred while trying to link tag with item, reason: %s" % msg)

        return tag


@blue_print.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blue_print.response(200, TagSchema)
    def get(self, tag_id):
        """
        get specific tag
        :param tag_id: int
        """
        tag = models.TagModel.query.get_or_404(tag_id)
        return tag

    @blue_print.response(202, description="Deletes a tag if no items is tagged with it.",
                         example={"message": "Tag deleted."})
    @blue_print.alt_response(404, description="Tag not found.")
    @blue_print.alt_response(400, description="Returned if the tag is assigned to one or more items, "
                                              "in this case, the tag is not deleted.")
    def delete(self, tag_id):
        tag = models.TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.deletd(tag)
            db.session.commit()
            return {"Message": "Tag deleted."}
        abort(400, message="Could not delete tag, Make sure tag is not associated with any items, then try again")
