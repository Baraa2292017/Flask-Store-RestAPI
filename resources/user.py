import models
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from schemas import UserSchema
from passlib.hash import pbkdf2_sha256
from db import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity
from blocklist import expired_tokens

blue_print = Blueprint("users", __name__, "Operations on user")


@blue_print.route("/register")
class UserRegister(MethodView):
    @blue_print.arguments(UserSchema)
    def post(self, validated_json_data):
        username = validated_json_data['username']
        hashed_password = pbkdf2_sha256.hash(validated_json_data['password'])

        user = models.UserModel(username=username, password=hashed_password)

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as msg:
            abort(500, message='Error occurred while creating a new user, reason: %s' % msg)

        return {"Message": "User has been created!"}


@blue_print.route("/user/<int:user_id>")
class User(MethodView):
    @blue_print.response(200, UserSchema, description='a user has been retrieved.')
    def get(self, user_id):
        user = models.UserModel.query.get_or_404(user_id)
        return user

    @blue_print.response(200, description="User has been deleted.")
    @blue_print.alt_response(404, description="User not found")
    def delete(self, user_id):
        user = models.UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"Message": "User has been deleted!"}


@blue_print.route("/login")
class UserLogIn(MethodView):
    @blue_print.arguments(UserSchema)
    def post(self, validated_json_data):
        username, password = validated_json_data['username'], validated_json_data['password']
        user = models.UserModel.query.filter(models.UserModel.username == username).first()
        if user and pbkdf2_sha256.verify(password, user.password):
            token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"token": token, "refresh_token": refresh_token}
        abort(401, message="Invalid username or password")


@blue_print.route("/logout")
class UserLogOut(MethodView):
    @jwt_required
    def post(self):
        jti = get_jwt()['jti']
        expired_tokens.add(jti)
        return {"message": "Logged out!"}


@blue_print.route("/refresh")
class TokenRefresh(MethodView):
    """
    API to get a refresh token, this is done to let user access some APIs without
    the need to re-login after the fresh token expires
    """

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
