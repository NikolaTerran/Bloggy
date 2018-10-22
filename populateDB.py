#Contains functions to populate the database


import sqlite3   #enable control of an sqlite database

DB_FILE="blogs.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops


#info is a list of fieldValues in order without primary key
def insert(tableName, info):
    # collect Column Data Types and Names in strings
    c.execute('PRAGMA TABLE_INFO({})'.format(tableName))
    colNames = ''
    colTypes = ''
    i = 0
    for cols in c.fetchall():
        if i == 0:
            i += 1 # primary key will update itself
        else:
            colNames += cols[1] + ','
            colTypes += cols[2] + ','
    colNames = colNames[:-1]
    colTypes = colTypes[:-1]
    print(colNames)
    print(colTypes)
    values = ''
    j = 0
    listTypes = colTypes.split(',')
    for val in info:
        print(listTypes[j])
        print(val)
        if listTypes[j] == "INTEGER":
            values += str(val) + ","
        else:
            values += "'" + val + "'" + ","
        j += 1
    values = values[:-1]
    c.execute("INSERT INTO {0}({1}) VALUES ({2})".format(tableName,
                                                          colNames ,
                                                          values  ))
    db.commit()



def findInfo(tableName,value,index):
        c.execute("PRAGMA TABLE_INFO({})".format(tableName))
        listNames = []
        for cols in c.fetchall():
            listNames.append(cols[1])
        print(listNames[index])
        command = "SELECT * FROM  '{0}'  WHERE {1} = '{2}'".format(tableName,listNames[index],value)
        print(command)
        c.execute(command)
        listInfo = []
        info = c.fetchone()
        for col in info:
            print(col)
            listInfo.append(col)
        print(listInfo)
        return listInfo

##insert('blogs', [1, '1,2,3', 'blog1', 'food'])
