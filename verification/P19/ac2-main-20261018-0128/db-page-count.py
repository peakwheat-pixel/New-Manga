import sqlite3, sys
con = sqlite3.connect(sys.argv[1]); cur = con.cursor()
row = cur.execute("select count(*) from pages p join chapters c on p.chapter_id=c.chapter_id where c.title=?", (sys.argv[2],)).fetchone()
print(row[0])
