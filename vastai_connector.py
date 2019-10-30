import argparse
import json
import os
import sys
import time
import warnings

warnings.filterwarnings('ignore')

BASE_PATH = os.path.dirname(__file__)
VAST_COMMAND_PATH = os.path.join(BASE_PATH + 'vast.py')
API_KEY_PATH = os.path.expanduser('~/.vast_api_key')


def main():
    argument_parser = construct_argument_parser()
    args = argument_parser.parse_args(sys.argv[1:])

    log_in()

    print('Machine criteria:')
    print('\tMin. CPU cores:\t\t%d' % args.cpu_cores)
    print('\tMin. RAM:\t\t%dGB' % args.memory)
    print('\tMin. download speed:\t%dMbps' % args.download_speed)
    print('\tDisk space:\t\t%dGB' % args.disk_space)
    print()

    top_offer = get_top_offer(args.cpu_cores, args.memory, args.download_speed, args.cuda)
    instance_id = create_instance(top_offer, args.image, args.disk_space)
    ssh_host, ssh_port = get_ssh_connection_details(instance_id)
    install_jupyter(ssh_host, ssh_port)
    start_jupyter(ssh_host, ssh_port)
    create_jupyter_tunnel(ssh_host, ssh_port, args.jupyter_port)
    create_ssh_tunnel(ssh_host, ssh_port, args.ssh_port)


def construct_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--cpu-cores', type=int, help='Minimal number of CPU cores on the machine', default=1)
    parser.add_argument(
        '-m', '--memory', type=int, help='Minimal amount of RAM in gigabytes', default=1)
    parser.add_argument(
        '-i', '--image', type=str, help='Name of the docker image to deploy',
        default='vastai/pytorch')
    parser.add_argument(
        '-j', '--jupyter-port', type=int, help='Local port for Jupyter', default=8080)
    parser.add_argument(
        '-s', '--ssh-port', type=int, help='Local port for SSH', default=8022)
    parser.add_argument(
        '-d', '--disk-space', type=int, help='Required disk space in GB', default=5)
    parser.add_argument(
        '--download-speed', type=int, help='Minimal download speed in Mb/s', default=50)
    parser.add_argument(
        '--cuda', type=float, help='Requested CUDA version', default=10.0)
    return parser


def log_in():
    if not os.path.exists(API_KEY_PATH):
        print('Please log in, so we can get the API KEY')
        os.system('python %s login' % VAST_COMMAND_PATH)


def get_top_offer(min_cpu: int, min_ram: float, min_download: int, cuda: float) -> dict:
    print('Searching for offers')
    command = "python %s search offers " \
              "'cpu_cores_effective > %d cpu_ram > %f dph > %f inet_down > %d cuda_vers = %f' --raw"
    output_buffer = os.popen(command % (
        VAST_COMMAND_PATH, min_cpu - 1, min_ram, 0.1, min_download, cuda))
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
    print('\tDown speed: %.3fMbps' % top_offer['inet_down'])
    print('\tCUDA version: %.1f' % top_offer['cuda_max_good'])
    return top_offer


def create_instance(offer: dict, docker_image: str, disk_space: int):
    print('Creating instance on machine %d' % offer['id'])
    command = 'python %s create instance %d --image %s --disk %d --raw'
    output_buffer = os.popen(command % (VAST_COMMAND_PATH, offer['id'], docker_image, disk_space))
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
    status = None

    while True:
        output_buffer = os.popen(command % VAST_COMMAND_PATH)
        instances = json.load(output_buffer)
        instance = list(filter(lambda i: i['id'] == instance_id, instances))

        if len(instance) != 1:
            raise RuntimeError('Something went wrong. Not able to find the instance')

        new_status = instance[0]['actual_status']

        if new_status != status:
            print('Status changed to "%s"' % new_status)

        status = new_status
        time.sleep(3)

        if status == 'running':
            break

    time.sleep(15)
    ssh_host = instance[0]['ssh_host']
    ssh_port = instance[0]['ssh_port']

    print('SSH host: %s\nSSH port: %d' % (ssh_host, ssh_port))
    return ssh_host, ssh_port


def install_jupyter(host, port):
    print('Installing Jupyter')
    command = 'ssh -t -p %d root@%s -o "StrictHostKeyChecking=no" ' \
              '/opt/conda/bin/pip install jupyter'
    os.system(command % (port, host))
    print('Done!')


def start_jupyter(host, port):
    print('Starting jupyter')
    command = 'ssh -t -p %d root@%s -o "StrictHostKeyChecking=no" ' \
              'PATH="$PATH:/opt/conda/bin" jupyter notebook --ip=127.0.0.1 --allow-root &'
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
