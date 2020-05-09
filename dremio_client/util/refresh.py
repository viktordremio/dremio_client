
import json


def refresh_vds_reflection_by_path(client, path=None):
    """
    By providing a path from VDS the reflection of that vds will be refreshed
    Script will find which pds is responsible for the reflection and
    trigger the refresh based on pds

    :param path: list ['space', 'folder', 'vds']
    """
    datasets = []
    datasets.append(client.catalog_item(cid=None, path=path))
    _refresh_by_path(client, datasets)


def _refresh_by_path(client, datasets):
    for dataset in datasets:
        response = client.graph(dataset['id'])
        _parents(client, response['parents'])


def _parents(client, parents):
    datasets = []
    for parent in parents:
        if (parent['datasetType'] == 'VIRTUAL'):
            datasets.append({"id": parent['id']})
        else:
            client.refresh_pds(client.catalog_item(cid=parent['id'], path=None)['id'])
        break
    _refresh_by_path(client, datasets)


def _reenable_reflection(client, refl_json):
    data = refl_json

    key_to_remove = ['updatedAt', 'createdAt',
                     'currentSizeBytes', 'totalSizeBytes']
    for key in key_to_remove:
        data.pop(key)

    refl_id = data['id']
    data['enabled'] = False
    data = json.dumps(data)

    # disable reflesction
    client.modify_reflection(refl_id, data)

    # get new tag version for update

    data = client.reflection(refl_id)
    #data = res.json()

    for key in key_to_remove:
        data.pop(key)
    data['enabled'] = True
    data = json.dumps(data)

    # enable reflection, will trigger an update
    print(client.modify_reflection(refl_id, data)['enabled'])


def refresh_reflections_of_one_dataset(client, path=None):
    """
    By providing a path from dataset the reflection of that dataset will be refreshed through reenable
    Enebled reflections of dataset and all reflections from derived dataset will be refreshed

    :param path: list ['space', 'folder', 'vds']
    """
    reflections = client.reflections()
    dataset_id = client.catalog_item(cid=None, path=path)['id']

    for reflection in reflections['data']:
        if dataset_id == reflection['datasetId']:
            if reflection['enabled'] == True:
                _reenable_reflection(client, reflection)
