import requests
from requests import codes
from concierge.exc import ConciergeException, LoginRequired


def _concierge_response(response):
    try:
        rjson = response.json()
    except ValueError:
        raise ConciergeException(message='')
    err_code = rjson.get('code', '')
    messages = ','.join(
        ['{}: {}'.format(k, ','.join(v) if isinstance(v, list) else v)
         for k, v in rjson.items() if k != 'code'])

    err_map = {
        codes.BAD_REQUEST: ConciergeException(code=err_code, message=messages),
        codes.UNAUTHORIZED: LoginRequired(),
        codes.SERVER_ERROR: ConciergeException(code=err_code, message=messages)
    }
    concern = err_map.get(response.status_code)
    if concern:
        raise concern
    elif response.status_code in [codes.ALL_GOOD, codes.ACCEPTED,
                                  codes.CREATED]:
        return rjson
    else:
        raise ConciergeException(**rjson)


def create_bag(server, remote_file_manifest, name, email, title, bearer_token,
               metadata={}):
    """
    :param remote_file_manifest: The BDBag remote file manifest for the bag.
    Docs can be found here:
    https://github.com/fair-research/bdbag/blob/master/doc/config.md#remote-file-manifest  # noqa
    :param name: The name that will be under on the Minid Service
    :param email: The email that will be used (Must be a
                    globus-linked-identity)
    :param title: The title of the minid
    :param bearer_token: A User Globus access token
    :param metadata: Optional metadata for the bdbag. Must be a dict of the
                     format:
                     {"bag_metadata": {...}, "ro_metadata": {...} }
    :return: Creates a BDBag from the manifest, registers it and returns
     the resulting Minid
    """
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    data = {
      'minid_user': name, 'minid_email': email, 'minid_title': title,
      'remote_files_manifest': remote_file_manifest, 'metadata': metadata
    }
    url = '{}/api/bags/'.format(server)
    response = requests.post(url, headers=headers, json=data)
    return _concierge_response(response)


def update_bag():
    pass


def get_bag():
    pass
