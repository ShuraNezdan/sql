import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_db():
    """
    Создание базы phonenumber
    """
    connection = psycopg2.connect(user='postgres', password='')
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    
    cursor.execute('CREATE DATABASE phonenumber')

    cursor.close()
    connection.close()

def create_table(conn):
    """
    Создание таблиц, выполняется один раз.
    Структура фиксированная, изменять таблицы не надо.
    """
    with conn.cursor() as cur:
        
        cur.execute("""
                    create table if not exists client (
                    id serial primary key,
                    name varchar(20) not null,
                    surname varchar(20) not null,
                    email varchar(255)
                    );
                    """)
        
        cur.execute("""
                    create table if not exists phone_number (
                    id serial primary key,
                    id_client integer not null references client(id),
                    number bigint not null
                    );
                    """)

def add_client(conn):
    """
    Добавляет клиента в таблицу client, возвращает id клиента
    Если введен номер телефона то выполняется запись в таблицу phone_number
    """
    print('''
Введите данные для создания нового клинта: Фамилию, Имя, eMail или Телефон. 
Пустым может быть телефон и email
          ''')
    data = requests()
    
    # Добавить Фамилию Имя и адрес
    with conn.cursor() as cur:
        cur.execute("""
                    insert into client(name, surname, email) values(%s, %s, %s) RETURNING id;
                    """, (data[1], data[0], data[2]))
        id_client = cur.fetchone()[0]
        
    # Если телефон введен, добавляем его в таблицу
    if data[3] != '':
        with conn.cursor() as cur:
            cur.execute("""
                    insert into phone_number(id_client, number) values(%s, %s) RETURNING id;
                    """, (id_client, data[3]))

    return id_client

def add_number(conn):
    """ 
    Добавляет телефон клиента в таблицу phone_number
    """
    
    print('''
Введите данные для какого клиента добавить номер. (Фамилию, Имя, eMail, Телефон)
Пустым может быть телефон и email.
          ''')
       
    data = search(conn)
    number_new = int(input('Введите новый номер телефона: '))
        
    with conn.cursor() as cur:
        cur.execute("""
                    insert into phone_number(id_client, number) values(%s, %s);
                    """, (int(data[0][0]), number_new))
        
def update(conn):
    """
    Позволяет изменить данные о клиенте 
    """
    print('''
Введите данные у какого клиента изменить данные. (Фамилию, Имя, eMail, Телефон).
          ''')
    print()
    data = search(conn)
    print()
    print('''Что вы хотите изменить
    1. Фамилию
    2. Имя
    3. eMail
    4. Номер телефона
    ''')
    control = input('Пункт меню: ')

    # Выбор по условию что менять
    if control == '1':
        new_surname = input('Введите новую фамилию: ')
        with conn.cursor() as cur:
            cur.execute("update client set surname = %s where id = %s;", (new_surname, data[0][0]))
    elif control == '2':
        new_name = input('Введите новое имя: ')
        with conn.cursor() as cur:
            cur.execute("update client set name = %s where id = %s;", (new_name, data[0][0]))
    elif control == '3':
        new_email = input('Введите новый eMail: ')
        with conn.cursor() as cur:
            cur.execute("update client set email = %s where id = %s;", (new_email, data[0][0]))
    elif control == '4':
        old_number = input('Введите старый номер телефона: ')
        new_number = input('Введите новый номер телефона: ')
        with conn.cursor() as cur:
            cur.execute("update phone_number set number = %s where id_client = %s and number = %s;", (new_number, data[0][0], old_number))

def dell_phone(conn):
    """
    Удаляет телефон
    """
    print('''
Введите данные у какого клиента удалить телефон. (Фамилию, Имя, eMail, Телефон).
          ''')    
    data = search(conn)
    
    old_number = input('Введите номер телефона для удаления: ')
    with conn.cursor() as cur:
        cur.execute('delete from phone_number where id_client = %s and number = %s;', (data[0][0], old_number))

def dell_client(conn):
    """
    Удаляет клиента
    """
    print('''
Введите данные какого клиента удалить. (Фамилию, Имя, eMail, Телефон).
          ''')    
    data = search(conn)

    # Сначала удаляем телефоны, если есть
    if data[0][4] != None:
        with conn.cursor() as cur:
            cur.execute('delete from phone_number where id_client = %s;', (data[0][0],))
    
    with conn.cursor() as cur:
        cur.execute('delete from client where id = %s;', (data[0][0],))

def all_client(conn):
    """
    Показать всех клиентов
    """
    with conn.cursor() as cur:
        cur.execute('select c.id, surname, name, email, number from client c\
            left join phone_number pn on c.id = pn.id_client\
                order by surname, name, number')
        client = cur.fetchall()
    
    for value in client:
        print(f'{value[1]} {value[2]} {value[3]} {value[4]}')

def search(conn):
#     print('''
# Для поиска введите Фамилию, Имя, eMail или Телефон. 
# Для пропуска данных, пуская строка
#           ''')
    data = requests()
    
    where_add = ''
    control = False
    
    if data[0] != '': 
        where_add += f"surname = '{data[0]}'"
        control = True
        
    if data[1] != '' and control == True:
        where_add += f" and name = '{data[1]}'"
    elif data[1] != '': 
        where_add += f"name = '{data[1]}'"
        control = True
        
    if data[2] != '' and control == True:
        where_add += f" and email = '{data[2]}'"
    elif data[2] != '':
        where_add += f"email = '{data[2]}'"
        control = True
    
    if data[3] != '' and control == True:
        where_add += f" and number = '{data[3]}'"
    elif data[3] != '':
        where_add += f"number = '{data[3]}'"
    
    request = f"select c.id, surname, name, email, number from client\
        c left join phone_number pn on c.id = pn.id_client \
        where {where_add} \
        order by surname, name, number;"
    
    with conn.cursor() as cur:
        cur.execute(request)
        client = cur.fetchall()
    
    # print(client)
    
    for value in client:
        print(f'{value[1]} {value[2]} {value[3]} {value[4]}')
        
    return client

def requests():
    """
    Дополнительная функция для введения информации
    """
    
    
    data = []
    
    surname_input = input('Введите Фамилию: ')
    name_input = input('Введите Имя: ')
    email_input = input('Введите eMail: ')
    number_input = input('Введите телефон: ')
    
    data.append(surname_input)
    data.append(name_input)
    data.append(email_input)
    data.append(number_input)

    return data



                        
def menu(conn):
    menu_item = {'1': create_table, '2': add_client, '3': add_number, '4': update, '5': dell_phone, '6': dell_client, '7': all_client, '8': search}
    control = True
    
    while control:
        print("""Введите команду:
          1 - Создать таблицы
          2 - Добавить нового клиента
          3 - Добавить телефон для существующего клиента
          4 - Изменить данные о клиенте
          5 - Удалить телефон у существующего клиента
          6 - Удалить клиента
          7 - Показать всех клиентов
          8 - Найти клиента по его данным (Имя, Фамилия, email, Телефон)
          q - выход
          """)
        
        comand = input('Команда: ').lower()
        if comand == 'q':
            control = False
        else: 
            return menu_item[comand](conn)






def main():
    # Создание, выполняется 1 раз
    # create_db()
            
    with psycopg2.connect(database='phonenumber' ,user='postgres', password='') as conn:
        
        menu(conn)
        

if __name__ == '__main__':
    main()
