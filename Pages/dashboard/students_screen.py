import flet as ft
import psycopg2
from psycopg2 import sql

def connect_to_db():
    return psycopg2.connect(
        dbname="railway",
        user="postgres",
        password="dfFudMqjdNUrRDNEvvTVVvBaNztZfxaP",
        host="autorack.proxy.rlwy.net",
        port="33741"
    )

def view_student_details(page, student_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if student:
            # Создаем диалоговое окно с подробной информацией о студенте
            details_dialog = ft.AlertDialog(
                title=ft.Text(f"Детали студента: {student[1]}"),
                content=ft.Column([
                    ft.Text(f"ФИО: {student[1]}"),
                    ft.Text(f"Дата рождения: {student[2]}"),
                    ft.Text(f"Школа: {student[3]}"),
                    ft.Text(f"Регион: {student[4]}"),
                    ft.Text(f"Район: {student[5]}"),
                    # Добавьте остальные поля по необходимости
                ]),
                actions=[
                    ft.TextButton("Закрыть", on_click=lambda e: page.dialog.close())
                ]
            )
            
            page.dialog = details_dialog
            details_dialog.open = True
            page.update()
        
        cursor.close()
        conn.close()
    except Exception as e:
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка просмотра: {str(e)}"))
        page.snack_bar.open = True
        page.update()

def edit_student_dialog(page, student_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if student:
            # Создаем поля с текущими значениями студента
            fio_field = ft.TextField(label="ФИО", value=student[1])
            dob_field = ft.TextField(label="Дата рождения", value=str(student[2]) if student[2] else "")
            school_field = ft.TextField(label="Школа", value=student[3])
            region_field = ft.TextField(label="Область", value=student[4])
            district_field = ft.TextField(label="Район", value=student[5])
            city_field = ft.TextField(label="Город", value=student[6])
            
            def save_edited_student(e):
                try:
                    conn = connect_to_db()
                    cursor = conn.cursor()
                    
                    update_query = sql.SQL("""
                        UPDATE students SET 
                        full_name = %s, date_of_birth = %s, origin_school = %s, 
                        region = %s, district = %s, city = %s
                        WHERE id = %s
                    """)
                    
                    cursor.execute(update_query, (
                        fio_field.value,
                        dob_field.value or None,
                        school_field.value,
                        region_field.value,
                        district_field.value,
                        city_field.value,
                        student_id
                    ))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    page.snack_bar = ft.SnackBar(content=ft.Text("Студент успешно обновлен!"))
                    page.snack_bar.open = True
                    page.update()
                    
                    dialog.close()
                    update_students_list(page)
                    
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка обновления: {str(ex)}"))
                    page.snack_bar.open = True
                    page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Редактировать студента"),
                content=ft.Column([
                    fio_field,
                    dob_field,
                    school_field,
                    region_field,
                    district_field,
                    city_field
                ]),
                actions=[
                    ft.TextButton("Сохранить", on_click=save_edited_student),
                    ft.TextButton("Отмена", on_click=lambda e: dialog.close())
                ]
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        cursor.close()
        conn.close()
    except Exception as e:
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка редактирования: {str(e)}"))
        page.snack_bar.open = True
        page.update()

def delete_student(page, student_id):
    def confirm_delete(e):
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            page.snack_bar = ft.SnackBar(content=ft.Text("Студент успешно удален!"))
            page.snack_bar.open = True
            page.update()
            
            delete_dialog.close()
            update_students_list(page)
            
        except Exception as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка удаления: {str(ex)}"))
            page.snack_bar.open = True
            page.update()
    
    delete_dialog = ft.AlertDialog(
        title=ft.Text("Подтвердите удаление"),
        content=ft.Text("Вы уверены, что хотите удалить этого студента?"),
        actions=[
            ft.TextButton("Да", on_click=confirm_delete),
            ft.TextButton("Нет", on_click=lambda e: delete_dialog.close())
        ]
    )
    
    page.dialog = delete_dialog
    delete_dialog.open = True
    page.update()

def update_students_list(page):
    global students_table, content
    content.controls.clear()
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, full_name, date_of_birth, origin_school, region, district, city
            FROM students
        """)
        rows = cursor.fetchall()

        students_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ФИО")),
                ft.DataColumn(ft.Text("Дата рождения")),
                ft.DataColumn(ft.Text("Школа")),
                ft.DataColumn(ft.Text("Область")),
                ft.DataColumn(ft.Text("Район")),
                ft.DataColumn(ft.Text("Город")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[1]))),  # ФИО
                        ft.DataCell(ft.Text(str(row[2]))),  # Дата рождения
                        ft.DataCell(ft.Text(str(row[3]))),  # Школа
                        ft.DataCell(ft.Text(str(row[4]))),  # Область
                        ft.DataCell(ft.Text(str(row[5]))),  # Район
                        ft.DataCell(ft.Text(str(row[6]))),  # Город
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY, 
                                    tooltip="Просмотр",
                                    on_click=lambda e, student_id=row[0]: view_student_details(page, student_id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT, 
                                    tooltip="Редактировать",
                                    on_click=lambda e, student_id=row[0]: edit_student_dialog(page, student_id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE, 
                                    tooltip="Удалить",
                                    on_click=lambda e, student_id=row[0]: delete_student(page, student_id)
                                )
                            ])
                        )
                    ]
                ) for row in rows
            ]
        )

        content.controls.append(students_table)
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        content.controls.append(ft.Text(f"Ошибка загрузки данных: {e}", color=ft.colors.RED))

def students_screen(page):
    def on_search_change(e):
        print(f"Поиск: {e.control.value}")

    search_row = ft.Row(
        controls=[
            ft.TextField(
                label="Поиск",
                hint_text="Введите имя или ИИН",
                on_change=on_search_change,
                width=400,
                border_radius=ft.border_radius.all(8),
            ),
            ft.ElevatedButton(
                "Прикрепить документ",
                icon=ft.icons.ATTACH_FILE,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
            ),
            ft.ElevatedButton(
                "Добавить студента",
                icon=ft.icons.ADD,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                on_click=lambda e: add_student_dialog(page),  # Открываем диалог для добавления студента
            ),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
    )

    global content
    content = ft.Column(
        controls=[],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

    update_students_list(page)  # Передаем page в функцию обновления

    return ft.Column(
        controls=[
            search_row,
            ft.Divider(thickness=1, color=ft.Colors.BLACK),
            ft.Text("Данные студентов:", size=20, weight=ft.FontWeight.BOLD),
            content,
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

def add_student_dialog(page):
    # Функция для создания диалогового окна
    def save_student(e):
        # Сохраняем данные студента
        student_info = {
            "full_name": fio_field.value or "",
            "date_of_birth": dob_field.value or None,
            # Остальные поля как в вашем оригинальном коде
        }

        # Подключаемся к базе данных и сохраняем данные
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            insert_query = sql.SQL("""
                INSERT INTO students (full_name, date_of_birth, origin_school, region, district, city, address,
                                      parent_full_name, factual_address, hobbies, nationality, citizenship,
                                      residence_permit, document_expiry_date, social_status, orphan_status,
                                      disability_status, family_support_info, previous_residence, current_residence,
                                      housing_type, parents_job_education, family_social_help, expelled, order_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)

            cursor.execute(insert_query, (
                student_info["full_name"],
                student_info["date_of_birth"],
                # Добавьте остальные поля из вашего оригинального кода
                "", "", "", "", "", "", "", "", "", "", "", None, "", 
                False, False, "", "", "", "", "", "", False, ""
            ))

            conn.commit()  # Подтверждаем изменения
            cursor.close()
            conn.close()
            
            # Уведомление об успешном сохранении
            page.snack_bar = ft.SnackBar(content=ft.Text("Студент успешно добавлен!"))
            page.snack_bar.open = True
            page.update()
            
            dialog.close()  # Закрываем диалог после сохранения
            update_students_list(page)  # Обновляем список студентов
        except Exception as e:
            # Более подробное уведомление об ошибке
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка при сохранении: {str(e)}"))
            page.snack_bar.open = True
            page.update()
            print(f"Ошибка при сохранении данных: {e}")

    # Поля для ввода данных студента (как в вашем оригинальном коде)
    fio_field = ft.TextField(label="ФИО")
    dob_field = ft.TextField(label="Дата рождения")
    # Добавьте остальные поля как в вашем оригинальном коде

    dialog = ft.AlertDialog(
        title=ft.Text("Добавить студента"),
        content=ft.Container(
            content=ft.ListView(
                controls=[
                    fio_field,
                    dob_field,
                    # Добавьте остальные поля как в вашем оригинальном коде
                ],
                spacing=10,
                expand=True,
            ),
            width=700,
            height=500,
        ),
        actions=[
            ft.TextButton("Сохранить", on_click=save_student),
            ft.TextButton("Отмена", on_click=lambda e: page.dialog.close()),
        ],
    )

    page.dialog = dialog
    dialog.open = True
    page.update()

# Экспортируем функцию students_screen для использования в других модулях

def update_students_list(page):  # Добавляем page как параметр
    global students_table, content
    content.controls.clear()
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, full_name, date_of_birth, origin_school, region, district, city
            FROM students
        """)
        rows = cursor.fetchall()

        students_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ФИО")),
                ft.DataColumn(ft.Text("Дата рождения")),
                ft.DataColumn(ft.Text("Школа")),
                ft.DataColumn(ft.Text("Область")),
                ft.DataColumn(ft.Text("Район")),
                ft.DataColumn(ft.Text("Город")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[1]))),  # ФИО
                        ft.DataCell(ft.Text(str(row[2]))),  # Дата рождения
                        ft.DataCell(ft.Text(str(row[3]))),  # Школа
                        ft.DataCell(ft.Text(str(row[4]))),  # Область
                        ft.DataCell(ft.Text(str(row[5]))),  # Район
                        ft.DataCell(ft.Text(str(row[6]))),  # Город
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY, 
                                    tooltip="Просмотр",
                                    on_click=lambda e, sid=row[0]: view_student_details(page, sid)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT, 
                                    tooltip="Редактировать",
                                    on_click=lambda e, sid=row[0]: edit_student_dialog(page, sid)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE, 
                                    tooltip="Удалить",
                                    on_click=lambda e, sid=row[0]: delete_student(page, sid)
                                )
                            ])
                        )
                    ]
                ) for row in rows
            ]
        )

        content.controls.append(students_table)
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        content.controls.append(ft.Text(f"Ошибка загрузки данных: {e}", color=ft.colors.RED))
# Остальной код остается прежним

def students_screen(page):
    def on_search_change(e):
        print(f"Поиск: {e.control.value}")

    search_row = ft.Row(
        controls=[
            ft.TextField(
                label="Поиск",
                hint_text="Введите имя или ИИН",
                on_change=on_search_change,
                width=400,
                border_radius=ft.border_radius.all(8),
            ),
            ft.ElevatedButton(
                "Прикрепить документ",
                icon=ft.icons.ATTACH_FILE,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
            ),
            ft.ElevatedButton(
                "Добавить студента",
                icon=ft.icons.ADD,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                on_click=lambda e: add_student_dialog(page),  # Открываем диалог для добавления студента
            ),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
    )


    

    global content
    content = ft.Column(
        controls=[],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

    update_students_list(page) # Обновляем список студентов при загрузке

    return ft.Column(
        controls=[
            search_row,
            ft.Divider(thickness=1, color=ft.Colors.BLACK),
            ft.Text("Данные студентов:", size=20, weight=ft.FontWeight.BOLD),
            content,
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )