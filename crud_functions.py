import sqlite3

file_name = 'Products.db'
fill_table = ''
base_names = 'Products'
connection = sqlite3.connect(file_name)
cursor = connection.cursor()


# Создание файла базы SQL по заданным параметрам
def initiate_db(base_name, catalog_id, title_name, description, price, image):
    global fill_table
    global connection
    global cursor
    print(f'\033[32mСоздаем базу данных, если она существует, то открываем: {file_name}\033[0m')
    fill_table = catalog_id, title_name, description, price, image
    print(f'\033[34mСоздаем список таблиц - Пользователь: {base_name}, поля: {catalog_id}, {title_name}, '
          f'{description}, {price}, {image}\033[0m')
    set_file_name = (f'''CREATE TABLE IF NOT EXISTS {base_name}(
            id INTEGER PRIMARY KEY,
            {catalog_id} TEXT NOT NULL,
            {title_name} TEXT,
            {description} TEXT,
            {price} INT NOT NULL,
            {image} TEXT
        )
    ''')
    cursor.execute(set_file_name)
    commit()


# Очистка таблицы SQL
def delete_table():
    print('Очистка списка')
    cursor.execute(f'DELETE FROM {base_names};')
    commit()


# Заполнение таблицы SQL по заданным параметрам
def fill_in_the_table(set_catalog, set_title, set_description, set_price, set_photo):
    global fill_table
    global connection
    global cursor
    sql = str(f'INSERT INTO {base_names} ({fill_table[0]}, {fill_table[1]}, {fill_table[2]}, '
              f'{fill_table[3]}, {fill_table[4]}) VALUES (?, ?, ?, ?, ?)')
    cursor.execute(f'{sql}', (f'{set_catalog}', f'{set_title}', f'{set_description}',
                              set_price, f'{set_photo}'))
    commit()


# Отображение содержимого таблицы по определенным параметрам
def screen():
    global base_names
    cursor.execute(f'SELECT * FROM {base_names}')
    products = cursor.fetchall()
    for product in products:
        print(f'id: {product[0]} | Название: {product[2]} | Описание: {product[3]} | Цена: {product[4]}')


# Отображение содержимого таблицы
def display():
    global base_names
    cursor.execute(f'SELECT * FROM {base_names}')
    products = cursor.fetchall()
    for product in products:
        print(product)


# Закрытие таблицы
def commit():
    global connection
    global cursor
    connection.commit()


# Завершение работы с таблицей
def finish():
    global connection
    global cursor
    connection.close()
