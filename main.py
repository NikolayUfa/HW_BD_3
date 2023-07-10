import psycopg2

# Функция создания структуры БД
def create_db(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients
        (id SERIAL PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phones
        (id SERIAL PRIMARY KEY,
        client_id INTEGER,
        phone_number TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id))
    """)

    conn.commit()

# Функция добавления нового клиента
def add_client(conn, first_name, last_name, email, phones=None):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clients (first_name, last_name, email)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (first_name, last_name, email))

    client_id = cursor.fetchone()[0]

    if phones:
        for phone in phones:
            add_phone(conn, client_id, phone)

    conn.commit()

# Функция добавления телефона для существующего клиента
def add_phone(conn, client_id, phone):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO phones (client_id, phone_number)
        VALUES (%s, %s)
    """, (client_id, phone))

    conn.commit()

# Функция изменения данных о клиенте
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    cursor = conn.cursor()

    if first_name:
        cursor.execute("""
            UPDATE clients
            SET first_name = %s
            WHERE id = %s
        """, (first_name, client_id))

    if last_name:
        cursor.execute("""
            UPDATE clients
            SET last_name = %s
            WHERE id = %s
        """, (last_name, client_id))

    if email:
        cursor.execute("""
            UPDATE clients
            SET email = %s
            WHERE id = %s
        """, (email, client_id))

    if phones:
        # Удаляем все старые телефоны клиента
        cursor.execute("""
            DELETE FROM phones
            WHERE client_id = %s
        """, (client_id,))

        # Добавляем новые телефоны
        for phone in phones:
            add_phone(conn, client_id, phone)

    conn.commit()

# Функция удаления телефона для существующего клиента
def delete_phone(conn, client_id, phone):
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM phones
        WHERE client_id = %s AND phone_number = %s
    """, (client_id, phone))

    conn.commit()

# Функция удаления существующего клиента
def delete_client(conn, client_id):
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM clients
        WHERE id = %s
    """, (client_id,))

    # Удаляем все телефоны клиента
    cursor.execute("""
        DELETE FROM phones
        WHERE client_id = %s
    """, (client_id,))

    conn.commit()

# Функция поиска клиента по его данным
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT clients.*, phones.phone_number
        FROM clients
        LEFT JOIN phones ON clients.id = phones.client_id
        WHERE clients.first_name = %s OR clients.last_name = %s OR clients.email = %s OR phones.phone_number = %s
        ORDER BY clients.id
    """, (first_name, last_name, email, phone))

    results = cursor.fetchall()
    return results

# Подключение к базе данных
with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
    # Создание структуры БД
    create_db(conn)

    # Добавление клиентов
    add_client(conn, "Иван", "Иванов", "ivan@example.com", ["1234567890", "9876543210"])
    add_client(conn, "Петр", "Петров", "petr@example.com")
    add_client(conn, "Сергей", "Сергеев", "sergey@example.com", ["1111111111"])

    # Изменение данных о клиенте
    change_client(conn, 2, first_name="Новое имя", last_name="Новая фамилия", email="newemail@example.com")

    # Удаление телефона для клиента
    delete_phone(conn, 2, "1111111111")

    # Удаление клиента
    delete_client(conn, 3)

    # Поиск клиента
    search_results = find_client(conn, first_name="Иван")
    for result in search_results:
        print(f"ID: {result[0]}, Имя: {result[1]}, Фамилия: {result[2]}, Email: {result[3]}, Телефон: {result[4]}")

conn.close()