# robotadvisor
CS411 Database System Project. View your current portfolio, and use the Robot to find predict the future of your portfolio!
# Languages and Tools
 * Python
 * Flask
 * MySQL
 * Neo4j
 * Bootstrap 4
 # Commands I have been using to run the flaskblog



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
