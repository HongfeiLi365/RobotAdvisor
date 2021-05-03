# robotadvisor
CS411 Database System Project. View your current portfolio, and use the Robot to find predict the future of your portfolio!
# Languages and Tools
 * Python
 * Flask
 * MySQL
 * Neo4j
 * Bootstrap 4


# Persistent Session for Flask on AWS EC2
I created a persistent session named 'robotadvisor' on our EC2 server
Use the following command to list all sessions.
```
tmux ls
```

Use the following command to create a new persistent session.
```
tmux new -s YOUR_SESSION_NAME
```

# Stop Flask on AWS EC2
1. Run the following command to connect to session 'robotadvisor' 
```
tmux attach -t robotadvisor  
```
2. Stop Flask by Ctrl+C

3. Press Ctrl+B, then press D, to detach from the session window

# Run Flask on AWS EC2
1. run the following commands
```
tmux attach -t robotadvisor
authbind --deep python3 run.py
```
2. Press Ctrl+B, then press D, to detach from the session window

Note that venv is not used.

If for some reason authbind throws a error, try running:
```
sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80
```

# To initialize MySQL on your own PC for testing purpose

1. Install MySQL, create user and password following prompt during installation. [Tutorial (Ubuntu)](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04)

2. Inside initialization folder, run init_user_tables.py to create user and post tables. (Change username and password in the script to whatever you set for MySQL during installation) 

3. Download data files from [Google Drive](https://drive.google.com/drive/folders/1ZbvjXqaLKyHTzSCw0lK9FEPdHQRN3_7S?usp=sharing). Put them under robotadvisor/initialization/data

4. Inside initialization folder, run dump_data.py to create prices, financials, and statistics tables. (Change username and password in the script to whatever you set for MySQL during installation) 

# To initialize Neo4j on your own PC for testing purpose
1. Install [Neo4j](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-neo4j-on-ubuntu-20-04), set username and password. Make sure that they are consistent with the ones in the initialization/load.py and initialization/loadNeo4j.py
2. Run these two scripts separately. 

First, go to the direcotry that the script is located
```
cd initialization
```
Run the script to populate the Neo4j database with stock nodes.
```
python3 load_stocks_neo4j.py
```
Run the script to cluster the stocks and assign the "label" attribute to each stock node.
```
python3 label_stocks_neo4j.py
```
3. Then the Neo4j database should be loaded with nodes of stock.

# Commands I have been using to run the robotadvisor on UIUC VM


Instructions to run
1. Create a new Virtual environment. Run: python3 -m venv /path/to/new/virtual/environment
3. Activate the new Virtual environment. source {PATH THE VIRTUAL VENV}/bin/activate
4. install everything in the "requirementsFront.txt": Use pip install -r requirementsFront.txt
5. export FLASK_APP=run.py
6. In the directory containing run.py, start the flask server with the following command
7. python3 run.py
8. App should be visible if you go to http://127.0.0.1:5000/
9. Note: this webstite is not visible to the outside. Use CTRL + C to shutdown the flask server

Visible to outside world
1. Follow steps 1 - 5 in the above section, "Instructions to run"
2. If you haven't already done so, export FLASK_APP=run.py
3. Setup port forwarding such that you can reach port 5000. Use a firewall to forward port 80 to 5000 
4. Run with: flask run --host=0.0.0.0 
5. Should see something in the terminal like this: 
 * Serving Flask app "run.py"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit) 
5. To navigate to the website, find the ipaddress of your VM, and enter that into an internet browser.

Utilizing nohup For persistent runs 
1. Follow steps 1 - 5 in the above section, "Instructions to run"
2. Setup port forwarding such that you can reach port 5000. Use a firewall to forward port 80 to 5000 
3. nohup flask run --host=0.0.0.0
4. The default log file will be located in $HOME/nohup.out.
5. If you want to redirect the output, do the following
6. nohup flask run --host=0.0.0.0 > ${PATH to LOG FILE}
7. To kill, use CTRL + C if you haven't already logged out. Otherwise, use do the following to find the PID of the process and kill it with kill -9
 * ps -ef | grep venv OR ps -ef | grep flask

ARCHIVE - old instructions. 
Source the virtual environement
 * source venv/bin/activate
For a simple run, use the following command
 * flask run --host=0.0.0.0
 * You may need to set FLASK_APP to run.py
 * This run can be killed with CTRL+C
For a persistent run
 * nohup flask run --host=0.0.0.0
 * Website should still be running, even after you log out
 * To kill this run... do the following
 * ps -ef | grep venv OR ps -ef | grep flask
 * Should look something like This
 * USER  9606     1  0 16:17 ?        00:00:00 /home/USER/robotadvisor/venv/bin/python3 /home/USER/robotadvisor/venv/bin/flask run --host=0.0.0.0
 * 9606 is this program's PID
 * kill that process with kill -9 {PID}
