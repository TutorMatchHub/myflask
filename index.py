from flask import Flask
from flask import render_template
from flask import request
import pymysql
from pymysql import cursors

app=Flask(__name__)

@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/info')
def info():
    return render_template('a2.html')
@app.route('/GetTeacherInfo',methods=['POST'])
def TeacherInfo():
    TeacherName=request.form['keywordInput']
    connection=pymysql.connect(
        host='localhost',
        user='root',
        password='asd2895032',
        database='TeacherInfo',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor=connection.cursor()
    try:
        search_query=f'''select name,title,subject,major,research_area,type,bio,email,phone,address
                        from BasicInfo,ContactInfo
                        where name='{TeacherName}' and id=teacher_id'''
        cursor.execute(search_query)
        result=cursor.fetchone() # 假设符合要求的只有一条结果
        teacher_info={
            'name':result['name'],
            'title':result['title'],
            'subject':result['subject'],
            'major':result['major'],
            'research_area':result['research_area'],
            'type':result['type'],
            'bio':result['bio'],
            'phone':result['phone'],
            'email':result['email'],
            'address':result['address']
        }

        return teacher_info
    except Exception as e:
        print("查询错误",e)
    finally:
        cursor.close()
        connection.close()


if __name__=='__main__':
    app.run(port=3000,host='127.0.0.1')

