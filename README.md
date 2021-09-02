# RobotAdvisor

This repository is a course project done by Hongfei Li, Haixu Leng, and Kevin Zhong for CS411 Database System @ UIUC. RobotAdvisor is a website where users can create and manage portfolios of stocks, and get machine-learning-based stock recommendations.

# What You Can Do on RobotAdvisor

### Watch our [demo video](https://youtu.be/4arxMlO9NW8) for a full tour.

- Create an account
![home](https://user-images.githubusercontent.com/26209594/131852692-cf0b48c8-abc3-4ede-9567-6923a7e5034c.jpg)

- Create a Portfolio and Get Machine Learning Recommendations
![Portfolio](https://user-images.githubusercontent.com/26209594/131852733-7726308c-6d81-44cb-a189-37f0b1954af5.jpg)

- Sort and Search Stocks by Certain Conditions
![Screening](https://user-images.githubusercontent.com/26209594/131852743-f5a65a42-3ca2-4e19-9cc3-cfc791dacbf9.jpg)

- Make a Post
![Post](https://user-images.githubusercontent.com/26209594/131852747-b1e9afa3-f808-43e4-8c0f-df084c2833a2.jpg)


# Languages and Tools
 * Python
 * Flask
 * MySQL
 * Neo4j

# Run robotadvisor on AWS EC2

## Persistent Session for Flask on AWS EC2
I created a persistent session named 'robotadvisor' on our EC2 server
Use the following command to list all sessions.
```
tmux ls
```

Use the following command to create a new persistent session.
```
tmux new -s YOUR_SESSION_NAME
```

## Stop Flask on AWS EC2
1. Run the following command to connect to session 'robotadvisor' 
```
tmux attach -t robotadvisor  
```
2. Stop Flask by Ctrl+C

3. Press Ctrl+B, then press D, to detach from the session window

## Run Flask on AWS EC2
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

# Set Up Databases
## To initialize MySQL on your own PC for testing purpose

1. Install MySQL, create user and password following prompt during installation. [Tutorial (Ubuntu)](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04)

2. Inside initialization folder, run init_user_tables.py to create user and post tables. (Change username and password in the script to whatever you set for MySQL during installation) 

3. Download data files from [Google Drive](https://drive.google.com/drive/folders/1ZbvjXqaLKyHTzSCw0lK9FEPdHQRN3_7S?usp=sharing). Put them under robotadvisor/initialization/data

4. Inside initialization folder, run dump_data.py to create prices, financials, and statistics tables. (Change username and password in the script to whatever you set for MySQL during installation) 

## To initialize Neo4j on your own PC for testing purpose
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
