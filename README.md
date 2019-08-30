# Vast.ai connector

I wrote this script to better connect my PyCharm
workflow with [Vast.ai](vast.ai). 

Vast.ai is a service
that offers cheap machines with a GPU for performing 
machine learning tasks.

Using this script one can easily use PyCharm to edit and run Jupyter
notebooks on these machines. In addition to that, it also allows the user
to connect remotely to the Vast.ai instance and perform deployments from
PyCharm using SSH. 

(I put some of my code into Python files outsite the
Jupyter notebook and use remote deployment to upload the files to
the machine actually running the code so I can import them)

## What the connector does

The script executes following steps:

1. Search for a machine fulfilling given criteria, such as maximum price, 
mininal number of CPU cores or minumal amount of RAM.
2. Create an instance on this machine
3. Install and start Jypyter Notebook on the instance
4. Create a SSH tunnel allowing the user to connect to Jupyter Notebook
   though selected localhost port.
5. Create a SSG tunnel allowing the user to connect to SSH trough selected
   localhost port.

Vast.ai of course allows its users to use SSH or a Jupyter Notebook 
instance out of the box. The issue is, that the host and port are different
every time you create a new instance. Steps 4 and 5 ensure that the host 
and port stay constant, so you don't have to change the setting all the 
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

2. Modify the constants in `vastai_connector.py` to match your needs.
3. Execute the script

   ```shell script
   $ python vastai_connector.py
   ```
   If you are running the script for the first time, you are asked to provide
   you Vast.ai e-mail address and password.
   
4. Do your work ...

5. After you are done, you need to manually kill the SSH tunnel processes for example
   by executing:
   
   ```shell script
   $ killall ssh
   ```
   
   This will also kill all other SSH connections.
   You can then delete the your Vast.ai instance using their web interface.
   
   *This step will be changed in the future*
   
## TODO

1. Use command line arguments instead of constants to provide machine search criteria and port numbers
2. Add an infinite loop after step 5:
    The loop can be stopped by keyboard interrupt (Ctrl + C). After the loop
    is stopped, the script closes the tunnels and deletes the instance.
3. Add `requirements.txt`