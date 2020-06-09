#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import yaml
import json
import subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

export_as_json = False
template_folder = os.path.join(os.getcwd(), 'template')


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


def write_yamls(p, data):
    if export_as_json:
        p = p.replace('.yaml', '.json')
    with open(p, 'w') as f:
        if export_as_json:
            f.write(json.dumps(data, indent=1))
        else:
            f.write(yaml.dump(data, Dumper=NoAliasDumper))
        f.close()


def load_template(p):
    with open(p, 'r') as f:
        temp = json.loads(f.read())
        f.close()
    return temp


def generate_deployments(img_name, template=os.path.join(template_folder, 'deployments.json'),
                         deployments_yaml='deployments.yaml', tag='latest'):
    deployments = load_template(template)
    deployments['metadata']['name'] = img_name
    deployments['metadata']['labels']['app'] = img_name
    deployments['spec']['selector']['matchLabels']['app'] = img_name
    deployments['spec']['template']['metadata']['labels']['app'] = img_name
    deployments['spec']['template']['spec']['containers'][0]['name'] = img_name
    deployments['spec']['template']['spec']['containers'][0]['image'] = img_name if tag is None \
        else img_name + ':' + tag
    write_yamls(deployments_yaml, deployments)
    return deployments_yaml


def generate_nginx_conf(template=os.path.join(template_folder, 'nginx-config.json'),
                        nginx_config_yaml='nginx-config.yaml', nginx_conf=os.path.join(template_folder, 'nginx.conf')):
    with open(nginx_conf, 'r') as conf:
        nginx_config = load_template(template)
        nginx_config['data']['nginx.conf'] = conf.read()
        conf.close()
    write_yamls(nginx_config_yaml, nginx_config)
    return nginx_config_yaml


def generate_service(img_name, template=os.path.join(template_folder, 'service.json'),
                     service_yaml='service.yaml'):
    service = load_template(template)
    service['metadata']['name'] = img_name
    service['spec']['selector']['app'] = img_name
    write_yamls(service_yaml, service)
    return service_yaml


def generate_env_yaml(img_name, template=os.path.join(template_folder, 'env.json'),
                      env_yaml='env.yaml', app_conf=os.path.join(os.path.dirname(os.getcwd()), 'app.conf')):
    envs = load_template(template)
    envs['metadata']['name'] = img_name
    envs['metadata']['labels']['app'] = img_name
    envs['spec']['template']['spec']['containers'][0]['name'] = img_name
    variables = list()
    p = subprocess.Popen(['sh', app_conf], stdout=subprocess.PIPE)
    output = p.communicate()
    for line in output:
        if line is not None:
            string_env = line.decode('utf-8').split('\n')[0: -1]
            for kv in string_env:
                if '=' in kv:
                    key, value = kv.split('=')
                    variables.append({'name': key, 'value': value})
    envs['spec']['template']['spec']['containers'][0]['env'] = variables
    write_yamls(env_yaml, envs)
    return env_yaml


def generate_kustomization(deployments_yaml, nginx_config_yaml, service_yaml, env_yaml,
                           template=os.path.join(template_folder, 'kustomization.json'),
                           name_space='default', kustomization_yaml='kustomization.yaml'):
    kustomization = load_template(template)
    kustomization['namespace'] = name_space
    kustomization['resources'] = [deployments_yaml, nginx_config_yaml, service_yaml]
    kustomization['patchesStrategicMerge'] = [env_yaml]
    write_yamls(kustomization_yaml, kustomization)


def main():
    img_name = args.img_name
    tag = None
    if ':' in img_name:
        img_name, tag = img_name.split(':')
    deployments_yaml = generate_deployments(img_name, tag=tag)
    nginx_config_yaml = generate_nginx_conf()
    service_yaml = generate_service(img_name)
    app_conf = args.app_conf
    if app_conf is None:
        env_yaml = generate_env_yaml(img_name)
    else:
        env_yaml = generate_env_yaml(img_name, app_conf=app_conf)
    generate_kustomization(deployments_yaml, nginx_config_yaml, service_yaml, env_yaml, name_space='default')


def is_valid_file(parser, arg):
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        if os.path.isfile(arg):
            return arg
        else:
            parser.error("%s is not a file!" % arg)


def get_parser():
    try:
        parser = ArgumentParser(description=__doc__,
                                formatter_class=ArgumentDefaultsHelpFormatter)
        parser.add_argument("-i", "--repository_tag", dest="img_name", default=None, type=str, required=True,
                            help="Docker image name - [REPOSITORY:TAG]")
        parser.add_argument("-c", "--flask_app_conf", dest="app_conf", default=None,
                            type=lambda x: is_valid_file(parser, x), required=False, metavar = "FILE",
                            help="Path of Flask app environmental variable file")
        return parser
    except Exception as e:
        print('usage: generate_kustomization.py --help')
        print(e)


if __name__ == "__main__":
    args = get_parser().parse_args()
    main()
