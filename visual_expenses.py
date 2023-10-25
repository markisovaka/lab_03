import sqlite3
import matplotlib.pyplot as plt

db = sqlite3.connect('C:/Users/alexa/Desktop/finances.db', check_same_thread=False)
cursor = db.cursor()

user_id = 951495777
cursor.execute("SELECT type_id FROM 'expenses' WHERE user_id =?", (user_id,))
types = cursor.fetchall()
types = [i[0] for i in types]
types = list(set(types))

exp_labels=[]
for elem1 in types:
    cursor.execute("SELECT name FROM 'expense_types' WHERE id = ?", (elem1,))
    result = cursor.fetchone()
    exp_labels.append(result[0])

exp_values = []
for elem2 in types:
    cursor.execute("SELECT SUM(amount) FROM 'expenses' WHERE type_id = ?", (elem2,))
    result = cursor.fetchone()
    exp_values.append(result[0])

plt.style.use('ggplot')
plt.title('Диаграмма расходов')
plt.pie(exp_values, labels=exp_labels, autopct='%.2f%%', shadow=True, startangle=90)
plt.axis("equal")
plt.legend(loc='upper left')
circle = plt.Circle(xy=(0,0), radius=.75, facecolor='white')
plt.gca().add_artist(circle)
plt.show()

db.commit()
db.close()