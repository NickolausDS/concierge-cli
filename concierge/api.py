import requests
from requests import codes
from concierge.exc import ConciergeException, LoginRequired
from concierge import DEFAULT_CONCIERGE_SERVER


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


def bag_create(remote_file_manifest, bearer_token, minid_metadata={},
               minid_test=False, minid_visible_to=('public',), bag_name='',
               bag_metadata={}, bag_ro_metadata={}, verify_remote_files=False,
               server=DEFAULT_CONCIERGE_SERVER):
    """
    :param remote_file_manifest: The BDBag remote file manifest for the bag.
    Docs can be found here:
    https://github.com/fair-research/bdbag/blob/master/doc/config.md#remote-file-manifest  # noqa
    :param bearer_token: A User Globus access token
    :param minid_metadata: Metadata to include for the minid
    :param minid_test: Create the minid as a test or real production minid
    :param minid_visible_to: Control who can view the minid
    :param bag_metadata: Optional metadata for the bdbag. Must be a dict of the
                     format:
                     {"bag_metadata": {...}, "ro_metadata": {...} }
    :param bag_ro_metadata: Research Object metadata, see BDBag docs for more info
                        on usage and file syntax:
                        https://github.com/fair-research/bdbag/tree/ro-metadata-enhancements/examples/metamanifests  # noqa
    :param verify_remote_files
    :return: Creates a BDBag from the manifest, registers it and returns
     the resulting Minid
    """
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    data = {
        'remote_file_manifest': remote_file_manifest,
        'minid_metadata': minid_metadata,
        'minid_test': minid_test,
        'minid_visible_to': minid_visible_to,
        'bag_name': bag_name if bag_name is not None else '',
        'bag_metadata': bag_metadata,
        'bag_ro_metadata': bag_ro_metadata,
        'verify_remote_files': verify_remote_files
    }
    url = '{}/api/bags/'.format(server)
    response = requests.post(url, headers=headers, json=data)
    return _concierge_response(response)

def bag_info(minids, server=DEFAULT_CONCIERGE_SERVER):
    base_url = 'https://identifiers.globus.org/'
    all_minid_info = []
    for minid in minids:
        if not minid.startswith('ark:/'):
            raise ConciergeException(code='BadInput',
                message='"{}" is not a valid minid!'.format(minid))
        all_minid_info.append(requests.get(base_url + minid).json())
    return all_minid_info


def bag_stage(minids, endpoint, bearer_token, prefix='',
              server=DEFAULT_CONCIERGE_SERVER):
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    data = {'minids': minids, 'destination_endpoint': endpoint,
            'destination_path_prefix': prefix}
    url = '{}/api/stagebag/'.format(server)
    response = requests.post(url, headers=headers, json=data)
    return _concierge_response(response)
