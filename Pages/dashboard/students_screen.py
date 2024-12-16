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
                content=ft.Container(
                    content=ft.ListView(
                        controls=[
                    ft.Text(f"ФИО: {student[1]}"),
                    ft.Text(f"Дата рождения: {student[2]}"),
                    ft.Text(f"Школа: {student[3]}"),
                    ft.Text(f"Регион: {student[4]}"),
                    ft.Text(f"Район: {student[5]}"),
                    ft.Text(f"Город: {student[6]}"),
                    ft.Text(f"Адрес проживания: {student[7]}"),
                    ft.Text(f"ФИО родителей: {student[8]}"),
                    ft.Text(f"Фактический адрес: {student[9]}"),
                    ft.Text(f"Хобби: {student[10]}"),
                    ft.Text(f"Национальность: {student[11]}"),
                    ft.Text(f"Гражданство: {student[12]}"),
                    ft.Text(f"РВП или ВНЖ: {student[13]}"),
                    ft.Text(f"Срок действия документа: {student[14]}"),
                    ft.Text(f"Социальный статус: {student[15]}"),
                    ft.Text(f"Статус сироты: {'Да' if student[16] else 'Нет'}"),
                    ft.Text(f"Статус инвалида: {'Да' if student[17] else 'Нет'}"),
                    ft.Text(f"Информация о поддержке семьи: {student[18]}"),
                    ft.Text(f"Предыдущее место жительства: {student[19]}"),
                    ft.Text(f"Текущее место жительства: {student[20]}"),
                    ft.Text(f"Тип жилья: {student[21]}"),
                    ft.Text(f"Образование и должность родителей: {student[22]}"),
                    ft.Text(f"Адресная социальная помощь: {student[23]}"),
                    ft.Text(f"Статус отчисления: {'Да' if student[24] else 'Нет'}"),
                    ft.Text(f"Номер приказа: {student[25]}")
                    ],
                    spacing=10,
                    expand=True,
                ),
                width=700,
                height=500,
                ),
                actions=[
                    ft.TextButton("Закрыть", on_click=lambda e: page.close(details_dialog))
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
            address_field = ft.TextField(label="Адрес проживания", value=student[7])
            parents_field = ft.TextField(label="ФИО родителей", value=student[8])
            factual_address_field = ft.TextField(label="Фактический адрес", value=student[9])
            hobbies_field = ft.TextField(label="Хобби", value=student[10])
            nationality_field = ft.TextField(label="Национальность", value=student[11])
            citizenship_field = ft.TextField(label="Гражданство", value=student[12])
            residence_permit_field = ft.TextField(label="РВП или ВНЖ", value=student[13])
            document_expiry_date_field = ft.TextField(label="Срок действия документа", value=str(student[14]) if student[14] else "")
            social_status_field = ft.TextField(label="Социальный статус", value=student[15])
            orphan_status_field = ft.Checkbox(label="Статус сироты", value=student[16])
            disability_status_field = ft.Checkbox(label="Статус инвалида", value=student[17])
            family_support_info_field = ft.TextField(label="Информация о поддержке", value=student[18])
            previous_residence_field = ft.TextField(label="Предыдущее место жительства", value=student[19])
            current_residence_field = ft.TextField(label="Текущее место жительства", value=student[20])
            housing_type_field = ft.TextField(label="Тип жилья", value=student[21])
            parents_job_education_field = ft.TextField(label="Образование и должность родителей", value=student[22])
            family_social_help_field = ft.TextField(label="Адресная соцпомощь", value=student[23])
            expelled_field = ft.Checkbox(label="Статус отчисления", value=student[24])
            order_number_field = ft.TextField(label="Номер приказа", value=student[25])

            def save_edited_student(e):
                try:
                    conn = connect_to_db()
                    cursor = conn.cursor()
                    update_query = sql.SQL("""
                    UPDATE students SET
                    full_name = %s, 
                    date_of_birth = %s, 
                    origin_school = %s,
                    region = %s, 
                    district = %s, 
                    city = %s,
                    address = %s,
                    parent_full_name = %s,
                    factual_address = %s,
                    hobbies = %s,
                    nationality = %s,
                    citizenship = %s,
                    residence_permit = %s,
                    document_expiry_date = %s,
                    social_status = %s,
                    orphan_status = %s,
                    disability_status = %s,
                    family_support_info = %s,
                    previous_residence = %s,
                    current_residence = %s,
                    housing_type = %s,
                    parents_job_education = %s,
                    family_social_help = %s,
                    expelled = %s,
                    order_number = %s
                    WHERE id = %s
                    """)
                    cursor.execute(update_query, (
                        fio_field.value,
                        dob_field.value or None,
                        school_field.value,
                        region_field.value,
                        district_field.value,
                        city_field.value,
                        address_field.value,
                        parents_field.value,
                        factual_address_field.value,
                        hobbies_field.value,
                        nationality_field.value,
                        citizenship_field.value,
                        residence_permit_field.value,
                        document_expiry_date_field.value or None,
                        social_status_field.value,
                        orphan_status_field.value,
                        disability_status_field.value,
                        family_support_info_field.value,
                        previous_residence_field.value,
                        current_residence_field.value,
                        housing_type_field.value,
                        parents_job_education_field.value,
                        family_social_help_field.value,
                        expelled_field.value,
                        order_number_field.value,
                        student_id
                    ),),
                    conn.commit()
                    cursor.close()
                    conn.close()
                    page.snack_bar = ft.SnackBar(content=ft.Text("Студент успешно обновлен!"))
                    page.snack_bar.open = True
                    page.update()
                    page.close(dialog)
                    update_students_list(page)
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка обновления: {str(ex)}"))
                    page.snack_bar.open = True
                    page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Редактировать студента"),
                content=ft.Container(
                    content=ft.ListView(
                        controls=[
                            fio_field,
                            dob_field,
                            school_field,
                            region_field,
                            district_field,
                            city_field,
                            address_field,
                            parents_field,
                            factual_address_field,
                            hobbies_field,
                            nationality_field,
                            citizenship_field,
                            residence_permit_field,
                            document_expiry_date_field,
                            social_status_field,
                            orphan_status_field,
                            disability_status_field,
                            family_support_info_field,
                            previous_residence_field,
                            current_residence_field,
                            housing_type_field,
                            parents_job_education_field,
                            family_social_help_field,
                            expelled_field,
                            order_number_field
                        ],
                        spacing=10,
                        expand=True
                    ),
                    width=700,
                    height=500
                ),
                actions=[
                    ft.TextButton("Сохранить", on_click=save_edited_student),
                    ft.TextButton("Отмена", on_click=lambda e: page.close(dialog))
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
            
            page.close(delete_dialog)
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
            ft.TextButton("Нет", on_click=lambda e: page.close(delete_dialog))
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
            "origin_school": school_field.value or "",
            "region": region_field.value or "",
            "district": district_field.value or "",
            "city": city_field.value or "",
            "address": address_field.value or "",
            "parent_full_name": parents_field.value or "",
            "factual_address": factual_address_field.value or "",
            "hobbies": hobbies_field.value or "",
            "nationality": nationality_field.value or "",
            "citizenship": citizenship_field.value or "",
            "residence_permit": residence_permit_field.value or "",
            "document_expiry_date": document_expiry_date_field.value or None,
            "social_status": social_status_field.value or "",
            "orphan_status": orphan_status_field.value,
            "disability_status": disability_status_field.value,
            "family_support_info": family_support_info_field.value or "",
            "previous_residence": previous_residence_field.value or "",
            "current_residence": current_residence_field.value or "",
            "housing_type": housing_type_field.value or "",
            "parents_job_education": parents_job_education_field.value or "",
            "family_social_help": family_social_help_field.value or "",
            "expelled": expelled_field.value,
            "order_number": order_number_field.value or "",
        }
        page.close(dialog)

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
                student_info["origin_school"],
                student_info["region"],
                student_info["district"],
                student_info["city"],
                student_info["address"],
                student_info["parent_full_name"],
                student_info["factual_address"],
                student_info["hobbies"],
                student_info["nationality"],
                student_info["citizenship"],
                student_info["residence_permit"],
                student_info["document_expiry_date"],
                student_info["social_status"],
                student_info["orphan_status"],
                student_info["disability_status"],
                student_info["family_support_info"],
                student_info["previous_residence"],
                student_info["current_residence"],
                student_info["housing_type"],
                student_info["parents_job_education"],
                student_info["family_social_help"],
                student_info["expelled"],
                student_info["order_number"]
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
    school_field = ft.TextField(label="Школа")
    region_field = ft.TextField(label="Область")
    district_field = ft.TextField(label="Район")
    city_field = ft.TextField(label="Город")
    address_field = ft.TextField(label="Адрес проживания")
    parents_field = ft.TextField(label="ФИО родителей")
    factual_address_field = ft.TextField(label="Фактический адрес")
    hobbies_field = ft.TextField(label="Хобби")
    nationality_field = ft.TextField(label="Национальность")
    citizenship_field = ft.TextField(label="Гражданство")
    residence_permit_field = ft.TextField(label="РВП или ВНЖ")
    document_expiry_date_field = ft.TextField(label="Срок действия документа")
    social_status_field = ft.TextField(label="Социальный статус")
    orphan_status_field = ft.Checkbox(label="Статус сироты")
    disability_status_field = ft.Checkbox(label="Статус инвалида")
    family_support_info_field = ft.TextField(label="Информация о поддержке")
    previous_residence_field = ft.TextField(label="Предыдущий адрес")
    current_residence_field = ft.TextField(label="Текущий адрес")
    housing_type_field = ft.TextField(label="Тип жилья")
    parents_job_education_field = ft.TextField(label="Образование и должность родителей")
    family_social_help_field = ft.TextField(label="Адресная соцпомощь")
    expelled_field = ft.Checkbox(label="Статус отчисления")
    order_number_field = ft.TextField(label="Номер приказа")
    # Добавьте остальные поля как в вашем оригинальном коде

    dialog = ft.AlertDialog(
        title=ft.Text("Добавить студента"),
        content=ft.Container(
            content=ft.ListView(
                controls=[
                    fio_field,
                    dob_field,
                    school_field,
                    region_field,
                    district_field,
                    city_field,
                    address_field,
                    parents_field,
                    factual_address_field,
                    hobbies_field,
                    nationality_field,
                    citizenship_field,
                    residence_permit_field,
                    document_expiry_date_field,
                    social_status_field,
                    orphan_status_field,
                    disability_status_field,
                    family_support_info_field,
                    previous_residence_field,
                    current_residence_field,
                    housing_type_field,
                    parents_job_education_field,
                    family_social_help_field,
                    expelled_field,
                    order_number_field,
                ],
                spacing=10,
                expand=True,
            ),
            width=700,
            height=500,
        ),
        actions=[
            ft.TextButton("Сохранить", on_click=save_student),
            ft.TextButton("Отмена", on_click=lambda e: page.close(dialog)),
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

            # content=ft.Container()
            #         content=ft.ListView()
            #             controls=[]
    

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