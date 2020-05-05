from flask import Flask, render_template, request, jsonify, make_response,Markup,session,redirect, url_for, Response
from flask_restful import Resource, Api
from flask import send_file
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import datetime
import pymysql
import time
import json
import math
from io import BytesIO



startTime = time.time()
try:
    db_connection_str = 'mysql+pymysql://root:Airtel@123@localhost'
    db_connection = create_engine(db_connection_str)
    print("connection established")
except:
    print("Error")
endTime = time.time()
# print(pd.read_sql('select * from CEN_db_mysql.cenCiscoXE_Interface limit 0,1;', con=db_connection ))


app = Flask(__name__)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
api = Api(app)



def queryBuilder(database,tableName,word,columnName):
    
    paramDict = dict()
    # if(word):
    if word == "noword" and columnName == "nocolumn":
        string = f'select * from {database}.{tableName}'
        paramDict =  dict()
    else:
        if len(word)!=0:
            session[columnName] = word
        
        else:
            if(session.get(columnName)):
                session.pop(columnName, None)

        
        string = f'select * from {database}.{tableName} Where'
        
        count = 0
        listOfKeys = session.keys()
        if(len(listOfKeys)>0):
            for key,value in session.items():
                if(value):
                    string = string +' '+ key + "LIKE %(word"+str(count)+")s "
                    paramDict["word"+str(count)] = "%"+value+"%"
                    if count != (len(listOfKeys) - 1):
                        string = string + "AND "
                    count += 1    

                    
                else: 
                    string = ""
            
                    
        else:
            string = ""
    # else:
    #     string = f'select * from {database}.{tableName}'
    #     paramDict =  dict()
    
    return string, paramDict

def lazy(query,shape,param="none"):
    print('QUERY--->',query,param)
    if param!= "none":
        df1 = pd.read_sql(query, con=db_connection,params=param)
    else:
        df1 = pd.read_sql(query, con=db_connection )
    
    if(len(df1)):
        
        value = df1.to_html( header=False ,index=False)     #time Eater
        value = value.replace('<table border="1" class="dataframe">','')
        value = value.replace('</table>','')
        value = value.replace('</tbody>','')
        value = value.replace('<tbody>','')
        
        for i in range(df1.shape[0]):
            value = value.replace('<tr>','<tr c><td class="index">'+str(i+shape)+'</td>',1)
        
    else:
        value = "<p class='noEntry'><p>"
    return value

@app.route('/')
def index():
    session.clear()
    return render_template('root.html')

@app.route('/database')
def database():
    
    if request.args:
        databaseName = request.args.get("c")
    tableNames =  pd.read_sql('show tables in '+databaseName, con=db_connection )
    tableNamesList = tableNames.to_json()
    res = make_response(tableNamesList, 200)
    return res
    
@app.route('/tableHeaders')
def tableHeaders():
    session.clear()
    if request.args:
        mainData = request.args.get("c")
    data = mainData.split(",")
    database = data[0] 
    table = data[1]
   
    headers =  pd.read_sql('select * from '+database+'.'+table+' limit 0,1;', con=db_connection )
    headers1 = list(headers.columns)
    res = make_response(json.dumps(headers1), 200)
    return res

@app.route("/load")
def load():
    if request.args:
        mainData = request.args.get("c")
    data = mainData.split(",")
    database = data[0] 
    table = data[1]
    column = data[2]
    word = data[3]
    counter = int(data[4])
    query,params = queryBuilder(database,table,word,column)
    # session["query"] = [query,params]
    if query:
        print(f"Returning posts {counter} to {counter + 35}")
        res = make_response(jsonify(lazy(query+' limit '+str(counter)+',35;',counter,params)), 200)
    else:
        res = make_response(jsonify(lazy(f"select * from {database}.{table} "+' limit '+str(counter)+',35;',counter)), 200)
    
    return res
    

@app.route('/downloadFile')
def downloadFile():
    if request.args:
        mainData = request.args.get("c")
    
    # else:
    data = mainData.split(",")
    database = data[0] 
    table = data[1]
    column = data[2]
    word = data[3]
    query,params = queryBuilder(database,table,word,column)
    # query = "select * from CEN_db_mysql.cenCiscoXE_Interface limit 0,1;"
    # params = "none"
    
    startTime = time.time()
    if(not query):
        query = f"select * from {database}.{table};"
    if params!= "none":
        df1 = pd.read_sql(query, con=db_connection,params=params)
    else:
        df1 = pd.read_sql(query, con=db_connection )

        # def generate():
    #     for ele in x:
    #        yield ','.join(ele.split())  + '\n'
    # return Response(generate(), mimetype='text/csv')
    buffer = BytesIO()
    buffer.write(df1.to_csv().encode('utf-8'))
    buffer.seek(0)

    return send_file(buffer,mimetype='text/csv',attachment_filename='report.csv',as_attachment=True)
    


    

@app.route('/tableInfo')
def tableInfo():
    if request.args:
        mainData = request.args.get("c")
    # startTime = time.time()
    
    data = mainData.split(",")
    database = data[0] 
    table = data[1]
    
    rows = pd.read_sql(f'select count(*) from {database}.{table}', con=db_connection)['count(*)'].iloc[0]
    size = pd.read_sql(f'SELECT table_name AS `Table`, round(((data_length + index_length) / 1024 / 1024)*4, 2) `Size in MB` FROM information_schema.TABLES WHERE table_schema = "{database}"    AND table_name = "{table}";', con=db_connection)['Size in MB'].iloc[0]
    # endTime = time.time()
    # print(endTime-startTime)
    return str(f"{rows}/{size}")
    
    
class fetch(Resource):
    def get(self, database, table):
        df = pd.read_sql(f"select * from {database}.{table} limit 0,100", con=db_connection )
        return df.to_json(orient='split')

api.add_resource(fetch, '/fetch/<database>/<table>')
        
    
    

    #return Response(df1, mimetype='text/csv',headers={'Content-Disposition': f'attachment; filename={"report.csv"}'})
    



if __name__ == '__main__':
    app.run(use_reloader= True,debug=True,host='0.0.0.0', port=8011,threaded=True)