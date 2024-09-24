import mysql.connector
from mysql.connector import Error
from datetime import datetime
from functools import singledispatch

class MySQLConnection:
    _instance = None

    def __init__(self):
        if MySQLConnection._instance is not None:
            raise Exception("이 클래스는 싱글톤입니다!")
        else:
            self.connection = None
            MySQLConnection._instance = self

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def db_connect(self, host,port, database, user, password):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=host,
                    port = port,
                    database=database,
                    user=user,
                    password=password
                )
                print("MySQL 데이터베이스 연결 성공")
            self.cursor = self.connection.cursor()    
        except Error as e:
            print(f"에러: {e}")
        

    def disconnection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL 연결이 닫혔습니다.")

    def get_obstacle_by_time(self,selected_start_time,selected_end_time):
        sql= f"""
        SELECT 
            COALESCE(CAST(DrivingLog.speed AS SIGNED), 'N/A') AS speed, 
            COALESCE(EventLog.category, 'N/A') AS category,  
            COALESCE(EventLog.type, 'N/A') AS type, 
            DrivingLog.time
        FROM    
            EventLog 
        RIGHT JOIN 
            DrivingLog ON DrivingLog.time = EventLog.occurtime
        WHERE 
            DrivingLog.time > '{selected_start_time}' AND 
            DrivingLog.time < '{selected_end_time}'"""
        

        print("select_data: ", sql)
        self.cursor.execute(sql)
        obstacle_results = self.cursor.fetchall()
        return obstacle_results
    
    def get_logmessage(self, type):
        sql= f"""SELECT id FROM LogMessage where type='{type}'"""
        
        print("select_data: ", sql)
        self.cursor.execute(sql)
        get_results = self.cursor.fetchall()
        return get_results
    
    def set_eventlog(self,category,type):
        sql= """INSERT INTO EventLog (category, type, occurtime, mid)
          VALUES(%s, %s, %s,%s)"""
        occurtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = self.get_logmessage(type)
        
        for val in result:
            mid = val[0]
            

        val = (category, type, occurtime, mid)
        print("select_data: ", sql)
        self.cursor.execute(sql,val)
        self.connection.commit()

    def set_drivinglog(self,speed):
        sql= """INSERT INTO DrivingLog (speed, time)
          VALUES(%s, %s) """
        
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        val = (speed, time)
        print("select_data: ", sql)
        self.cursor.execute(sql, val)
        self.connection.commit()    


    def select_data(self, table, columns= ("*",), where = None, order = None, limit=None):
        columns_str = ', '.join(columns)

        sql = f"""
          SELECT {columns_str}
          FROM {table}
        """
        if where:
          sql += f" WHERE {where}"
        if order:
          sql += f" ORDER BY {order}"
        if limit:
          sql += f" LIMIT {limit}"

        print("select_data: ", sql)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results
    
    def insert_data(self, table, columns, params):
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(params))
        sql = f"""
          INSERT INTO {table} ({columns_str})
          VALUES ({placeholders})
        """
        print("insert_data: ",sql)
        self.cursor.execute(sql, params)
        self.connection.commit()

    def delete_data(self, table, where = None, params = None):
        sql = f"DELETE FROM {table}"

        if where:
            sql += f" WHERE {where}"

        print("delete_data: ", sql)

        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

        self.connection.commit() 

    def update_data(self, table, columns, params, where = None):
        set_clauses = [f"{column} = %s" for column in columns]
        set_clause_str = ', '.join(set_clauses)

        sql = f"UPDATE {table} SET {set_clause_str}"

        if where:
          sql += f" WHERE {where}"

        print("update_data: ", sql)
        self.cursor.execute(sql, params)

        self.connection.commit() 
# 사용 예시
#def main():
    #db = MySQLConnection.getInstance()
    #db.db_connect("192.168.0.130",3306, "deep_project", "yhc", "1234")
    #current_time = datetime.now()

    #select query
    #result = db.select_data("LogMessage",where="id='1'")
    #if result:
    #    for row in result:
    #        print(row)
    
    
   
    #db.update_data("EventLog",("type",), ("test",), where="category='장애물'")

#    db.close_connection()
#if __name__ == "__main__":
#    main()