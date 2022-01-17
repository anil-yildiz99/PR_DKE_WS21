from flask import jsonify
from app import db
from app.api import bp
from app.api.auth import basic_auth

''' In der folgenden View Function wird mit "...login_required" vom User verlangt, dass dieser angemeldet ist,
    sonst hat dieser keinen Zugriff auf diese View Function. Somit wird dann die "get_token()" Methode von
    dem momentan angemeldeten User aufgerufen und es wird somit ein Token generiert und in der Datenbank
    persistiert. '''
@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})

def revoke_token():
    pass
