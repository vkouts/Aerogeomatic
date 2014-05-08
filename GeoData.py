#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import xlrd
import re
import math
import time
import os.path

def km_to_kmm(km_):
    """
      Небольшая подпрограмма для перевода километров в км+метры
    """    
    km_ = float(km_)
    km = int(km_)
    m = str(int((km_ - math.trunc(km_))*1000))
    if len(m) == 1:
       m = '00' + m
    if len(m) == 2:
       m = '0' + m
    return "%s+%s"%(str(km),m)


class Road:
    Roads = []
    """Основной объект для работы с геоданными.

      При старте, если не установлен флаг (не существует файла FirstRun.flag), вычитывает исходные данные 
      из файлов в директории ./in/
      Основные свойства:
        FirstRunFile - флаг первого запуска. Если данный файл удалить, 
           исходные данные вычитываются заново
        DB - файл БД
        ROADSFILE - текстовый файл с дампом базы дорог
        AZSFILE - исходный Excel-файл с данными по АЗС
        EXITSFILE - исходный Excel-файл с данными по съездам
      Основные методы:
        RoadList() - выводит имеющийся список кодов дорог
        RoadAZS(Rcode, Begin_km, End_km, Date) - выводит список АЗС на заданном участке
           Rcode - код дороги
           Begin_km - начальный участок
           End_km - конечный участок
           Date - актуальная дата
        RoadExits(AZSs, Begin_km, End_km, Date) - выводит список съездов АЗС на заданном участке
           AZSs - массив с заправками, полученный методом RoadAZS
           Begin_km - начальный участок
           End_km - конечный участок
           Date - актуальная дата
        RoadLength(Rcode) - возвращает длину дороги
           Rcode - код дороги
        RoadName(Rcode) - возвращает наименование дороги
        Show() - вспомагательный метод для целей тестирования

    """
    FirstRunFile = './FirstRun.flag'
    DB = './aerogeomatika.db'
    ROADSFILE = './in/roads.txt'
    AZSFILE = './in/АЗС.xls'
    EXITSFILE = './in/Съезды.xls'

    def __init__(self):
       self.conn = sqlite3.connect(self.DB,check_same_thread = False)
       self.cur = self.conn.cursor()
       if not os.path.isfile(self.FirstRunFile):
         self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Roads(
                ID INTEGER PRIMARY KEY,
                id_ INTEGER,
                road_code INTEGER,
                k_s001_1 INTEGER,
                number TEXT,
                new_road_code TEXT,
                name TEXT,
                length REAL,
                class_ INTEGER,
                inventory_date TEXT,
                remark TEXT,
                create_user_name TEXT,
                create_date_time TEXT,
                update_user_name TEXT,
                update_date_time TEXT,
                history_info TEXT,
                econ_adm_value TEXT,
                road_links TEXT,
                traffic_description TEXT,
                topo_conditions TEXT 
            )  
         """)
         self.conn.commit()
         DataPattern_ = re.compile('^\d+;.*')
         fil = open(self.ROADSFILE, 'r')
         for line in fil:
             DataPattern = DataPattern_.match(line)
             if DataPattern is not None:
                 #rawdata = line.decode('windows-1251').replace('"','').split(';')
                 rawdata = line.decode('utf-8').replace('"','').split(';')
                 row = []
                 row.append(int(rawdata[0].strip()))   # id_
                 row.append(int(rawdata[1].strip()))   # road_code
                 row.append(int(rawdata[2].strip()))   # k_s001_1
                 row.append(rawdata[3].strip())        # number
                 row.append(rawdata[4].strip())        # new_road_code
                 row.append(rawdata[5].strip())        # name
                 row.append(float(rawdata[6].strip())) # length
                 row.append(int(rawdata[7].strip()))   # class_
                 row.append(rawdata[8].strip())        # inventory_date
                 row.append(rawdata[9].strip())        # remark
                 row.append(rawdata[10].strip())       # create_user_name
                 row.append(rawdata[11].strip())       # create_date_time
                 row.append(rawdata[12].strip())       # update_user_name
                 row.append(rawdata[13].strip())       # update_date_time
                 row.append(rawdata[14].strip())       # history_info
                 row.append(rawdata[15].strip())       # econ_adm_value
                 row.append(rawdata[16].strip())       # road_links
                 row.append(rawdata[17].strip())       # traffic_description
                 row.append(rawdata[18].strip())       # topo_conditions

                 self.cur.execute('SELECT * FROM Roads WHERE id_=?',[row[0]])
                 if self.cur.fetchone() is None:
                     self.cur.execute("""
                        INSERT INTO Roads(
                            id_,
                            road_code,
                            k_s001_1,
                            number,
                            new_road_code,
                            name,
                            length,
                            class_,
                            inventory_date,
                            remark,
                            create_user_name,
                            create_date_time,
                            update_user_name,
                            update_date_time,
                            history_info,
                            econ_adm_value,
                            road_links,
                            traffic_description,
                            topo_conditions) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                     """,row)
                     self.conn.commit()

         # Тут и ниже уже будем наполнять таблицу заново для  упрощения
         self.cur.execute('DROP TABLE IF EXISTS AZS;')
         self.conn.commit()
         self.cur.execute("""
              CREATE TABLE AZS (
                 ID INTEGER PRIMARY KEY,
                 code INTEGER,
                 begin_azs REAL,
                 end_azs REAL,
                 situat TEXT,
                 data_add TEXT,
                 data_delete TEXT)
         """)
         self.conn.commit()
         workbook = xlrd.open_workbook(self.AZSFILE)
         worksheet = workbook.sheet_by_index(0)
         num_rows = worksheet.nrows - 1
         cur_row = 1
         while cur_row < num_rows+1:
             code = int(worksheet.cell_value(cur_row,0))
             begin_azs = float(worksheet.cell_value(cur_row,2))
             end_azs = float(worksheet.cell_value(cur_row,4))
             situat = worksheet.cell_value(cur_row,6).encode('utf-8').decode('utf-8')
             data_add = worksheet.cell_value(cur_row,8)
             data_delete = worksheet.cell_value(cur_row,10)
             self.cur.execute("""
                     INSERT INTO AZS (
                        code,
                        begin_azs,
                        end_azs,
                        situat,
                        data_add,
                        data_delete) VALUES (?,?,?,?,?,?)
             """,[code, begin_azs, end_azs, situat, data_add, data_delete])
             cur_row += 1  

         self.cur.execute('DROP TABLE IF EXISTS EXITS;')
         self.conn.commit()
         self.cur.execute("""
             CREATE TABLE EXITS (
                ID INTEGER PRIMARY KEY,
                code INTEGER,
                position REAL,
                transverse TEXT,
                name TEXT,
                material TEXT,
                tech_condition TEXT,
                date_add TEXT,
                date_del TEXT
             )
         """)
         self.conn.commit()

         workbook = xlrd.open_workbook(self.EXITSFILE)
         worksheet = workbook.sheet_by_index(0)
         num_rows = worksheet.nrows - 1
         cur_row = 1
         while cur_row < num_rows+1:
             code = int(worksheet.cell_value(cur_row,0))
             position = float(worksheet.cell_value(cur_row,2))
             transverse = worksheet.cell_value(cur_row,4).encode('utf-8').decode('utf-8')
             name = worksheet.cell_value(cur_row,6).encode('utf-8').decode('utf-8')
             material = worksheet.cell_value(cur_row,8).encode('utf-8').decode('utf-8')
             tech_condition = worksheet.cell_value(cur_row,10).encode('utf-8').decode('utf-8')
             date_add = worksheet.cell_value(cur_row,12)
             date_del = worksheet.cell_value(cur_row,14)
             self.cur.execute("""
                INSERT INTO EXITS (
                  code,
                  position,
                  transverse,
                  name,
                  material,
                  tech_condition,
                  date_add,
                  date_del) VALUES (?,?,?,?,?,?,?,?)""",[code, position, transverse, name, material, tech_condition, date_add, date_del])
             self.conn.commit()
             cur_row +=1
         open(self.FirstRunFile, 'a').close()


    def RoadLength(self, RCode):
        self.cur.execute("SELECT length FROM Roads WHERE road_code=?",[RCode])
        return self.cur.fetchone()[0]

    def RoadName(self, RCode):
        self.cur.execute("SELECT name FROM Roads WHERE road_code=?",[RCode])
        return self.cur.fetchone()[0]

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def Show(self):
       sql = """SELECT
                  name
                FROM
                  Roads;
       """
       self.cur.execute(sql)
       row = self.cur.fetchone()
       while row:
          print row[0]
          row = self.cur.fetchone()

    def RoadList(self):
        RoadsLst = []
        sql = 'SELECT DISTINCT road_code FROM Roads;'
        self.cur.execute(sql)
        row = self.cur.fetchone()
        while row:
           RoadsLst.append(row[0])
           row = self.cur.fetchone()
        return RoadsLst


    def RoadAZS(self, Rcode, Begin_km, End_km, Date):
        AZS = []
        if Date.strip() != '':
            Date_ = time.strptime(Date, "%d/%m/%Y")
        else:
            Date_ = ''

        self.cur.execute("""
            SELECT 
              code,begin_azs,end_azs,situat,data_add,data_delete 
            FROM AZS 
            WHERE code=? AND ((begin_azs BETWEEN ? AND ?) OR (end_azs BETWEEN ? AND ?));
        """,[Rcode, Begin_km, End_km, Begin_km, End_km])
        row = self.cur.fetchone()
        while row is not None:
            if row[4].strip() != '':
                data_add_ = time.strptime(row[4], "%d.%m.%Y %H:%M:%S")
            else:
                data_add_ = time.strptime("01.01.0001 00:00:00", "%d.%m.%Y %H:%M:%S")

            if row[5].strip() != '':
                data_delete_ = time.strptime(row[5], "%d.%m.%Y %H:%M:%S")
            else:
                data_delete_ = time.strptime("31.12.9999 23:59:59", "%d.%m.%Y %H:%M:%S")
            if Date_ != '' and (Date_>data_add_ and Date_<data_delete_): 
                AZS.append(dict(code=row[0],begin_azs=row[1], end_azs=row[2], situat=row[3], data_add=row[4], data_delete=row[5]))
            row = self.cur.fetchone()
        return AZS

    def RoadExits(self, AZSs, Begin_km, End_km, Date):
        EXITS = []
        if Date.strip() != '':
           Date_ = time.strptime(Date, "%d/%m/%Y")
        else:
           Date_ = ''

        for AZS in AZSs:
           self.cur.execute("""
              SELECT 
                  code,position,transverse,name,material,tech_condition,date_add,date_del
              FROM EXITS
              WHERE code=? AND (position BETWEEN ? AND ?);
           """,[AZS['code'],AZS['begin_azs'],AZS['end_azs']])
           row = self.cur.fetchone()
           while row is not None:
               if row[6].strip() != '':
                   data_add_ = time.strptime(row[6], "%d.%m.%Y %H:%M:%S")
               else:
                   data_add_ = time.strptime("01.01.0001 00:00:00", "%d.%m.%Y %H:%M:%S")

               if row[7].strip() != '':
                   data_delete_ = time.strptime(row[7], "%d.%m.%Y %H:%M:%S")
               else:
                   data_delete_ = time.strptime("31.12.9999 23:59:59", "%d.%m.%Y %H:%M:%S")

               if u'АЗС' in row[3] and (Date_ != '' and (Date_>data_add_ and Date_<data_delete_)):
                   EXITS.append(dict(code=row[0],position=km_to_kmm(row[1]),transverse=row[2],name=row[3],material=row[4],tech_condition=row[5],date_add=row[6],date_del=row[7]))
               row = self.cur.fetchone()
        return EXITS
        





if __name__ == '__main__':
   # Тестируем
   Road1 = Road()
   print Road1.RoadList()
   print Road1.RoadLength('6002')
   AZS1 = Road1.RoadAZS('6002',0,5,'08/05/2014')
   print Road1.RoadExits(AZS1,0,5,'08/05/2014')




