#encoding=utf-8
import pymysql
import MySQLdb
if __name__=='__main__':
    #conn=pymysql.connect(host='127.0.0.1',user='feng',password='f1234',database='blog',charset='utf8')
    conn1 = MySQLdb.connect(host='127.0.0.1', user='feng', password='f1234', database='blog', charset='utf8')
    cur1=conn1.cursor()
    #cur=conn.cursor()
    #sql="select * from blog_post where ? = ?"
    sql = 'select * from blog_post where id=%(id)s'
    #sql='select * from %(asdfg)s'
    params = {'id': 2}
    #params2={'asdfg':'blog_post'}
    count = cur1.execute(sql,params)
    cur1=conn1.execute(sql,params)
    data=cur1.fetchall()
    #print(count.keys())
    print(type(count))
    print(data)
    cur1.close()
    conn1.close()

