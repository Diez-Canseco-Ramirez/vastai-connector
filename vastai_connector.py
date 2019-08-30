import json
import os
import time
import warnings

warnings.filterwarnings("ignore")

BASE_PATH = os.path.dirname(__file__)
VAST_COMMAND_PATH = os.path.join(BASE_PATH + 'vast.py')
API_KEY_PATH = os.path.expanduser('~/.vast_api_key')

# Machine search criteria
MIN_CPU = 6
MIN_RAM = 16
MAX_RATE = 0.3
IMAGE = 'pytorch/pytorch'

# Tunnel configuration
JUPYTER_PORT = 8080
SSH_TUNNEL_PORT = 8022


def main():
    log_in()
    top_offer = get_top_offer(MIN_CPU, MIN_RAM, MAX_RATE)
    instance_id = create_instance(top_offer, IMAGE)
    print('Waiting 1 minute for initialization')
    time.sleep(60)
    ssh_host, ssh_port = get_ssh_connection_details(instance_id)
    install_jupyter(ssh_host, ssh_port)
    start_jupyter(ssh_host, ssh_port)
    create_jupyter_tunnel(ssh_host, ssh_port, JUPYTER_PORT)
    create_ssh_tunnel(ssh_host, ssh_port, SSH_TUNNEL_PORT)


def log_in():
    if not os.path.exists(API_KEY_PATH):
        print('Please log in, so we can get the API KEY')
        os.system('python %s login' % VAST_COMMAND_PATH)


def get_top_offer(min_cpu: int, min_ram: float, max_rate: float) -> dict:
    print('Searching for offers')
    command = "python %s search offers 'cpu_cores_effective > %d cpu_ram > %f dph < %f dph > %f' --raw"
    output_buffer = os.popen(command % (VAST_COMMAND_PATH, min_cpu - 1, min_ram, max_rate, 0.1))
    offers = json.load(output_buffer)
    offers.sort(key=lambda o: o['dph_total'])
    top_offer = offers[0]
    print('Top offer: ')
    print('\tID: %d' % top_offer['id'])
    print('\tCPU: %s' % top_offer['cpu_name'])
    print('\tCPU cores (effective): %d' % top_offer['cpu_cores_effective'])
    print('\tCPU cores (total): %s' % top_offer['cpu_cores'])
    print('\tRAM (total): %sMB' % top_offer['cpu_ram'])
    print('\tBase price (without storage): %.3f$/h' % top_offer['dph_base'])
    return top_offer


def create_instance(offer: dict, docker_image: str):
    print('Creating instance on machine %d' % offer['id'])
    command = 'python %s create instance %d --image %s --disk 5 --raw'
    output_buffer = os.popen(command % (VAST_COMMAND_PATH, offer['id'], docker_image))
    result = json.load(output_buffer)

    if result['success']:
        print('Instance created')
        return result['new_contract']
    else:
        print('Something went wrong')
        print(result)
        return None


def get_ssh_connection_details(instance_id: int) -> tuple:
    print('Getting SSH connection details for instance %d' % instance_id)
    command = "python %s show instances --raw"
    output_buffer = os.popen(command % VAST_COMMAND_PATH)
    instances = json.load(output_buffer)
    instance = list(filter(lambda i: i['id'] == instance_id, instances))

    if len(instance) != 1:
        raise RuntimeError('Something went wrong. Not able to find the instance')

    ssh_host = instance[0]['ssh_host']
    ssh_port = instance[0]['ssh_port']

    print('SSH host: %s\nSSH port: %d' % (ssh_host, ssh_port))
    return ssh_host, ssh_port


def install_jupyter(host, port):
    print('Installing Jupyter')
    command = 'ssh -t -p %d root@%s -o "StrictHostKeyChecking=no" /opt/conda/bin/pip install jupyter'
    os.system(command % (port, host))
    print('Done!')


def start_jupyter(host, port):
    print('Starting jupyter')
    command = 'ssh -t -p %d root@%s -o "StrictHostKeyChecking=no" ' \
              '/opt/conda/bin/jupyter notebook --ip=127.0.0.1 --allow-root &'
    os.system(command % (port, host))
    print('Done!')


def create_jupyter_tunnel(host, ssh_port, jupyter_port):
    print('Opening jupyter tunnel on port %d' % jupyter_port)
    command = 'ssh -fN -p %d root@%s -L %d:localhost:8888'
    os.system(command % (ssh_port, host, jupyter_port))
    print('Done')


def create_ssh_tunnel(host, ssh_port, ssh_local_port):
    print('Opening SSH tunnel on port %d' % ssh_local_port)
    command = 'ssh -fN -p %d root@%s -L %d:localhost:22'
    os.system(command % (ssh_port, host, ssh_local_port))
    print('Done')


if __name__ == '__main__':
    main()
