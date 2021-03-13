# robotadvisor
CS411 Database System Project. View your current portfolio, and use the Robot to find predict the future of your portfolio!
# Languages and Tools
 * Python
 * Flask
 * MySQL
 * Neo4j
 * Bootstrap 4
 # Command I have been using to run the flaskblog

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
 * ps -ef | grep venv
 * Should look something like This
 * USER  9606     1  0 16:17 ?        00:00:00 /home/USER/robotadvisor/venv/bin/python3 /home/USER/robotadvisor/venv/bin/flask run --host=0.0.0.0
 * 9606 is this program's PID
 * kill that process with kill -9 {PID}
