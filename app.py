from flask import Flask, render_template, request, jsonify, make_response,Markup
from flask import send_file
import pandas as pd
from sqlalchemy import create_engine
import datetime
import pymysql
import time

global tableName 
tableName = ''


try:
    db_connection_str = 'mysql+pymysql://root:Airtel@123@localhost/CEN_db_mysql'
    db_connection = create_engine(db_connection_str)
    print("connection established")
except:
    print("Error")


app = Flask(__name__)
searchDict = dict()

def queryBuilder(tableName,word,columnName):
    
    paramDict = dict()
    if word == "noword" and columnName == "nocolumn":
        string = f'select * from {tableName}'
        paramDict =  dict()
    else:
        
        if len(word)!=0:
            searchDict[columnName] = word
        else:
            if(columnName in searchDict):
                del searchDict[columnName]

        
        string = f'select * from {tableName} Where'
        
        count = 0
        listOfKeys = searchDict.keys()
        if(len(listOfKeys)>0):
            for key,value in searchDict.items():
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
    
     
    return string, paramDict; 

        
                        
    


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
            value = value.replace('<tr>','<tr c><td>'+str(i+shape)+'</td>',1)
        
    else:
        value = "<p class='noEntry'><p>"
    return value


@app.route('/')
def index():
    df1 = pd.read_sql('select * from cenCiscoXE_Interface limit 0,1', con=db_connection )
    tableNames =  pd.read_sql('show tables', con=db_connection )
    return render_template('root.html',tableNames = tableNames['Tables_in_CEN_db_mysql'].tolist(),header=list(df1.columns))

@app.route('/table')
def table():
    
    df1 = pd.read_sql('select * from cenCiscoXE_Interface limit 0,1', con=db_connection )
    tableNames =  pd.read_sql('show tables', con=db_connection )
    

    return render_template('root.html',tableNames = tableNames['Tables_in_CEN_db_mysql'].tolist() ,header=list(df1.columns))

@app.route("/load")
def load():
    print(tableName)
    if request.args:
        mainData = request.args.get("c")
    
    print(mainData)
    data = mainData.split(",")
    column = data[0]
    word = data[1]
    counter = int(data[2])
    query,params = queryBuilder('cenCiscoXE_Interface',word,column)
    if query:
        print(f"Returning posts {counter} to {counter + 35}")
        res = make_response(jsonify(lazy(query+' limit '+str(counter)+',35;',counter,params)), 200)
    else:
        res = make_response(jsonify(lazy("select * from cenCiscoXE_Interface "+' limit '+str(counter)+',35;',counter)), 200)
    
    return res

@app.route("/selectTable")
def selectTable():
    global tableName
    if request.args:
        tableName = request.args.get("c")
    return "Table Selected ----->" + tableName
    


    
    


if __name__ == '__main__':
    app.run(use_reloader= True,debug=True,host='0.0.0.0', port=8011,threaded=True)