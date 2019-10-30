# Vast.ai Connector

This script makes creating a [Vast.ai](vast.ai) instance faster and automatically
connects the instance to your local environment. The intended use is simple deployment
of [PyCharm](https://www.jetbrains.com/pycharm/) projects. 

[Vast.ai](vast.ai) is a service
that offers cheap machines with a GPU for performing 
machine learning tasks.

Using this script one can easily use PyCharm to edit and run Jupyter
notebooks on these machines. In addition to that, it also allows the user
to connect remotely to the Vast.ai instance and perform deployments from
PyCharm using SSH. 

## What the connector does

The script executes following steps:

1. Search for a machine fulfilling given criteria, such as, 
minimal number of CPU cores or minumal amount of RAM.
2. Create an instance on this machine
3. Install and start Jypyter Notebook on the instance
4. Create a SSH tunnel allowing the user to connect to Jupyter Notebook
   though selected localhost port.
5. Create a SSH tunnel allowing the user to connect to SSH trough selected
   localhost port.

Vast.ai of course allows its users to use SSH or Jupyter Notebook web
interface out of the box. The issue is that the host and port are different
every time you create a new instance. Steps 4 and 5 ensure that the host 
and port stay constant, so you don't have to change your PyCharm project settings all the 
time.

We use the official CLI application (the `vast.py` file) 
to communicate with Vast.ai and execute steps 1 and 2.

## How to use the script

*Warning: For now the script was tested only on Ubuntu 19.04 with Anaconda*

1. Clone the repository

   ```shell script
   $ git clone https://github.com/msvana/vastai-connector.git
   $ cd vastai-connector/
   ```

2. Execute the script

   ```shell script
   $ python vastai_connector.py --cpu-cores 6 --memory 16 --jupyter-port 8081
   ```
   If you are running the script for the first time, you are asked to provide
   you Vast.ai e-mail address and password.
   
   Following command line arguments are supported:
   - `--help`: displays basic information about the script and its command line arguments
   - `-c`, `--cpu-cores`: minimal number of CPU cores you need (default value: `1`)
   - `-m`, `--memory`: minimal amount of RAM in gigabytes (default value: `1`)
   - `-i`, `--image`: name of the Docker image to deploy (default value: `vastai/pytorch`)
   - `-j`, `--jupyter-port`: local port for a Jupyter notebook tunnel. You will be able to 
      access Jupyter notebook on `http://localhost:[jupyter_port]/` (default value: `8080`)
   - `-s`, `--ssh-port`: local port for tunneled SSH access. You will be able to connect to the 
      instance by executing `ssh root@localhost -p [ssh_port]` (default value: `8022`)
   - `-d`, `--disk-space`: disk space in GB to allocate on the machine (default value: `5`)
   - `--download-speed`: minimal download speed of the machine in Mbps (default value: `50`)
   - `--cuda`: requested CUDA version (default: `10.0`)
   
3. Do your work ...

4. After you are done with your work, you can destroy the server using keyboard interrupt (eg. `Ctrl+C`) 
in the script.
   
## TODO

1. Add `requirements.txt`