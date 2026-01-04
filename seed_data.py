import psycopg2 
from schema import db_url

conn = psycopg2.connect(db_url)
cursor = conn.cursor()

cursor.execute(
    '''
    INSERT INTO questions (question, option1, option2, option3, option4, correct_option)
VALUES
('پایتون چیست؟', 'یک زبان برنامه‌نویسی', 'یک حیوان', 'یک سیستم‌عامل', 'یک مرورگر', 1),

('کدام گزینه نوع داده در پایتون است؟', 'Car', 'int', 'House', 'Table', 2),

('برای چاپ در پایتون از چه دستوری استفاده می‌کنیم؟', 'write()', 'echo()', 'print()', 'out()', 3),

('خروجی 2 ** 3 در پایتون چیست؟', '5', '6', '8', '9', 3),

('کدام دستور برای تعریف تابع در پایتون استفاده می‌شود؟', 'function', 'def', 'fun', 'define', 2);



    '''
)

conn.commit()
conn.close()