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



def on_group_change(page, e):
    update_students_list(page, selected_group=e.control.value)
    page.update()

def on_course_change(page, e):
    update_students_list(page, selected_course=e.control.value)
    page.update()

def select_group_course_dialog(page):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT group_name FROM students WHERE group_name IS NOT NULL")
        groups = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT course_number FROM students WHERE course_number IS NOT NULL")
        courses = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
    except Exception as e:
        groups = []
        courses = []
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка получения групп и курсов: {str(e)}"))
        page.snack_bar.open = True
        page.update()

    group_dropdown = ft.Dropdown(
        label="Выберите группу",
        options=[ft.dropdown.Option(group) for group in groups],
        width=300,
        on_change=lambda e: on_group_change(page, e)  # Передаем page явно
    )
    
    course_dropdown = ft.Dropdown(
        label="Выберите курс", 
        options=[ft.dropdown.Option(str(course)) for course in courses],
        width=300,
        on_change=lambda e: on_course_change(page, e)  # Передаем page явно
    )

    dialog = ft.AlertDialog(
        title=ft.Text("Фильтр групп и курсов"),
        content=ft.Column(
            controls=[
                group_dropdown,
                course_dropdown
            ],
            spacing=10,
            width=350
        ),
        actions=[
            ft.TextButton("Применить", on_click=lambda e: page.close(dialog)),
            ft.TextButton("Отмена", on_click=lambda e: page.close(dialog))
        ]
    )

    page.dialog = dialog
    dialog.open = True
    page.update()

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
                    ft.Text(f"Номер приказа: {student[25]}"),
                    ft.Text(f"Группа: {student[27] or 'Не указано'}"),
                    ft.Text(f"Курс: {student[28] or 'Не указан'}"),
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
            group_name_field = ft.TextField(label="Группа", value=student[27] if student[27] else "")
            course_number_field = ft.TextField(label="Курс", value=str(student[28]) if student[28] else "")

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
                        order_number = %s,
                        group_name = %s,
                        course_number = %s
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
                        group_name_field.value,
                        course_number_field.value,
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
                            order_number_field,
                            group_name_field,
                            course_number_field
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

def update_students_list(page, search_query=None, selected_group=None, selected_course=None):
    global students_table, content
    content.controls.clear()
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT id, full_name, date_of_birth, origin_school, region, district, city, group_name, course_number
            FROM students
            WHERE 1=1
        """
        params = []

        if search_query:
            query += """ 
                AND (
                    LOWER(full_name) LIKE LOWER(%s) 
                    OR LOWER(origin_school) LIKE LOWER(%s)
                    OR LOWER(city) LIKE LOWER(%s)
                    OR LOWER(district) LIKE LOWER(%s)
                    OR LOWER(group_name) LIKE LOWER(%s)
                )
            """
            search_param = f"%{search_query}%"
            params.extend([search_param] * 5)

        if selected_group:
            query += " AND group_name = %s"
            params.append(selected_group)

        if selected_course:
            query += " AND course_number = %s"
            params.append(selected_course)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        students_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ФИО")),
                ft.DataColumn(ft.Text("Дата рождения")),
                ft.DataColumn(ft.Text("Школа")),
                ft.DataColumn(ft.Text("Район")),
                ft.DataColumn(ft.Text("Город")),
                ft.DataColumn(ft.Text("Группа")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[1]))),  # ФИО
                        ft.DataCell(ft.Text(str(row[2]))),  # Дата рождения
                        ft.DataCell(ft.Text(str(row[3]))),  # Школа
                        ft.DataCell(ft.Text(str(row[5]))),  # Район
                        ft.DataCell(ft.Text(str(row[6]))),  # Город
                        ft.DataCell(ft.Text(str(row[7] or ''))),  # Группа
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY, 
                                    tooltip="Просмотр",
                                    icon_color=ft.Colors.BLUE_600,
                                    on_click=lambda e, sid=row[0]: view_student_details(page, sid)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT, 
                                    tooltip="Редактировать",
                                    icon_color=ft.Colors.BLUE_600,
                                    on_click=lambda e, sid=row[0]: edit_student_dialog(page, sid)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE, 
                                    tooltip="Удалить",
                                    icon_color=ft.Colors.BLUE_600,
                                    on_click=lambda e, sid=row[0]: delete_student(page, sid)
                                )
                            ])
                        )
                    ]
                ) for row in rows
            ]
        )

        # Wrap the table in a Container with scrolling
        table_container = ft.Container(
            content=students_table,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            padding=10,
            expand=True,
        )

        scrollable_content = ft.Column(
            [table_container],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
        )

        content.controls.append(scrollable_content)
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        content.controls.append(ft.Text(f"Ошибка загрузки данных: {e}", color=ft.colors.RED))

def students_screen(page):
    search_field = ft.TextField(
        label="Поиск",
        hint_text="Поиск по ФИО, школе, городу, району или группе",
        width=400,
        border_radius=ft.border_radius.all(8),
    )

    def apply_search(e):
        update_students_list(page, search_query=search_field.value)
        page.update()

    def reset_filter(e):
        search_field.value = ""
        update_students_list(page)
        page.snack_bar = ft.SnackBar(content=ft.Text("Фильтры сброшены."))
        page.snack_bar.open = True
        page.update()

    search_row = ft.Row(
        controls=[
            search_field,
            ft.ElevatedButton(
                "Поиск",
                icon=ft.icons.SEARCH,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                on_click=apply_search,
            ),
            ft.ElevatedButton(
                "Добавить студента",
                icon=ft.icons.ADD,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                on_click=lambda e: add_student_dialog(page),
            ),
            ft.ElevatedButton(
                "Выбрать группу",
                icon=ft.icons.SELECT_ALL,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                on_click=lambda e: select_group_course_dialog(page),
            ),
            ft.ElevatedButton(
                "Сбросить фильтр",
                icon=ft.icons.CLEAR,
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                on_click=reset_filter,
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
            ft.Container(
                content=content,
                expand=True,
            ),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

def add_student_dialog(page):
    def save_student(e):
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
            "group_name": group_name_field.value or "",
            "course_number": course_number_field.value or "",
        }

        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            insert_query = sql.SQL("""
                INSERT INTO students (
                    full_name, date_of_birth, origin_school, region, district, 
                    city, address, parent_full_name, factual_address, hobbies, 
                    nationality, citizenship, residence_permit, 
                    document_expiry_date, social_status, orphan_status,
                    disability_status, family_support_info, previous_residence, 
                    current_residence, housing_type, parents_job_education, 
                    family_social_help, expelled, order_number, 
                    group_name, course_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s)
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
                student_info["order_number"],
                student_info["group_name"],
                student_info["course_number"]
            ))

            conn.commit()
            cursor.close()
            conn.close()
            
            page.snack_bar = ft.SnackBar(content=ft.Text("Студент успешно добавлен!"))
            page.snack_bar.open = True
            page.update()
            
            dialog.close()
            update_students_list(page)
        except Exception as e:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка при сохранении: {str(e)}"))
            page.snack_bar.open = True
            page.update()
            print(f"Ошибка при сохранении данных: {e}")

    # Для курса сделаем выпадающий список с фиксированными значениями
    course_number_field = ft.Dropdown(
        label="Курс",
        width=300,
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2"),
            ft.dropdown.Option("3")
        ]
    )

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
    group_name_field = ft.TextField(label="Группа")
    course_number_field = ft.TextField(label="Курс")
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
                    group_name_field,
                    course_number_field
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