import json
import os
import requests
import yaml

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_text

try:
    import display
except ImportError:
    from ansible.utils.display import Display

    display = Display()

_valid_lookup_args = ['section', 'enumerate']


class LookupModule(LookupBase):
    """
    Main class
    """

    def run(self, terms, variables=None, **kwargs):
        # terraform_state = TerraformState(self)

        ret = []
        assets = []
        artifacts = []
        module_paths = []

        for term in terms:
            lookupfile = self.find_file_in_search_path(variables, 'files', term)

            try:
                if lookupfile:
                    b_contents, _ = self._loader._get_file_contents(lookupfile)

                    contents = to_text(b_contents, errors='surrogate_or_strict')
                    contents_json = json.loads(contents)

            except AnsibleParserError:
                raise AnsibleError("could not locate file in lookup: {}".format(term))

            try:
                # Build module paths
                module_path_lists = enumerate_assets(contents_json['modules'], 'path')
                module_paths = enumerate_module_paths(module_path_lists)

                print("KWARGS", kwargs)

                enumerate_action = None
                if 'enumerate' in kwargs:
                    enumerate_action = 'enumerate'

                if 'enumerate_with_path' in kwargs:
                    enumerate_action = 'enumerate_with_path'

                if 'enumerate_attributes' in kwargs:
                    enumerate_action = 'enumerate_attributes'

                # Just return the json of statefile
                if 'section' not in kwargs:
                    artifacts = contents_json
                    return artifacts

                # Process option to return specific sections
                if 'section' in kwargs:
                    assets = contents_json[kwargs['section']]

                # if not any(k in kwargs for k in ('enumerate', 'enumerate_with_path')):
                if enumerate_action is None:
                    artifacts = assets
                    return artifacts

                if enumerate_action == 'enumerate':
                    # Just return path list dict if path type is specified
                    if kwargs['enumerate'] == 'path':
                        print(type(module_paths))
                        return [module_paths]


                if enumerate_action == 'enumerate':
                    artifacts = enumerate_assets(assets, kwargs['enumerate'])
                    return artifacts


                # Enumerate sections with module paths
                if enumerate_action == 'enumerate_with_path':
                    asset_enumerations = enumerate_assets(assets, kwargs['enumerate_with_path'])

                    for path, asset in list(zip(module_paths, asset_enumerations)):
                        artifacts.append({'path': path, kwargs['enumerate_with_path']: asset})
                    return artifacts


                # Enumerate sections attributes
                if enumerate_action == 'enumerate_attributes':
                    asset_enumerations = enumerate_assets(assets, kwargs['enumerate_attributes'])

                    asset_attributes_list = enumerate_attributes(module_paths, asset_enumerations,
                                                                 kwargs['enumerate_attributes'])

                    # artifacts.append({'path': path, kwargs['enumerate_with_path']: asset})
                    return [asset_attributes_list]

                else:
                    raise AnsibleParserError("Some parse error")

            except Exception:
                raise
                # raise Exception("Error in handling enumerate actions")

        return artifacts


def enumerate_assets(modules_list, enumerate_key):
    """
    Function to enumerate assets objects in a list and return an identifier attribute for each
    """
    module_objects = []
    for module in modules_list:
        module_objects.append({enumerate_key: module[enumerate_key]})
    return module_objects


def enumerate_module_paths(module_path_lists):
    """
    Function to enumerate paths for each module in statefile and build a path for each
    :param module_path_lists:
    :return:
    """
    module_paths = []
    for paths in module_path_lists:
        module_path_groups = paths['path']
        module_paths.append('.'.join(module_path_groups))
    return module_paths


def enumerate_attributes(module_path_lists, modules_list, enumerate_key):
    """
    Function to enumerate paths for each module in statefile and build a path for each
    :param modules_list:
    :param enumerate_key:
    :param module_path_lists:
    :return:
    """
    asset_resources = []

    for path, asset in list(zip(module_path_lists, modules_list)):

        if enumerate_key == 'resources':
            selected_resources = list(asset['resources'].keys())
            for resource in selected_resources:
                asset_resources.append({
                    'path': path,
                    'resource': resource,
                    'resource_attributes': asset['resources'][resource]
                })

        if enumerate_key == 'outputs':
            selected_outputs = list(asset['outputs'].keys())
            for output in selected_outputs:
                asset_resources.append({
                    'path': path,
                    'output': output,
                    'output_attributes': asset['outputs'][output]
                })

    return asset_resources


def parse_enumerations(enumerate_key):
    if enumerate_key == 'path':
        pass
