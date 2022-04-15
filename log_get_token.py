import requests
from conf.object import TEST_USER
from conf.errors_custom import AccessTokenWasNotCreated
from simple_app import app

LOGIN_LINK = 'http://localhost:5002/login'
GET_ITEM_LINK = 'http://localhost:5002/items'
CREATE_ITEM_LINK = 'http://localhost:5002/items'


def user_login(user):
    response_ = requests.post(LOGIN_LINK, json={'username': user.username, 'password': user.password})
    access_token = response_.json().get('access_token')
    if access_token is None:
        app.logger.error('Cannot get token from login request, access_token = None')
        raise AccessTokenWasNotCreated('Cannot get token form login request, access_token = None')
    user.access_token = access_token
    return user


def create_item(item, user):
    requests.post(CREATE_ITEM_LINK, json=item,
                  headers={'Authorization': f'Bearer {user.access_token}'})


def get_item(item_id, user):
    specific_item_link = f'{GET_ITEM_LINK}/{item_id}'
    response_ = requests.get(specific_item_link,
                             headers={'Authorization': f'Bearer {user.access_token}'})
    return response_.text


if __name__ == '__main__':
    user = user_login(user=TEST_USER)
    create_item(item={'id': 1, 'name': 'First Item'}, user=user)
    item = get_item(item_id=0, user=user)
    app.logger.info(f'\nItem data: {item}')