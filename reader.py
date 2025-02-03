import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
from functools import wraps
import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3 as sql
import sys
from datetime import datetime

con = None
con = sql.connect('data.db',check_same_thread=False)
db = con.cursor()

with open("./parts.csv", 'r') as file:
  csvreader = csv.reader(file)
  for row in csvreader:
    db.execute('INSERT INTO parts (description, code, cost) VALUES (?,?,?);',(row[1],row[0],row[2]))
    con.commit()