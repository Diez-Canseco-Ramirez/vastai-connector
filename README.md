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

