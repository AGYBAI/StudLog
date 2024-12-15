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


def add_student_dialog(page):
    # Функция для создания диалогового окна
    def save_student(e):
        # Сохраняем данные студента
        student_info = {
            "full_name": fio_field.value,
            "date_of_birth": dob_field.value,
            "origin_school": school_field.value,
            "region": region_field.value,
            "district": district_field.value,
            "city": city_field.value,
            "address": address_field.value,
            "parent_full_name": parents_field.value,
            "factual_address": factual_address_field.value,
            "hobbies": hobbies_field.value,
            "nationality": nationality_field.value,
            "citizenship": citizenship_field.value,
            "residence_permit": residence_permit_field.value,
            "document_expiry_date": document_expiry_date_field.value,
            "social_status": social_status_field.value,
            "orphan_status": orphan_status_field.value,
            "disability_status": disability_status_field.value,
            "family_support_info": family_support_info_field.value,
            "previous_residence": previous_residence_field.value,
            "current_residence": current_residence_field.value,
            "housing_type": housing_type_field.value,
            "parents_job_education": parents_job_education_field.value,
            "family_social_help": family_social_help_field.value,
            "expelled": expelled_field.value,
            "order_number": order_number_field.value,
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
            dialog.close()  # Закрываем диалог после сохранения
            update_students_list()  # Обновляем список студентов
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")

    # Поля для ввода данных студента
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

    dialog = ft.AlertDialog(
        title=ft.Text("Добавить студента"),  # Используем ft.Text вместо строки
        content=ft.Column(
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
        ),
        actions=[
            ft.TextButton("Сохранить", on_click=save_student),
            ft.TextButton("Отмена", on_click=lambda e: page.close(dialog)),
        ],
    )

    page.dialog = dialog
    dialog.open = True

def update_students_list():
    # Функция для обновления списка студентов на главной странице
    content.controls.clear()
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()

        for row in rows:
            content.controls.append(
                ft.Text(f"{row[1]} - {row[3]} - {row[4]}"))  # Пример отображения ФИО, области и района

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")


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

    update_students_list()  # Обновляем список студентов при загрузке

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