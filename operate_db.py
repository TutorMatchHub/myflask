import pymysql
import re
import json

class Query:
    def Create_DB(self,DB_name):#创建数据库
        return f"CREATE DATABASE IF NOT EXISTS {DB_name}"

    def Drop_DB(self,DB_name):#删除数据库
        return f"drop DATABASE {DB_name}"

    def Use_DB(self,DB_name):#使用/进入数据库
        return f"USE {DB_name}"

    def Create_table(self,table_name,attrs):#创建表
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({attrs})"

    def Drop_table(self,table_name):#删除表
        return f"drop {table_name}"

    def Insert(self,table_name,attrs,values):#插入
        return f"INSERT INTO {table_name} ({attrs}) VALUES {values}"

    def Search(self,obj,table_name):#查询
        return f"SELECT {obj} FROM {table_name}"



def CreateRelation(table_name,attr_name):
    query =Query()
    connection=pymysql.connect(
        host="localhost",
        user="root",
        password="asd2895032"
    )

    try:
        #新建数据库TeacherInfo
        with connection.cursor() as cursor:
            #create_DB_query= query.Create_DB("TeacherInfo")
            cursor.execute(query.Create_DB("TeacherInfo"))

        #重新连接到新创建的数据库
        connection.select_db("TeacherInfo")

        #新建表：基本信息，联系方式
        with connection.cursor() as cursor:
            cursor.execute(query.Create_table(table_name,attr_name))

        #提交事务
        connection.commit()

    finally:
        #关闭连接
        connection.close()

def getTeacherInfo(filepath,filename):
    dict_basic={}
    dict_contact={}
    with open (filepath+'\\'+filename,'r',encoding="utf-8") as file:
        # 逐行读取文件
        for line in file:
            # 去除行末的换行符
            line = line.strip()
            if line=="":
                continue
            # 使用冒号分割每行的键值对
            separator_pattern=r'[:：]'
            tmp_key,tmp_value=re.split(separator_pattern, line, maxsplit=1)

            key=re.sub(r'\s+','',tmp_key)
            value=re.sub(r'\s+','',tmp_value)

            #保存键值对信息
            if key=="姓名" or key=="职称" or key=="学科" or key=="专业" or key=="研究方向" or key=="导师类型" or key=="个人简介":
                if key=="个人简介":
                    value1=value
                    for pattern in [r'<.*?>.*?</.*?>',r'<.*?>']:
                        value=re.sub(pattern,'',value1)
                        value1=value

                dict_basic[key]=value
            elif key=="联系电话" or key=="电子邮件" or key=="通讯地址" :
                dict_contact[key]=value

    return dict_basic,dict_contact

def getTeacherName(filepath,filename):
    with open(filepath + "\\" + filename, 'r', encoding='utf-8') as file:
        first_line = file.readline()
        tmp_name = first_line.replace("姓名:", '')
        teacher_name = tmp_name.replace('\n', '')
    return teacher_name

def getCNKIinfo(Tname):
    #得到导师名字，合作作者名字及学校
    dict_tutor={}#导师信息
    dict_coauthor={}#合作作者信息

    try:
        with open("CNKIdata"+"\\"+f'{Tname}.txt','r',encoding='utf-8') as file:
            for line in file:
                # 去除行末的换行符
                line = line.strip()
                if line == "":
                    continue
                # 使用冒号分割每行的键值对
                separator_pattern = r'[:：]'
                tmp_key, tmp_value = re.split(separator_pattern, line, maxsplit=1)

                key = re.sub(r'\s+', '', tmp_key)
                value = re.sub(r'\s+', '', tmp_value)

                if key=='姓名' or key=='学校' or key=='导师':
                    if value=="未找到相关数据":
                        value=''
                    dict_tutor[key]=value

                elif key=='合作作者':
                    lines=file.readlines()
                    for li in lines:
                        li=li.strip()
                        key,value=re.split(' ',li,maxsplit=1)
                        dict_coauthor[key]=value#key:名字，value:学校

        return dict_tutor,dict_coauthor
    except:
        return {},{}


