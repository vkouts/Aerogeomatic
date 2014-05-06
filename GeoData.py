#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import xlrd
import re

class Road:
   Roads = []
   DB = './aerogeomatika.db'
   ROADSFILE = './in/roads.txt'

   def __init__(self):
      self.conn = sqlite3.connect(self.DB)
      self.cur = self.conn.cursor()
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

   def List(self):
       RoadsLst = []
       sql = 'SELECT DISTINCT road_code FROM Roads;'
       self.cur.execute(sql)
       row = self.cur.fetchone()
       while row:
          RoadsLst.append(row[0])
          row = self.cur.fetchone()
       return RoadsLst


class AZS:
   AZS = []
   AZSFILE = './in/АЗС.xls'

   def __init__(self):
      workbook = xlrd.open_workbook(self.AZSFILE)
      worksheet = workbook.sheet_by_index(0)
      num_rows = worksheet.nrows - 1
      cur_row = 1
      while cur_row < num_rows+1:
          code = int(worksheet.cell_value(cur_row,0))
          begin_azs = float(worksheet.cell_value(cur_row,2))
          end_azs = float(worksheet.cell_value(cur_row,4))
          situat = worksheet.cell_value(cur_row,6).encode('utf-8')
          data_add = worksheet.cell_value(cur_row,8)
          data_delete = worksheet.cell_value(cur_row,10)
          self.AZS.append(dict(code=code, begin_azs=begin_azs, end_azs=end_azs, situat=situat, data_add=data_add, data_delete=data_delete))
          cur_row += 1

   def Show(self):
      for im in self.AZS:
         print im['code']


class EXIT:
    EXIT = []
    EXITSFILE = './in/Съезды.xls'
    def __init__(self):
      workbook = xlrd.open_workbook(self.EXITSFILE)
      worksheet = workbook.sheet_by_index(0)
      num_rows = worksheet.nrows - 1
      cur_row = 1
      while cur_row < num_rows+1:
          code = int(worksheet.cell_value(cur_row,0))
          position = float(worksheet.cell_value(cur_row,2))
          transverse = worksheet.cell_value(cur_row,4).encode('utf-8')
          name = worksheet.cell_value(cur_row,6).encode('utf-8')
          material = worksheet.cell_value(cur_row,8).encode('utf-8')
          tech_condition = worksheet.cell_value(cur_row,10).encode('utf-8')
          date_add = worksheet.cell_value(cur_row,12)
          date_del = worksheet.cell_value(cur_row,14)
          self.EXIT.append(dict(
				code=code, 
				position=position, 
				transverse=transverse, 
				name=name, 
				material=material, 
				tech_condition=tech_condition, 
				date_add=date_add, 
				date_del=date_del))
          cur_row += 1

    def Show(self):
      for im in self.EXIT:
         print im['name']



if __name__ == '__main__':
   Road1 = Road()
   #Road1.Show()
   print Road1.List()
   #AZS1 = AZS()
   #AZS1.Show()
   #EXIT1 = EXIT()
   #EXIT1.Show()




