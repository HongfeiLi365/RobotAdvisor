import sqlite3 as dbapi

class stocksDataBase:
    '''
    create the database drafted by Hongfei
    Table 1:
    Users(id TEXT, email TEXT, password TEXT, PRIMARY KEY(id))

    Table 2:
    Portafolio(name TEXT, id TEXT, PRIMARY KEY(name))

    Table 3:
    Contains(portafolio TEXT, stock TEXT)
    BCNF?

    Table 4:
    Stocks(date TEXT, symbol TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL, PRIMARY KEY(date, symbol))
    '''

    def __init__(self):
        self.con = dbapi.connect('stocks.db')
        self.cur = self.con.cursor()
        try:
            self.cur.execute('CREATE TABLE Users(id TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL, PRIMARY KEY(id))')
            self.cur.execute('CREATE TABLE Portafolio(name TEXT NOT NULL, id TEXT NOT NULL, PRIMARY KEY(name))')
            self.cur.execute('CREATE TABLE Contains(portafolio TEXT NOT NULL, stock TEXT NOT NULL)')
            self.cur.execute('CREATE TABLE Stocks(date TEXT, symbol TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL, PRIMARY KEY(date, symbol))')
            self.con.commit()
        except:
            print('Tables are created, no need to do anything.')

    def insertUser(self, id, email, password):
        '''
        insert into Table Users(id TEXT, email TEXT, password TEXT, PRIMARY KEY(id))
        '''
        command = 'INSERT INTO Users VALUES("%s", "%s", "%s")'%(id, email, password)
        try:
            self.cur.execute(command)
            self.con.commit()
        except:
            print("Tuple exists!")

    def insertPortafolio(self, name, id):
        '''
        insert into Table Portafolio(name TEXT, id TEXT, PRIMARY KEY(name))
        foreign key reference from this id to Users.id will be added
        '''
        command = 'INSERT INTO Portafolio VALUES("%s", "%s")'%(name, id)
        try:
            self.cur.execute(command)
            self.con.commit()
        except:
            print("Tuple exists!")

    def showAllUsers(self):
        '''
        display all users
        '''
        self.cur.execute('SELECT * FROM Users')
        print(self.cur.fetchall())

    def showAllPortafolio(self):
        '''
        display all portafolio
        '''
        self.cur.execute('SELECT * FROM Portafolio')
        print(self.cur.fetchall())

    def showAllUsersAndPortafolio(self):
        '''
        display natural join of users and portafolio
        '''
        self.cur.execute('SELECT * FROM Users NATURAL JOIN Portafolio')
        for item in self.cur.fetchall():
            print(item)

if __name__ == "__main__":
    print("This is a test.")
    sdb = stocksDataBase()
    sdb.insertUser('haixul2', 'haixul2@gmail.com', '123456')
    sdb.insertUser('haixul1', 'haixul1@gmail.com', '123456')
    sdb.insertPortafolio('401k', 'haixul1')
    sdb.insertPortafolio('roth', 'haixul1')
    sdb.insertPortafolio('tech', 'haixul2')
    sdb.showAllUsersAndPortafolio()