def InsertRecord():
    query = Query()

    attr_name='''id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            title VARCHAR(255) NULl,
            subject VARCHAR(255),
            major VARCHAR(255),
            research_area VARCHAR(255),
            type VARCHAR(255) NULL,
            bio TEXT
            '''
    table_name="BasicInfo"
    CreateRelation(table_name,attr_name)#创建BasicInfo表

    attr_name='''teacher_id INT,
            phone VARCHAR(255) NULL,
            email VARCHAR(255) NULL,
            address VARCHAR(255) NULL,
            FOREIGN KEY (teacher_id) REFERENCES BasicInfo(id)
            '''
    table_name="ContactInfo"
    CreateRelation(table_name,attr_name)#创建ContactInfo表

    connection = pymysql.connect(#与mysql连接
        host="localhost",
        user="root",
        password="asd2895032",
        database="TeacherInfo"
    )
    cursor=connection.cursor()

    # 执行删除所有记录的语句,调试期间
    try:
        cursor.execute("ALTER TABLE ContactInfo DROP FOREIGN KEY contactinfo_ibfk_1")
        cursor.execute("DELETE FROM BasicInfo")
        cursor.execute("DELETE FROM ContactInfo")
        cursor.execute("ALTER TABLE BasicInfo AUTO_INCREMENT = 1;")
        cursor.execute('''ALTER TABLE ContactInfo 
                        ADD CONSTRAINT contactinfo_ibfk_1 
                        FOREIGN KEY (teacher_id) 
                        REFERENCES BasicInfo(id);''')
        connection.commit()
        print("All records deleted successfully.")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    #获取教师信息
    dict_basic={}
    dict_contact={}

    for i in range(1,107):
        dict_basic.clear()
        dict_contact.clear()
        dict_basic,dict_contact=getTeacherInfo("jiaoshou",f"output{i}.txt")#得到信息

        basic_attrs="name,title,subject,major,research_area,type,bio"#basic属性
        basic_value=tuple(dict_basic.values())#basic值
        cursor.execute(query.Insert("BasicInfo",basic_attrs,basic_value))#插入basic表

        teacher_id=cursor.lastrowid#获得刚刚插入的basic的id

        contact_attrs = "teacher_id,phone,email,address"  # contact属性
        tmp_value = tuple(dict_contact.values())  # contact值
        contact_value=(teacher_id,)+tmp_value
        cursor.execute(query.Insert("ContactInfo",contact_attrs,contact_value))#插入contact表

        connection.commit()#提交事务


    for i in range(1,75):
        dict_basic.clear()
        dict_contact.clear()
        dict_basic, dict_contact = getTeacherInfo("fjs", f"output{i}.txt")  # 得到信息

        basic_attrs = "name,title,subject,major,research_area,type,bio"  # basic属性
        basic_value = tuple(dict_basic.values())  # basic值
        cursor.execute(query.Insert("BasicInfo", basic_attrs, basic_value))  # 插入basic表

        teacher_id = cursor.lastrowid  # 获得刚刚插入的basic的id

        contact_attrs = "teacher_id,phone,email,address"  # contact属性
        tmp_value = tuple(dict_contact.values())  # contact值
        contact_value = (teacher_id,) + tmp_value
        cursor.execute(query.Insert("ContactInfo", contact_attrs, contact_value))  # 插入contact表

        connection.commit()  # 提交事务

    for i in range(1,16):
        dict_basic.clear()
        dict_contact.clear()
        dict_basic, dict_contact = getTeacherInfo("js+jf+szgl", f"output{i}.txt")  # 得到信息

        basic_attrs = "name,title,subject,major,research_area,type,bio"  # basic属性
        basic_value = tuple(dict_basic.values())  # basic值
        cursor.execute(query.Insert("BasicInfo", basic_attrs, basic_value))  # 插入basic表

        teacher_id = cursor.lastrowid  # 获得刚刚插入的basic的id

        contact_attrs = "teacher_id,phone,email,address"  # contact属性
        tmp_value = tuple(dict_contact.values())  # contact值
        contact_value = (teacher_id,) + tmp_value
        cursor.execute(query.Insert("ContactInfo", contact_attrs, contact_value))  # 插入contact表

        connection.commit()  # 提交事务

    cursor.close()
    connection.close()

def Insert_CNKIrecord():
    #得到老师名字
    Tnames=[]
    for i in range(1,107):
        Tnames.append(getTeacherName("jiaoshou",f'output{i}.txt'))
    for i in range(1,75):
        Tnames.append(getTeacherName("fjs",f'output{i}.txt'))
    for i in range(1,16):
        Tnames.append(getTeacherName("js+jf+szgl",f'output{i}.txt'))

    #建立表格
    query=Query()
    attr_name = '''id INT AUTO_INCREMENT PRIMARY KEY,
               name VARCHAR(255),school VARCHAR(255) NULl,tutor VARCHAR(255)
               '''
    table_name = "TutorInfo"
    CreateRelation(table_name, attr_name)  # 创建TutorInfo表

    attr_name = '''teacher_id INT,co_author TEXT,
                 FOREIGN KEY (teacher_id) REFERENCES TutorInfo(id)
                 '''
    table_name = "CoauthInfo"
    CreateRelation(table_name, attr_name)  # 创建ContactInfo表

    #插入数据
    connection = pymysql.connect( # 与mysql连接
        host="localhost",
        user="root",
        password="asd2895032",
        database="TeacherInfo"
    )
    cursor = connection.cursor()

    # 执行删除所有记录的语句,调试期间
    try:
        cursor.execute("DELETE FROM CoauthInfo")
        cursor.execute("DELETE FROM TutorInfo")
        cursor.execute("ALTER TABLE TutorInfo AUTO_INCREMENT = 1;")
        connection.commit()
        print("All records deleted successfully.")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    # 得到CNKI信息
    dict_tutor = {}
    dict_coauthor = {}
    for Tname in Tnames:
        if dict_tutor!={} and dict_coauthor!={}:
            dict_tutor.clear()
            dict_coauthor.clear()

        dict_tutor, dict_coauthor = getCNKIinfo(Tname)

        if dict_tutor== {} or dict_coauthor== {}:
            continue

        tutor_attr="name,school,tutor"
        tutor_value=tuple(dict_tutor.values())
        cursor.execute(query.Insert("TutorInfo",tutor_attr,tutor_value))

        teacher_id=cursor.lastrowid
        coauth_attr="teacher_id,co_author"
        str_coauth=';'.join([str(key)+":"+str(value) for key,value in dict_coauthor.items()])
        coauth_value=(teacher_id,str_coauth)
        cursor.execute(query.Insert("CoauthInfo",coauth_attr,coauth_value))

        connection.commit()

    cursor.close()
    connection.close()


def ShowAllRecord(table_name):
    connection = pymysql.connect(  # 与mysql连接
        host="localhost",
        user="root",
        password="asd2895032",
        database="TeacherInfo"
    )
    cursor = connection.cursor()

    query=Query()
    cursor.execute(query.Search('*',table_name))
    res=cursor.fetchall()
    for r in res:
        print(r)

    connection.commit()

    cursor.close()
    connection.close()


if __name__=="__main__":
    #InsertRecord()
    #Insert_CNKIrecord()

    ShowAllRecord("BasicInfo")
    ShowAllRecord("ContactInfo")

