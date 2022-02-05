#!/usr/bin/env python3
#encoding: utf8

import pymysql
import json
import os
import sys

class C:
    def sql(self, s, params = None):
        with self.db.cursor() as cursor:
            cursor.execute(s, params)
            r = cursor.fetchall()
        self.db.commit()
        return r

c = None
credentials = None

def access_db():
    global credentials
    global c
    if c:
        return
    c = C()
    if credentials is None:
        folder = os.path.dirname(__file__)
        credentials = folder + "/credentials.json"
    j = json.load(open(credentials))
    c.db = pymysql.connect(host = j["host"], user = j["user"],
        passwd = j["password"], db = j["database"])
    create_db()

def exit_db():
    global c
    c.db.close()
    c = None

def create_db():
    c.sql("""CREATE TABLE IF NOT EXISTS found (inaturalistid INTEGER, place TEXT, date DATE)""")

def list_found():
    access_db()
    r = c.sql("SELECT * FROM found")
    exit_db()
    return r

def list_found_where(inaturalistid, place, date):
    access_db()
    clauses = []
    if inaturalistid: clauses += [f"inaturalistid='{inaturalistid}'"]
    if place: clauses += [f"place='{place}'"]
    if date: clauses += [f"date='{date}'"]
    where = ""
    if clauses:
        where = " WHERE " + (" AND ".join(clauses))
    r = c.sql("SELECT * FROM found" + where)
    exit_db()
    return r


def add_found(inaturalistid, place, date):
    access_db()
    r = c.sql("""
        INSERT INTO found (inaturalistid, place, date)
        VALUES (%s, %s, %s)""", (inaturalistid, place, date))
    exit_db()
    return r

def del_found(inaturalistid, place, date):
    access_db()
    r = c.sql("""
        DELETE FROM found
        WHERE inaturalistid=%s AND place=%s AND date=%s
        """, (inaturalistid, place, date))
    exit_db()
    return r

def data(r):
    taxon = r["taxon"]
    place = r["place"]
    date = r["date"]
    add_found(taxon, place, date)
    return "ok"

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        print("list")
        print("list id place date")
        print("found id place date")
        print("del id place date")
    elif sys.argv[1] == "listall":
        for r in list_found():
            print(r)
    elif sys.argv[1] == "list":
        for r in list_found_where(sys.argv[2], sys.argv[3], sys.argv[4]):
            print(r)
    elif sys.argv[1] == "found":
        add_found(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "del":
        print(del_found(sys.argv[2], sys.argv[3], sys.argv[4]))

