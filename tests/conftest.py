import sys,types
try:import psycopg
except ImportError:
 p=types.ModuleType('psycopg');r=types.ModuleType('psycopg.rows');r.dict_row=object();sys.modules['psycopg']=p;sys.modules['psycopg.rows']=r
try:import psycopg_pool
except ImportError:
 p=types.ModuleType('psycopg_pool');p.ConnectionPool=object;sys.modules['psycopg_pool']=p
