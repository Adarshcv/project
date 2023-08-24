import psycopg2

def iud(qry, val): #to insert update and delete
    con = psycopg2.connect(host='localhost', port=5432, user='Shopping', password='password', dbname='imall')
    cmd = con.cursor()
    cmd.execute(qry, val)
    con.commit()
    cmd.execute("SELECT lastval()")
    id = cmd.fetchone()[0]
    cmd.close()
    con.close()
    return id
def dell(qry,val): #to delete
    con = psycopg2.connect(host='localhost', port=5432, user='Shopping', password='password', dbname='imall')
    cmd = con.cursor()
    cmd.execute(qry, val)
    con.commit()
    deleted_rows_count = cmd.rowcount
    print("Number of deleted rows:", deleted_rows_count)
    cmd.close()
    con.close()

def selectone(qry, val): #to select one item with condition
    con = psycopg2.connect(host='localhost', port=5432, user='Shopping', password='password', dbname='imall')
    cmd = con.cursor()
    cmd.execute(qry, val)
    res = cmd.fetchone()
    con.close()
    return res

def selectall(qry): #to select many item without condition
    con = psycopg2.connect(host='localhost', port=5432, user='Shopping', password='password', dbname='imall')
    cmd = con.cursor()
    cmd.execute(qry)
    res = cmd.fetchall()
    con.close()
    return res

def selectall2(qry, val): #to select many item with condition
    con = psycopg2.connect(host='localhost', port=5432, user='Shopping', password='password', dbname='imall')
    cmd = con.cursor()
    cmd.execute(qry, val)
    res = cmd.fetchall()
    con.close()
    return res

def update(qry, val): #to update
    con = psycopg2.connect(host='localhost', port=5432, user='Shopping', password='password', dbname='imall')
    cmd = con.cursor()
    cmd.execute(qry, val)
    con.commit()
    cmd.close()
    con.close()

