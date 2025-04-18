import flet as ft
import psycopg2
from psycopg2 import sql
import traceback  # Import traceback for better error reporting
from Pages.utils import t
from Pages.utils import is_admin
import datetime
import os
import tempfile
import time
import subprocess
import sys

# Проверка и установка xlsxwriter
def ensure_xlsxwriter_installed():
    global EXCEL_AVAILABLE
    try:
        import xlsxwriter
        EXCEL_AVAILABLE = True
        print("xlsxwriter is available")
        return True
    except ImportError:
        EXCEL_AVAILABLE = False
        print("xlsxwriter is not installed. Attempting to install...")
        try:
            # Устанавливаем xlsxwriter с помощью pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "xlsxwriter"])
            import xlsxwriter
            EXCEL_AVAILABLE = True
            print("xlsxwriter successfully installed")
            return True
        except Exception as e:
            print(f"Failed to install xlsxwriter: {e}")
            EXCEL_AVAILABLE = False
            return False

# Для работы с Excel
try:
    import xlsxwriter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("WARNING: xlsxwriter module not found. Excel export feature will be disabled.")

# Добавление глобальной переменной для хранения текущего вида отображения
# true - карточки, false - таблица
view_as_cards = False

def connect_to_db():
    try:
        # Database configuration
        db_config = {
            "dbname": "railway",
            "user": "postgres",
            "password": "dfFudMqjdNUrRDNEvvTVVvBaNztZfxaP",
            "host": "autorack.proxy.rlwy.net",
            "port": "33741"
        }
        
        # Log connection attempt
        print(f"Attempting to connect to database at {db_config['host']}:{db_config['port']}")
        
        # Добавляем таймаут для подключения
        import time
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"Попытка подключения {retry_count + 1} из {max_retries}")
                # Create connection with timeout
                conn = psycopg2.connect(**db_config, connect_timeout=10)
                
                # Test connection
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                print("Database connection successful!")
                return conn
            except Exception as retry_error:
                retry_count += 1
                print(f"Попытка {retry_count} не удалась: {str(retry_error)}")
                if retry_count < max_retries:
                    print(f"Ожидание 2 секунды перед следующей попыткой...")
                    time.sleep(2)
                else:
                    print("Превышено максимальное количество попыток подключения.")
                    raise
        
        return None
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        traceback.print_exc()
        return None



def on_group_change(page, e):
    update_students_list(page, selected_group=e.control.value)

def on_course_change(page, e):
    update_students_list(page, selected_course=e.control.value)

def select_group_course_dialog(page):
    try:
        # Add debug for version and platform
        print(f"Flet version: {ft.__version__ if hasattr(ft, '__version__') else 'Unknown'}")
        print(f"Running platform: {ft.get_platform() if hasattr(ft, 'get_platform') else 'Unknown'}")
        print("Opening group/course dialog...")
        
        # Показываем индикатор загрузки
        loading_dialog = ft.AlertDialog(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Text("Загрузка данных групп и курсов...", text_align=ft.TextAlign.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            modal=True
        )
        
        # Открываем диалог загрузки
        page.dialog = loading_dialog
        loading_dialog.open = True
        page.update()
        
        conn = connect_to_db()
        if not conn:
            # Закрываем диалог загрузки
            loading_dialog.open = False
            page.update()
            
            show_snackbar(page, t("connection_error"), is_error=True)
            return
            
        cursor = conn.cursor()
        
        # Get distinct groups and courses
        cursor.execute("SELECT DISTINCT group_name FROM students WHERE group_name IS NOT NULL ORDER BY group_name")
        groups = [row[0] for row in cursor.fetchall()]
        print(f"Found {len(groups)} groups: {groups}")
        
        cursor.execute("SELECT DISTINCT course_number FROM students WHERE course_number IS NOT NULL ORDER BY course_number")
        courses = [str(row[0]) for row in cursor.fetchall()]
        print(f"Found {len(courses)} courses: {courses}")
        
        cursor.close()
        conn.close()

        # Закрываем диалог загрузки
        loading_dialog.open = False
        page.update()

        # Упрощенные выпадающие списки
        group_dropdown = ft.Dropdown(
            label=t("select_group"),
            hint_text=t("select_group_hint"),
            options=[ft.dropdown.Option(group) for group in groups],
            width=300,
        )

        course_dropdown = ft.Dropdown(
            label=t("select_course"),
            hint_text=t("select_course_hint"),
            options=[ft.dropdown.Option(course) for course in courses],
            width=300,
        )
        
        # Упрощенное содержимое диалога
        content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(t("select_filters_description"), size=16),
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.colors.BLUE_50,
                ),
                ft.Container(height=15),
                group_dropdown,
                ft.Container(height=15),
                course_dropdown,
            ],
            spacing=5,
            width=350,
            height=250,
        )
        
        def apply_filters(e):
            # Показываем индикатор загрузки на кнопке
            apply_btn.disabled = True
            apply_btn.icon = ft.icons.HOURGLASS_EMPTY
            apply_btn.text = t("applying")
            cancel_btn.disabled = True
            page.update()
            
            print(f"Applying filters - Group: {group_dropdown.value}, Course: {course_dropdown.value}")
            # Закрываем диалог сразу для ощущения отзывчивости
            dialog.close()
            
            # Обновляем список с анимацией загрузки (она встроена в update_students_list)
            update_students_list(
                page,
                selected_group=group_dropdown.value,
                selected_course=course_dropdown.value
            )
            
            # Показываем уведомление об успешном применении фильтров
            show_snackbar(page, t("filters_applied"))

        def close_dialog(e):
            print("Closing dialog")
            dialog.close()
            
        # Создаем кнопки для доступа из обработчиков
        apply_btn = ft.ElevatedButton(
            t("apply"),
            icon=ft.icons.CHECK,
            on_click=apply_filters,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
        )
        
        cancel_btn = ft.ElevatedButton(
            t("cancel"),
            icon=ft.icons.CANCEL,
            on_click=close_dialog,
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
        )
            
        # Упрощенные кнопки действий
        actions = [apply_btn, cancel_btn]
        
        # Create and open the custom dialog
        dialog = CustomDialog(
            page=page,
            title=t("filters"),
            content=content,
            actions=actions
        )
        
        dialog.open()
        print("Custom group/course dialog should be visible now")
        
    except Exception as e:
        # Закрываем диалог загрузки, если он открыт
        if hasattr(page, 'dialog') and page.dialog == loading_dialog:
            loading_dialog.open = False
            page.update()
            
        print(f"DEBUG - Error in filter dialog: {e}")  # Debug log
        traceback.print_exc()  # Print full traceback
        show_snackbar(page, f"{t('loading_error')}: {str(e)}", is_error=True)

def view_student_details(page, student_id):
    # Check admin permissions
    is_admin_user = is_admin()
    print(f"View student details for student {student_id}, is_admin: {is_admin_user}")
    
    if not is_admin_user:
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Только администраторы могут просматривать детальную информацию студентов"),
            open=True
        )
        page.update()
        return
        
    # Показываем индикатор загрузки
    loading_dialog = ft.AlertDialog(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=4),
            ft.Text("Загрузка данных студента...", text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        modal=True
    )
    
    # Открываем диалог загрузки
    page.dialog = loading_dialog
    loading_dialog.open = True
        
    try:
        conn = connect_to_db()
        if not conn:
            # Закрываем диалог загрузки
            loading_dialog.open = False
            page.update()
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка подключения к базе данных"),
                open=True
            )
            page.update()
            return
            
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Закрываем диалог загрузки
        loading_dialog.open = False
        page.update()
        
        if student:
            # Создаем словарь с полями и их значениями для лучшей читаемости
            field_mappings = [
                ("full_name", t("full_name"), student[1] or ""),
                ("birth_date", t("birth_date"), str(student[2]) if student[2] else ""),
                ("school", t("school"), student[3] or ""),
                ("region", t("region"), student[4] or ""),
                ("district", t("district"), student[5] or ""),
                ("city", t("city"), student[6] or ""),
                ("address", t("address"), student[7] or ""),
                ("parents_name", t("parents_name"), student[8] or ""),
                ("factual_address", t("factual_address"), student[9] or ""),
                ("hobbies", t("hobbies"), student[10] or ""),
                ("nationality", t("nationality"), student[11] or ""),
                ("citizenship", t("citizenship"), student[12] or ""),
                ("residence_permit", t("residence_permit"), student[13] or ""),
                ("document_expiry", t("document_expiry"), str(student[14]) if student[14] else ""),
                ("social_status", t("social_status"), student[15] or ""),
                ("orphan_status", t("orphan_status"), "✓" if student[16] else "✗"),
                ("disability_status", t("disability_status"), "✓" if student[17] else "✗"),
                ("family_support", t("family_support"), student[18] or ""),
                ("previous_residence", t("previous_residence"), student[19] or ""),
                ("current_residence", t("current_residence"), student[20] or ""),
                ("housing_type", t("housing_type"), student[21] or ""),
                ("parents_education", t("parents_education"), student[22] or ""),
                ("social_help", t("social_help"), student[23] or ""),
                ("expelled_status", t("expelled_status"), "✓" if student[24] else "✗"),
                ("order_number", t("order_number"), student[25] or ""),
                ("group", t("group"), student[27] or t("no_data")),
                ("course", t("course"), str(student[28]) if student[28] else t("no_data")),
            ]
            
            # Создаем контейнеры для каждого поля
            fields_containers = []
            for field_id, field_name, field_value in field_mappings:
                fields_containers.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(field_name, weight=ft.FontWeight.BOLD, size=14, color=ft.colors.BLUE_700),
                            ft.Text(field_value, selectable=True),
                        ]),
                        padding=10,
                        border_radius=8,
                        bgcolor=ft.colors.BLUE_50,
                        margin=ft.margin.only(bottom=5),
                    )
                )
            
            # Создаем скроллируемое окно с содержимым
            content = ft.ListView(
                controls=fields_containers,
                spacing=5,
                height=500,  # Увеличиваем высоту для размещения большего количества данных
                auto_scroll=False,  # Отключаем автоскролл
                padding=10,
            )
            
            # Кнопка прокрутки вверх
            scroll_to_top_btn = ft.IconButton(
                icon=ft.icons.ARROW_UPWARD,
                tooltip="Прокрутить вверх",
                icon_color=ft.colors.BLUE_400,
                on_click=lambda e: content.scroll_to(offset=0, duration=300),
            )
            
            # Кнопка редактирования в диалоге просмотра
            edit_btn = ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip=t("edit"),
                icon_color=ft.colors.ORANGE_400,
                on_click=lambda e: edit_from_view(e, student_id, dialog),
            )
            
            # Объединяем контент и кнопки
            view_content = ft.Column([
                content,
                ft.Row([
                    scroll_to_top_btn,
                    edit_btn
                ], alignment=ft.MainAxisAlignment.END),
            ])
            
            def close_dialog(e):
                dialog.close()
                page.update()
                
            # Create actions
            actions = [
                ft.ElevatedButton(t("close"), on_click=close_dialog)
            ]
            
            # Create and open the dialog
            dialog = CustomDialog(
                page=page,
                title=f"{t('student_details')}: {student[1]}",
                content=view_content,
                actions=actions
            )
            
            dialog.open()
            # Сброс позиции скролла после открытия
            content.scroll_to(offset=0)
            page.update()
            
            print(f"View details dialog opened for student {student_id}")
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Студент не найден"),
                open=True
            )
            page.update()
    except Exception as e:
        # Закрываем диалог загрузки, если он открыт
        if hasattr(page, 'dialog') and page.dialog == loading_dialog:
            loading_dialog.open = False
            page.update()
            
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Ошибка просмотра: {str(e)}"),
            open=True
        )
        page.update()

# Функция для редактирования студента из окна просмотра
def edit_from_view(e, student_id, view_dialog):
    # Получаем объект страницы из события
    page = e.page
    # Закрываем диалог просмотра
    if view_dialog:
        view_dialog.close()
    # Открываем диалог редактирования
    edit_student_dialog(page, student_id)

def edit_student_dialog(page, student_id):
    """Диалог для редактирования данных студента."""
    print(f"Открываем диалог редактирования для студента ID={student_id}")
    
    # Проверка прав администратора
    is_admin_user = is_admin()
    if not is_admin_user:
        show_snackbar(page, t("admin_only"), is_error=True)
        return
    
    # Показать индикатор загрузки
    loading_dialog = ft.AlertDialog(
        title=ft.Text(t("loading"), text_align=ft.TextAlign.CENTER),
        content=ft.Column([
            ft.ProgressRing(),
            ft.Text(t("loading_student_data"), text_align=ft.TextAlign.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER),
    )
    page.dialog = loading_dialog
    loading_dialog.open = True
    
    try:
        # Загружаем данные студента из БД
        conn = connect_to_db()
        if not conn:
            loading_dialog.open = False
            page.update()
            show_snackbar(page, t("connection_error"), is_error=True)
            return
            
        cursor = conn.cursor()
        
        # Получаем все данные студента
        cursor.execute(
            """
            SELECT * FROM students
            WHERE id = %s
            """,
            (student_id,)
        )
        
        student_data = cursor.fetchone()
        
        if not student_data:
            cursor.close()
            conn.close()
            loading_dialog.open = False
            page.update()
            show_snackbar(page, t("student_not_found"), is_error=True)
            return
        
        # Загружаем список групп
        cursor.execute("SELECT DISTINCT group_name FROM students ORDER BY group_name")
        groups = [row[0] for row in cursor.fetchall()]
        
        # Загружаем список курсов
        cursor.execute("SELECT DISTINCT course_number FROM students ORDER BY course_number")
        courses = [str(row[0]) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        # Создаем поля формы
        full_name_field = ft.TextField(
            label=t("full_name"), 
            value=student_data[1] or "",
            autofocus=True,
            expand=True,
            max_length=100
        )
        
        # Создаем DatePicker и поле для отображения даты
        date_picker = ft.DatePicker(
            first_date=datetime.datetime(1990, 1, 1),
            last_date=datetime.datetime.now(),
        )
        page.overlay.append(date_picker)
        
        date_field = ft.TextField(
            label=t("birth_date"),
            read_only=True,
            expand=True,
            hint_text="YYYY-MM-DD"
        )
        
        # Функция для открытия выбора даты
        def show_date_picker(_):
            date_picker.open = True
            page.update()
        
        # Устанавливаем обработчик нажатия на поле даты
        date_field.on_tap = show_date_picker
        
        # Функция обработки выбранной даты
        def on_date_selected(e):
            selected_date = date_picker.value
            
            # Валидация даты: она должна быть в прошлом и не ранее 100 лет назад
            if selected_date:
                today = datetime.datetime.now().date()
                date_100_years_ago = datetime.datetime.now().replace(year=today.year - 100).date()
                
                selected_date_obj = selected_date.date() if hasattr(selected_date, 'date') else selected_date
                
                if selected_date_obj > today:
                    show_snackbar(page, t("error_future_date"), is_error=True)
                    date_field.error_text = t("error_future_date")
                    date_field.value = ""
                elif selected_date_obj < date_100_years_ago:
                    show_snackbar(page, t("error_too_old_date"), is_error=True)
                    date_field.error_text = t("error_too_old_date")
                    date_field.value = ""
                else:
                    # Дата валидна
                    date_field.value = selected_date.strftime("%Y-%m-%d")
                    date_field.error_text = None
            else:
                date_field.value = ""
            
            page.update()
        
        # Устанавливаем обработчик изменения даты
        date_picker.on_change = on_date_selected
        
        # Основные поля
        school_field = ft.TextField(label=t("school"), expand=True, max_length=100)
        region_field = ft.TextField(label=t("region"), expand=True, max_length=100)
        district_field = ft.TextField(label=t("district"), expand=True, max_length=100)
        city_field = ft.TextField(label=t("city"), expand=True, max_length=100)
        
        # Дополнительные поля
        address_field = ft.TextField(label=t("address"), expand=True, max_length=100)
        parents_name_field = ft.TextField(label=t("parents_name"), expand=True, max_length=100)
        factual_address_field = ft.TextField(label=t("factual_address"), expand=True, max_length=100)
        hobbies_field = ft.TextField(label=t("hobbies"), expand=True, max_length=100)
        
        # Еще больше дополнительных полей
        nationality_field = ft.TextField(label=t("nationality"), expand=True, max_length=100)
        citizenship_field = ft.TextField(label=t("citizenship"), expand=True, max_length=100)
        residence_permit_field = ft.TextField(label=t("residence_permit"), expand=True, max_length=100)
        document_expiry_field = ft.TextField(label=t("document_expiry"), expand=True, max_length=100)
        social_status_field = ft.TextField(label=t("social_status"), expand=True, max_length=100)
        orphan_status_field = ft.TextField(label=t("orphan_status"), expand=True, max_length=100)
        disability_status_field = ft.TextField(label=t("disability_status"), expand=True, max_length=100)
        family_support_field = ft.TextField(label=t("family_support"), expand=True, max_length=100)
        previous_residence_field = ft.TextField(label=t("previous_residence"), expand=True, max_length=100)
        current_residence_field = ft.TextField(label=t("current_residence"), expand=True, max_length=100)
        housing_type_field = ft.TextField(label=t("housing_type"), expand=True, max_length=100)
        parents_education_field = ft.TextField(label=t("parents_education"), expand=True, max_length=100)
        social_help_field = ft.TextField(label=t("social_help"), expand=True, max_length=100)
        expelled_status_field = ft.TextField(label=t("expelled_status"), expand=True, max_length=100)
        order_number_field = ft.TextField(label=t("order_number"), expand=True, max_length=100)
        
        # Выпадающие списки для групп и курсов
        group_dropdown = ft.Dropdown(
            label=t("group"),
            options=[ft.dropdown.Option(group) for group in groups],
            expand=True,
            autofocus=False
        )
        
        course_dropdown = ft.Dropdown(
            label=t("course"),
            options=[ft.dropdown.Option(course) for course in courses],
            expand=True,
            autofocus=False
        )
        
        # Функция закрытия диалога
        def close_add_dialog(e):
            dialog.close()
            page.update()
        
        # Функция для сохранения нового студента
        def save_student(e):
            print("Пытаемся сохранить студента...")
            
            # Валидация ввода
            if not full_name_field.value or not full_name_field.value.strip():
                show_snackbar(page, t("error_empty_name"), is_error=True)
                return
            
            # Улучшенная валидация даты
            if not date_field.value:
                show_snackbar(page, t("error_empty_date"), is_error=True)
                date_field.error_text = t("error_empty_date")
                page.update()
                return
            
            # Проверяем формат даты
            try:
                birth_date = datetime.datetime.strptime(date_field.value, "%Y-%m-%d").date()
                today = datetime.datetime.now().date()
                
                # Проверяем, не в будущем ли дата
                if birth_date > today:
                    show_snackbar(page, t("error_future_date"), is_error=True)
                    date_field.error_text = t("error_future_date")
                    page.update()
                    return
                    
                # Проверяем, не слишком ли старая дата (больше 100 лет)
                date_100_years_ago = datetime.datetime.now().replace(year=today.year - 100).date()
                if birth_date < date_100_years_ago:
                    show_snackbar(page, t("error_too_old_date"), is_error=True)
                    date_field.error_text = t("error_too_old_date")
                    page.update()
                    return
            except ValueError:
                show_snackbar(page, t("error_invalid_date_format"), is_error=True)
                date_field.error_text = t("error_invalid_date_format")
                page.update()
                return
            
            if not school_field.value or not school_field.value.strip():
                show_snackbar(page, t("error_empty_school"), is_error=True)
                return
            
            if not region_field.value or not region_field.value.strip():
                show_snackbar(page, t("error_empty_region"), is_error=True)
                return
            
            if not city_field.value or not city_field.value.strip():
                show_snackbar(page, t("error_empty_city"), is_error=True)
                return
            
            if not group_dropdown.value:
                show_snackbar(page, t("error_empty_group"), is_error=True)
                return
            
            if not course_dropdown.value:
                show_snackbar(page, t("error_empty_course"), is_error=True)
                return
            
            # Показать диалог загрузки при сохранении
            saving_dialog = ft.AlertDialog(
                title=ft.Text(t("saving"), text_align=ft.TextAlign.CENTER),
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Text(t("saving_student_data"), text_align=ft.TextAlign.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            )
            page.dialog = saving_dialog
            saving_dialog.open = True
            page.update()
            
            try:
                # Сохраняем данные в БД
                conn = connect_to_db()
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO students (
                        full_name, date_of_birth, origin_school, region, district, city, address, 
                        parents_name, factual_address, hobbies, nationality, citizenship, 
                        residence_permit, document_expiry, social_status, orphan_status, 
                        disability_status, family_support, previous_residence, current_residence, 
                        housing_type, parents_education, social_help, expelled_status, order_number, 
                        group_name, course_number
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                cursor.execute(
                    query,
                    (
                        full_name_field.value.strip(),
                        date_field.value,
                        school_field.value.strip(),
                        region_field.value.strip(),
                        district_field.value.strip() if district_field.value else "",
                        city_field.value.strip(),
                        address_field.value.strip() if address_field.value else "",
                        parents_name_field.value.strip() if parents_name_field.value else "",
                        factual_address_field.value.strip() if factual_address_field.value else "",
                        hobbies_field.value.strip() if hobbies_field.value else "",
                        nationality_field.value.strip() if nationality_field.value else "",
                        citizenship_field.value.strip() if citizenship_field.value else "",
                        residence_permit_field.value.strip() if residence_permit_field.value else "",
                        document_expiry_field.value.strip() if document_expiry_field.value else "",
                        social_status_field.value.strip() if social_status_field.value else "",
                        orphan_status_field.value.strip() if orphan_status_field.value else "",
                        disability_status_field.value.strip() if disability_status_field.value else "",
                        family_support_field.value.strip() if family_support_field.value else "",
                        previous_residence_field.value.strip() if previous_residence_field.value else "",
                        current_residence_field.value.strip() if current_residence_field.value else "",
                        housing_type_field.value.strip() if housing_type_field.value else "",
                        parents_education_field.value.strip() if parents_education_field.value else "",
                        social_help_field.value.strip() if social_help_field.value else "",
                        expelled_status_field.value.strip() if expelled_status_field.value else "",
                        order_number_field.value.strip() if order_number_field.value else "",
                        group_dropdown.value,
                        int(course_dropdown.value)
                    )
                )
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Закрываем диалог
                dialog.close()
                
                # Обновляем список студентов
                update_students_list(page)
                
                # Показываем уведомление об успешном добавлении
                show_snackbar(page, t("student_added"))
                
            except Exception as db_error:
                print(f"Ошибка сохранения студента: {db_error}")
                page.dialog.open = False
                page.update()
                show_snackbar(page, f"{t('error_adding_student')}: {str(db_error)}", is_error=True)
        
        # Создаем основные поля
        basic_fields = [
            full_name_field,
            ft.Row([
                date_field,
                ft.IconButton(
                    icon=ft.icons.CALENDAR_TODAY,
                    tooltip=t("select_date"),
                    on_click=show_date_picker
                )
            ], spacing=0),
            school_field,
            region_field,
            district_field,
            city_field,
        ]
        
        # Дополнительные поля
        additional_fields = [
            address_field,
            parents_name_field,
            factual_address_field,
            hobbies_field,
        ]
        
        # Еще больше дополнительных полей
        more_fields = [
            nationality_field,
            citizenship_field,
            residence_permit_field,
            document_expiry_field,
            social_status_field,
            orphan_status_field,
            disability_status_field,
            family_support_field,
        ]
        
        # Поля про проживание
        residence_fields = [
            previous_residence_field,
            current_residence_field,
            housing_type_field,
            parents_education_field,
            social_help_field,
            expelled_status_field,
            order_number_field,
        ]
        
        # Группа и курс
        group_course_fields = [
            ft.Row([
                group_dropdown,
                course_dropdown,
            ], spacing=10)
        ]
        
        # Создаем вкладки для организации данных
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text=t("basic_info"),
                    content=ft.Column(basic_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("additional_info"),
                    content=ft.Column(additional_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("more_info"),
                    content=ft.Column(more_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("residence_info"),
                    content=ft.Column(residence_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("group_course"),
                    content=ft.Column(group_course_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
            ],
            height=450,
            expand=True,
        )
        
        # Создаем кнопки действий
        dialog_actions = [
            ft.TextButton(t("cancel"), on_click=close_add_dialog),
            ft.ElevatedButton(
                text=t("save"),
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                on_click=save_student,
            ),
        ]
        
        # Создаем диалог с помощью CustomDialog
        dialog = CustomDialog(
            page=page,
            title=t("add_student"),
            content=tabs,
            actions=dialog_actions
        )
        
        # Закрываем диалог загрузки и показываем основной диалог
        loading_dialog.open = False
        page.update()
        dialog.open()
        
    except Exception as e:
        print(f"Ошибка при создании диалога: {e}")
        traceback.print_exc()
        # Закрываем диалог загрузки и показываем ошибку
        loading_dialog.open = False
        page.update()
        show_snackbar(page, f"{t('error_loading_dialog')}: {str(e)}", is_error=True)

# Функция для создания улучшенных уведомлений
def show_snackbar(page, message, is_error=False):
    """
    Показывает улучшенное уведомление SnackBar с иконками и форматированием
    """
    color = ft.colors.RED if is_error else ft.colors.GREEN
    icon = ft.icons.ERROR_OUTLINE if is_error else ft.icons.CHECK_CIRCLE
    
    page.snack_bar = ft.SnackBar(
        content=ft.Row([
            ft.Icon(icon, color=color, size=20),
            ft.Text(message),
        ], spacing=10),
        bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK),
        duration=3000,
        open=True
    )
    page.update()

# Общий метод создания диалоговых форм для студентов с решением проблемы прокрутки
def create_student_form_dialog(page, title, fields, actions, on_open=None):
    """
    Создает диалоговое окно с формой для студента, решая проблему с прокруткой
    """
    # Создаем ListView с auto_scroll=False, чтобы предотвратить прокрутку вниз
    form_container = ft.ListView(
        controls=fields,
        spacing=10,
        height=400,
        auto_scroll=False,  # Отключаем автоскролл
        padding=10,
    )
    
    # Кнопка прокрутки вверх
    scroll_to_top_btn = ft.IconButton(
        icon=ft.icons.ARROW_UPWARD,
        tooltip="Прокрутить вверх",
        icon_color=ft.colors.BLUE_400,
        on_click=lambda e: form_container.scroll_to(offset=0, duration=300),
    )
    
    # Создаем содержимое диалога с кнопкой прокрутки
    content = ft.Column([
        form_container,
        ft.Container(
            content=scroll_to_top_btn,
            alignment=ft.alignment.bottom_right,
            margin=ft.margin.only(right=10),
        )
    ])
    
    # Создаем и открываем диалог
    dialog = CustomDialog(
        page=page,
        title=title,
        content=content,
        actions=actions
    )
    
    def open_dialog():
        dialog.open()
        if on_open:
            on_open()
        # Устанавливаем скролл в начало после открытия диалога
        form_container.scroll_to(offset=0)
        page.update()
    
    # Возвращаем объект диалога и функцию для его открытия
    return dialog, open_dialog

def export_to_excel(page, data):
    """
    Экспортирует данные студентов в файл Excel.
    
    Args:
        page: объект страницы Flet
        data: список кортежей с данными студентов
    """
    if not EXCEL_AVAILABLE:
        show_snackbar(page, t("excel_module_error"), is_error=True)
        return
    
    try:
        # Показываем диалог выбора полей для экспорта
        show_export_options_dialog(page, data)
    except Exception as e:
        show_snackbar(page, f"{t('export_error')}: {str(e)}", is_error=True)
        traceback.print_exc()

def generate_excel_file(data, filename=None):
    """Генерирует Excel файл с данными студентов."""
    # Проверяем доступность xlsxwriter и пытаемся установить его, если он не установлен
    global EXCEL_AVAILABLE
    if not EXCEL_AVAILABLE:
        success = ensure_xlsxwriter_installed()
        if not success:
            print("xlsxwriter module not installed and installation failed")
            return None
    
    # Теперь пробуем импортировать xlsxwriter еще раз
    try:
        import xlsxwriter
    except ImportError as e:
        print(f"Failed to import xlsxwriter even after installation attempt: {e}")
        return None
    
    # Проверяем входные параметры
    if data is None or not isinstance(data, list) or len(data) == 0:
        print("Error: No data provided for Excel export")
        return None
    
    if not filename:
        print("Error: No filename provided for Excel export")
        # Создаем временное имя файла
        current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(tempfile.gettempdir(), f"students_export_{current_date}.xlsx")
        print(f"Using temporary filename: {filename}")
    
    try:
        # Убедимся, что директория существует
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        
        print(f"Creating Excel file at: {filename}")
        
        # Создаем Excel файл
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet(t("students"))
        
        # Дополнительная отладочная информация
        print(f"Created workbook and worksheet successfully")
        
        # Добавляем стили для заголовков
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#4285F4',
            'font_color': 'white',  # Заменяем 'color' на 'font_color'
            'border': 1
        })
        
        # Стиль для данных
        data_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Стиль для чередования строк
        alt_row_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#F0F8FF'  # Светло-голубой
        })
        
        # Получаем заголовки столбцов из первой строки данных
        if data and len(data) > 0 and isinstance(data[0], dict):
            headers = list(data[0].keys())
            print(f"Got {len(headers)} headers: {headers}")
            
            # Записываем заголовки
            for col, header in enumerate(headers):
                print(f"Writing header {header} at column {col}")
                worksheet.write(0, col, header, header_format)
                # Устанавливаем ширину столбца
                worksheet.set_column(col, col, max(15, len(str(header)) + 5))
            
            # Записываем данные
            for row_idx, row_data in enumerate(data):
                # Выбираем формат в зависимости от четности строки
                format_to_use = alt_row_format if row_idx % 2 == 0 else data_format
                
                for col_idx, header in enumerate(headers):
                    value = row_data.get(header, "")
                    worksheet.write(row_idx + 1, col_idx, value, format_to_use)
                
                # Дополнительная отладка для длинных данных
                if row_idx == 0 or row_idx % 100 == 0:
                    print(f"Processed row {row_idx}")
        else:
            print("Error: Invalid data format for Excel export")
            workbook.close()
            return None
        
        # Закрываем файл
        print("Closing workbook...")
        workbook.close()
        print(f"Excel file successfully exported to: {filename}")
        
        # Проверяем, что файл создан
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            print(f"File exists and has size: {os.path.getsize(filename)} bytes")
            return filename
        else:
            print(f"Error: Excel file not created or empty: {filename}")
            return None
        
    except Exception as e:
        print(f"Error generating Excel file: {e}")
        traceback.print_exc()
        # Проверяем, был ли файл создан частично и удаляем его
        try:
            if filename and os.path.exists(filename):
                os.remove(filename)
                print(f"Removed partially created file: {filename}")
        except Exception as remove_error:
            print(f"Error removing partial file: {remove_error}")
        return None

def show_export_options_dialog(page, data):
    """Отображает диалог с выбором полей для экспорта в Excel."""
    print("Opening export options dialog")
    
    # Определяем поля для экспорта и их названия
    field_options = [
        ("full_name", t("full_name")),
        ("birth_date", t("birth_date")),
        ("school", t("school")),
        ("region", t("region")),
        ("district", t("district")),
        ("city", t("city")),
        ("address", t("address")),
        ("parents_name", t("parents_name")),
        ("factual_address", t("factual_address")),
        ("hobbies", t("hobbies")),
        ("nationality", t("nationality")),
        ("citizenship", t("citizenship")),
        ("residence_permit", t("residence_permit")),
        ("document_expiry", t("document_expiry")),
        ("social_status", t("social_status")),
        ("orphan_status", t("orphan_status")),
        ("disability_status", t("disability_status")),
        ("family_support", t("family_support")),
        ("previous_residence", t("previous_residence")),
        ("current_residence", t("current_residence")),
        ("housing_type", t("housing_type")),
        ("parents_education", t("parents_education")),
        ("social_help", t("social_help")),
        ("expelled_status", t("expelled_status")),
        ("order_number", t("order_number")),
        ("group", t("group")),
        ("course", t("course")),
    ]
    
    # Словарь для быстрого доступа к индексам столбцов по именам
    field_indexes = {
        "full_name": 1,
        "birth_date": 2,
        "school": 3,
        "region": 4,
        "district": 5,
        "city": 6,
        "address": 7,
        "parents_name": 8,
        "factual_address": 9,
        "hobbies": 10,
        "nationality": 11,
        "citizenship": 12,
        "residence_permit": 13,
        "document_expiry": 14,
        "social_status": 15,
        "orphan_status": 16,
        "disability_status": 17,
        "family_support": 18,
        "previous_residence": 19,
        "current_residence": 20,
        "housing_type": 21,
        "parents_education": 22,
        "social_help": 23,
        "expelled_status": 24,
        "order_number": 25,
        "group": 27,
        "course": 28,
    }
    
    # Создаем чекбоксы для выбора полей
    field_checkboxes = {}
    checkbox_columns = []
    column_controls = []
    
    # Создаем колонки с чекбоксами (3 колонки для равномерного распределения)
    for i, (field_id, field_name) in enumerate(field_options):
        checkbox = ft.Checkbox(label=field_name, value=True)
        field_checkboxes[field_id] = checkbox
        column_controls.append(checkbox)
        
        # Каждые N элементов создаем новую колонку
        if (i + 1) % 9 == 0 or i == len(field_options) - 1:
            checkbox_columns.append(ft.Column(controls=column_controls, spacing=5))
            column_controls = []
    
    # Функция для выбора/снятия выбора со всех полей
    def toggle_all(e):
        new_value = not all(checkbox.value for checkbox in field_checkboxes.values())
        for checkbox in field_checkboxes.values():
            checkbox.value = new_value
            page.update()
    
    # Функция для экспорта данных
    def export_action(e):
        # Проверяем, выбрано ли хотя бы одно поле
        selected_fields = [field_id for field_id, checkbox in field_checkboxes.items() if checkbox.value]
        
        if not selected_fields:
            show_snackbar(page, t("select_at_least_one_field"), is_error=True)
            return
        
        # Закрываем диалог
        dialog.close()
        
        # Показываем диалог загрузки
        loading_dialog = create_loading_dialog(page, t("generating_excel"))
        loading_dialog.open = True
        page.update()
        
        try:
            # Преобразуем данные для выбранных полей
            export_data = []
            for row in data:
                export_row = {}
                for field_id in selected_fields:
                    # Получаем значение из строки БД по индексу поля
                    field_index = field_indexes.get(field_id)
                    if field_index is None:
                        print(f"Warning: Field index not found for {field_id}")
                        continue
                    
                    if field_index >= len(row):
                        print(f"Warning: Index {field_index} out of range for row with length {len(row)}")
                        value = ""
                    else:
                        value = row[field_index]
                    
                    # Форматируем определенные типы данных
                    if field_id == "birth_date" or field_id == "document_expiry":
                        value = str(value) if value else ""
                    elif field_id == "orphan_status" or field_id == "disability_status" or field_id == "expelled_status":
                        value = "✓" if value else "✗"
                    else:
                        value = str(value) if value is not None else ""
                    
                    # Добавляем в словарь с переведенным названием поля
                    translated_field_name = next((name for fid, name in field_options if fid == field_id), field_id)
                    export_row[translated_field_name] = value
                
                export_data.append(export_row)
            
            # Проверяем, есть ли данные для экспорта
            if not export_data:
                show_snackbar(page, f"{t('export_error')}: {t('no_data')}", is_error=True)
                loading_dialog.open = False
                page.update()
                return
            
            # Создаем имя файла с текущей датой и временем
            current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"students_export_{current_date}.xlsx"
            
            # Создаем полный путь к файлу в папке Downloads
            home_dir = os.path.expanduser("~")
            downloads_dir = os.path.join(home_dir, "Downloads")
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            
            file_path = os.path.join(downloads_dir, filename)
            
            # Создаем и сохраняем файл Excel
            export_path = generate_excel_file(export_data, file_path)
            
            # Закрываем диалог загрузки
            loading_dialog.open = False
            page.update()
            
            # Проверяем, был ли успешно создан файл
            if export_path is None:
                show_snackbar(page, f"{t('export_error')}: {t('excel_module_error')}", is_error=True)
                return
            
            # Показываем сообщение об успешном экспорте
            show_snackbar(page, f"{t('excel_exported_successfully')}: {export_path}", is_error=False)
            
            # Открываем файл с помощью системного приложения по умолчанию
            import subprocess
            import platform
            
            try:
                system = platform.system()
                if system == 'Darwin':  # macOS
                    subprocess.call(('open', export_path))
                elif system == 'Windows':
                    os.startfile(export_path)
                else:  # Linux
                    subprocess.call(('xdg-open', export_path))
                    
                print(f"Excel file opened: {export_path}")
            except Exception as open_error:
                print(f"Error opening Excel file: {open_error}")
                # Если не удалось открыть файл, просто показываем путь к нему
                show_snackbar(page, f"{t('excel_file_saved')}: {export_path}", is_error=False)
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            traceback.print_exc()
            
            # Показываем сообщение об ошибке
            show_snackbar(page, f"{t('export_error')}: {str(e)}", is_error=True)
            
        finally:
            # Закрываем диалог загрузки если он ещё открыт
            if hasattr(loading_dialog, 'open') and loading_dialog.open:
                loading_dialog.open = False
                page.update()
    
    # Создаем кнопки действий
    select_all_btn = ft.TextButton(t("select_all_fields"), on_click=toggle_all)
    cancel_btn = ft.TextButton(t("cancel"), on_click=lambda e: dialog.close())
    export_btn = ft.ElevatedButton(
        t("export_excel"),
        on_click=export_action,
        bgcolor=ft.colors.GREEN,
        color=ft.colors.WHITE,
    )
    
    # Создаем содержимое диалога
    content = ft.Column(
        [
            ft.Text(t("select_fields_to_export"), weight=ft.FontWeight.BOLD, size=16),
            ft.Divider(),
            ft.Row(
                checkbox_columns,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Row(
                [select_all_btn],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        height=400,
    )
    
    # Создаем действия диалога
    actions = [
        cancel_btn,
        export_btn,
    ]
    
    # Создаем диалог с использованием CustomDialog
    dialog = CustomDialog(
        page=page,
        title=t("export_to_excel"),
        content=content,
        actions=actions
    )
    
    # Открываем диалог
    dialog.open()

# Добавим класс CustomDialog
class CustomDialog:
    def __init__(self, page, title, content, actions=None):
        self.page = page
        self.visible = False
        
        # Исправленный дизайн диалогового окна
        self.dialog = ft.Container(
            width=page.width if hasattr(page, 'width') else None,
            height=page.height if hasattr(page, 'height') else None,
            expand=True,  # Expand to fill available space
            bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK),  # Translucent background
            alignment=ft.alignment.center,  # Center the card
            content=ft.Card(
                elevation=10,  # Тень для лучшей видимости
                content=ft.Container(
                    padding=20,
                    border_radius=10,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.INFO_OUTLINE, color=ft.colors.BLUE),
                            ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800),
                        ], spacing=10),
                        ft.Divider(height=10, thickness=1, color=ft.colors.BLUE_100),
                        content,
                        ft.Divider(height=10, thickness=1, color=ft.colors.BLUE_100),
                        ft.Container(
                            content=ft.Row(
                                actions or [],
                                alignment=ft.MainAxisAlignment.END,
                                spacing=10,
                            ),
                            padding=ft.padding.only(top=10)
                        )
                    ], spacing=10),
                ),
                width=720,
            ),
        )
        
    def open(self):
        self.visible = True
        self.page.overlay.append(self.dialog)
        self.page.update()
        
    def close(self):
        self.visible = False
        try:
            self.page.overlay.remove(self.dialog)
            self.page.update()
        except:
            print("Error removing dialog from overlay")
            traceback.print_exc()

# Добавим функцию для создания диалога загрузки
def create_loading_dialog(page, message):
    """Создает и возвращает диалог с индикатором загрузки."""
    loading_dialog = ft.AlertDialog(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=4),
            ft.Text(message, text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        modal=True
    )
    page.dialog = loading_dialog
    return loading_dialog

def update_students_list(page, selected_group=None, selected_course=None, search_query=None, update_container_func=None):
    """
    Обновляет список студентов с поддержкой фильтрации и выбора вида отображения (таблица/карточки)
    """
    global view_as_cards
    
    print(f"Updating students list, view_as_cards={view_as_cards}")
    print(f"Filters: group={selected_group}, course={selected_course}, search={search_query}")
    
    # Создаем индикатор загрузки
    loading_container = ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=4),
            ft.Text(t("loading_data"), size=14, color=ft.colors.BLUE_400),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        alignment=ft.alignment.center,
        expand=True,
    )
    
    # Показываем индикатор загрузки
    if update_container_func:
        update_container_func(loading_container)
    
    try:
        # Загружаем данные студентов из БД
        conn = connect_to_db()
        if not conn:
            error_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.RED, size=60),
                    ft.Text(t("connection_error"), size=16, color=ft.colors.RED),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                alignment=ft.alignment.center,
                expand=True,
            )
            if update_container_func:
                update_container_func(error_container)
            return
        
        cursor = conn.cursor()
        
        # Строим запрос с параметрами для фильтрации
        query = """
            SELECT id, full_name, date_of_birth, origin_school, region, district, city, group_name, course_number
            FROM students
            WHERE 1=1
        """
        params = []
        
        # Добавляем фильтры если они указаны
        if selected_group:
            query += " AND group_name = %s"
            params.append(selected_group)
        
        if selected_course:
            query += " AND course_number = %s"
            params.append(selected_course)
        
        if search_query and search_query.strip():
            query += """ 
                AND (
                    LOWER(full_name) LIKE LOWER(%s) 
                    OR LOWER(origin_school) LIKE LOWER(%s)
                    OR LOWER(city) LIKE LOWER(%s)
                    OR LOWER(region) LIKE LOWER(%s)
                    OR LOWER(district) LIKE LOWER(%s)
                    OR CAST(group_name AS TEXT) LIKE LOWER(%s)
                )
            """
            search_param = f"%{search_query.strip()}%"
            params.extend([search_param] * 6)
        
        # Добавляем сортировку по имени
        query += " ORDER BY full_name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        print(f"Found {len(rows)} students")
        
        cursor.close()
        conn.close()
        
        # Проверяем, есть ли данные
        if not rows:
            no_data_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SEARCH_OFF, color=ft.colors.BLUE_GREY_300, size=60),
                    ft.Text(t("no_students_found"), size=16, color=ft.colors.BLUE_GREY_300),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                alignment=ft.alignment.center,
                expand=True,
            )
            if update_container_func:
                update_container_func(no_data_container)
            return
        
        # Проверяем, выбран ли вид карточек или таблицы
        if view_as_cards:
            # Создаем карточки для студентов
            students_grid = ft.GridView(
                expand=True,
                runs_count=3,
                max_extent=300,
                spacing=10,
                run_spacing=10,
                padding=10,
                child_aspect_ratio=1.0,
            )
            
            is_admin_user = is_admin()
            
            for row in rows:
                student_id = row[0]
                full_name = row[1] or "Без имени"
                birth_date = row[2] or "Нет данных"
                school = row[3] or "Нет данных"
                region = row[4] or "Нет данных"
                city = row[6] or "Нет данных"
                group = row[7] or "Нет группы"
                course = row[8] or "Нет курса"
                
                # Создаем карточку для студента
                card = ft.Card(
                    elevation=3,
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            # Шапка карточки с именем студента
                            ft.Container(
                                padding=ft.padding.all(10),
                                bgcolor=ft.colors.BLUE_100,
                                border_radius=ft.border_radius.all(8),
                                content=ft.Row([
                                    ft.Icon(ft.icons.PERSON, color=ft.colors.BLUE_600),
                                    ft.Text(full_name, weight=ft.FontWeight.BOLD, size=16, color=ft.colors.BLUE_800),
                                ], spacing=10),
                            ),
                            # Информация о студенте
                            ft.Container(
                                content=ft.Column([
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Text(f"{t('birth_date')}:", weight=ft.FontWeight.BOLD, size=12, color=ft.colors.BLUE_GREY_700),
                                            ft.Text(str(birth_date), size=12),
                                        ], spacing=5),
                                        margin=ft.margin.only(top=5),
                                    ),
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Text(f"{t('school')}:", weight=ft.FontWeight.BOLD, size=12, color=ft.colors.BLUE_GREY_700),
                                            ft.Text(school, size=12),
                                        ], spacing=5),
                                        margin=ft.margin.only(top=5),
                                    ),
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Text(f"{t('region')}/{t('city')}:", weight=ft.FontWeight.BOLD, size=12, color=ft.colors.BLUE_GREY_700),
                                            ft.Text(f"{region}, {city}", size=12),
                                        ], spacing=5),
                                        margin=ft.margin.only(top=5),
                                    ),
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Text(f"{t('group')}/{t('course')}:", weight=ft.FontWeight.BOLD, size=12, color=ft.colors.BLUE_GREY_700),
                                            ft.Text(f"{group}, {t('course')} {course}", size=12),
                                        ], spacing=5),
                                        margin=ft.margin.only(top=5),
                                    ),
                                ]),
                                padding=ft.padding.only(left=5, right=5, top=10, bottom=10),
                            ),
                            # Кнопки действий
                            ft.Container(
                                content=create_action_buttons(page, student_id, full_name),
                                margin=ft.margin.only(top=5),
                                alignment=ft.alignment.center,
                                width=120,  # Фиксированная ширина для кнопок
                                height=40,  # Высота для кнопок
                                padding=ft.padding.all(5),  # Отступы внутри контейнера
                            ) if is_admin_user else ft.Container(height=0),
                        ]),
                    ),
                )
                
                students_grid.controls.append(card)
            
            # Обновляем контейнер с результатами
            if update_container_func:
                update_container_func(students_grid)
                
        else:
            # Создаем таблицу для студентов
            students_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(t("full_name"), weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("birth_date"), weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("school"), weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("region"), weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("city"), weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("group"), weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("course"), weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("actions"), weight=ft.FontWeight.BOLD)),  # Удаляем параметр width
                ],
                border=ft.border.all(1, ft.colors.BLUE_200),
                vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_100),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_100),
                heading_row_height=40,
                data_row_min_height=50,
                column_spacing=5,  # Уменьшаем отступы между колонками
                width=page.width - 50 if hasattr(page, 'width') else None,
                show_checkbox_column=False,  # Убираем колонку с чекбоксами
            )
            
            is_admin_user = is_admin()
            
            for row in rows:
                student_id = row[0]
                full_name = row[1] or "Без имени"
                birth_date = row[2] or "Нет данных"
                school = row[3] or "Нет данных"
                region = row[4] or "Нет данных"
                city = row[6] or "Нет данных"
                group = row[7] or "Нет группы"
                course = row[8] or "Нет курса"
                
                # Создаем строку таблицы
                data_row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(full_name)),
                        ft.DataCell(ft.Text(str(birth_date))),
                        ft.DataCell(ft.Text(school)),
                        ft.DataCell(ft.Text(region)),
                        ft.DataCell(ft.Text(city)),
                        ft.DataCell(ft.Text(group)),
                        ft.DataCell(ft.Text(str(course))),
                        ft.DataCell(
                            ft.Container(
                                content=create_action_buttons(page, student_id, full_name),
                                padding=ft.padding.only(left=10, right=10),  # Добавляем отступы слева и справа
                                expand=True
                            )
                        ) if is_admin_user else ft.DataCell(ft.Container()),
                    ]
                )
                
                students_table.rows.append(data_row)
            
            # Создаем контейнер с прокруткой для таблицы
            table_container = ft.Container(
                content=students_table,
                padding=10,
                border_radius=10,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLUE_GREY),
                    offset=ft.Offset(2, 2),
                ),
            )
            
            # Оборачиваем в ScrollableControl вместо использования scroll в Container
            scroll_container = ft.Column(
                [table_container],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
            
            # Обновляем контейнер с результатами
            if update_container_func:
                update_container_func(scroll_container)
        
    except Exception as e:
        print(f"Ошибка загрузки данных студентов: {e}")
        traceback.print_exc()
        
        error_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.RED, size=60),
                ft.Text(f"{t('data_loading_error')}: {str(e)}", size=16, color=ft.colors.RED),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        if update_container_func:
            update_container_func(error_container)

def create_action_buttons(page, student_id, student_name=None):
    """Создает кнопки действий для студента."""
    if not is_admin():
        # Если не админ, возвращаем пустой контейнер
        return ft.Container()
    
    def on_view_details(e):
        view_student_details(page, student_id)
    
    def on_edit_student(e):
        edit_student_dialog(page, student_id)
    
    def on_delete_student(e, student_name=student_name):
        confirm_delete_student(page, student_id, student_name)
    
    # Создаем кнопки с иконками и подсказками, но меньшего размера
    view_btn = ft.IconButton(
        icon=ft.icons.VISIBILITY,
        tooltip=t("view_details"),
        icon_color=ft.colors.BLUE,
        icon_size=14,  # Ещё больше уменьшаем размер иконки
        on_click=on_view_details,
        style=ft.ButtonStyle(
            padding=ft.padding.all(2),  # Минимальные отступы
            shape=ft.RoundedRectangleBorder(radius=2),  # Меньшие скругления
        ),
    )
    
    edit_btn = ft.IconButton(
        icon=ft.icons.EDIT,
        tooltip=t("edit"),
        icon_color=ft.colors.ORANGE,
        icon_size=14,  # Ещё больше уменьшаем размер иконки
        on_click=on_edit_student,
        style=ft.ButtonStyle(
            padding=ft.padding.all(2),  # Минимальные отступы
            shape=ft.RoundedRectangleBorder(radius=2),  # Меньшие скругления
        ),
    )
    
    delete_btn = ft.IconButton(
        icon=ft.icons.DELETE,
        tooltip=t("delete"),
        icon_color=ft.colors.RED,
        icon_size=14,  # Ещё больше уменьшаем размер иконки
        on_click=on_delete_student,
        style=ft.ButtonStyle(
            padding=ft.padding.all(2),  # Минимальные отступы
            shape=ft.RoundedRectangleBorder(radius=2),  # Меньшие скругления
        ),
    )
    
    # Возвращаем Row с кнопками без отступов между ними
    return ft.Row(
        [view_btn, edit_btn, delete_btn],
        spacing=0,  # Убираем отступы между кнопками
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,  # Делаем компактный режим
        wrap=False,  # Запрещаем перенос на новую строку
    )

def confirm_delete_student(page, student_id, student_name=None):
    """Показывает диалог подтверждения удаления студента."""
    print(f"Показываем диалог подтверждения удаления для студента ID={student_id}")
    
    delete_text = t("confirm_delete_student")
    if student_name:
        delete_text = f"{delete_text}: {student_name}"
    
    def handle_confirm(e):
        dialog.close()
        delete_student(page, student_id)
    
    def handle_cancel(e):
        dialog.close()
    
    # Создаем содержимое диалога
    content = ft.Column([
        ft.Text(delete_text, size=16),
        ft.Container(
            content=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.RED, size=50),
            alignment=ft.alignment.center,
            margin=10,
        ),
        ft.Text(t("delete_warning"), color=ft.colors.RED, size=14),
    ], spacing=10)
    
    # Создаем кнопки действий
    actions = [
        ft.TextButton(t("cancel"), on_click=handle_cancel),
        ft.ElevatedButton(
            t("delete"),
            on_click=handle_confirm,
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
        ),
    ]
    
    # Создаем и показываем диалог
    dialog = CustomDialog(
        page=page,
        title=t("delete_student"),
        content=content,
        actions=actions
    )
    
    dialog.open()

def delete_student(page, student_id):
    """Удаляет студента из базы данных."""
    print(f"Удаляем студента ID={student_id}")
    
    # Показываем индикатор загрузки
    loading_dialog = ft.AlertDialog(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=4),
            ft.Text(t("deleting_student"), text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        modal=True
    )
    
    page.dialog = loading_dialog
    loading_dialog.open = True
    page.update()
    
    try:
        conn = connect_to_db()
        if not conn:
            loading_dialog.open = False
            page.update()
            show_snackbar(page, t("connection_error"), is_error=True)
            return
            
        cursor = conn.cursor()
        
        # Удаляем студента
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        
        # Проверяем, было ли удаление успешным
        if cursor.rowcount > 0:
            conn.commit()
            cursor.close()
            conn.close()
            
            # Закрываем диалог загрузки
            loading_dialog.open = False
            page.update()
            
            # Показываем сообщение об успешном удалении и обновляем список
            show_snackbar(page, t("student_deleted"))
            update_students_list(page)
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            
            # Закрываем диалог загрузки
            loading_dialog.open = False
            page.update()
            
            # Показываем сообщение об ошибке
            show_snackbar(page, t("student_not_found"), is_error=True)
        
    except Exception as e:
        print(f"Ошибка удаления студента: {e}")
        
        # Закрываем диалог загрузки
        loading_dialog.open = False
        page.update()
        
        # Показываем сообщение об ошибке
        show_snackbar(page, f"{t('delete_error')}: {str(e)}", is_error=True)

def add_student_dialog(page):
    """Диалог для добавления нового студента."""
    print("Открываем диалог добавления студента")
    
    # Проверка прав администратора
    is_admin_user = is_admin()
    if not is_admin_user:
        show_snackbar(page, t("admin_only"), is_error=True)
        return
    
    # Показываем индикатор загрузки
    loading_dialog = ft.AlertDialog(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=4),
            ft.Text(t("loading_data"), text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        modal=True
    )
    
    page.dialog = loading_dialog
    loading_dialog.open = True
    page.update()
    
    try:
        # Загружаем списки групп и курсов
        conn = connect_to_db()
        if not conn:
            loading_dialog.open = False
            page.update()
            show_snackbar(page, t("connection_error"), is_error=True)
            return
            
        cursor = conn.cursor()
        
        # Загружаем список групп
        cursor.execute("SELECT DISTINCT group_name FROM students ORDER BY group_name")
        groups = [row[0] for row in cursor.fetchall()]
        
        # Загружаем список курсов
        cursor.execute("SELECT DISTINCT course_number FROM students ORDER BY course_number")
        courses = [str(row[0]) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        # Создаем поля формы
        full_name_field = ft.TextField(
            label=t("full_name"), 
            autofocus=True,
            expand=True,
            max_length=100
        )
        
        # Создаем DatePicker и поле для отображения даты
        date_picker = ft.DatePicker(
            first_date=datetime.datetime(1990, 1, 1),
            last_date=datetime.datetime.now(),
        )
        page.overlay.append(date_picker)
        
        date_field = ft.TextField(
            label=t("birth_date"),
            read_only=True,
            expand=True,
            hint_text="YYYY-MM-DD"
        )
        
        # Функция для открытия выбора даты
        def show_date_picker(_):
            date_picker.open = True
            page.update()
        
        # Устанавливаем обработчик нажатия на поле даты
        date_field.on_tap = show_date_picker
        
        # Функция обработки выбранной даты
        def on_date_selected(e):
            selected_date = date_picker.value
            
            # Валидация даты: она должна быть в прошлом и не ранее 100 лет назад
            if selected_date:
                today = datetime.datetime.now().date()
                date_100_years_ago = datetime.datetime.now().replace(year=today.year - 100).date()
                
                selected_date_obj = selected_date.date() if hasattr(selected_date, 'date') else selected_date
                
                if selected_date_obj > today:
                    show_snackbar(page, t("error_future_date"), is_error=True)
                    date_field.error_text = t("error_future_date")
                    date_field.value = ""
                elif selected_date_obj < date_100_years_ago:
                    show_snackbar(page, t("error_too_old_date"), is_error=True)
                    date_field.error_text = t("error_too_old_date")
                    date_field.value = ""
                else:
                    # Дата валидна
                    date_field.value = selected_date.strftime("%Y-%m-%d")
                    date_field.error_text = None
            else:
                date_field.value = ""
            
            page.update()
        
        # Устанавливаем обработчик изменения даты
        date_picker.on_change = on_date_selected
        
        # Основные поля
        school_field = ft.TextField(label=t("school"), expand=True, max_length=100)
        region_field = ft.TextField(label=t("region"), expand=True, max_length=100)
        district_field = ft.TextField(label=t("district"), expand=True, max_length=100)
        city_field = ft.TextField(label=t("city"), expand=True, max_length=100)
        
        # Дополнительные поля
        address_field = ft.TextField(label=t("address"), expand=True, max_length=100)
        parents_name_field = ft.TextField(label=t("parents_name"), expand=True, max_length=100)
        factual_address_field = ft.TextField(label=t("factual_address"), expand=True, max_length=100)
        hobbies_field = ft.TextField(label=t("hobbies"), expand=True, max_length=100)
        
        # Еще больше дополнительных полей
        nationality_field = ft.TextField(label=t("nationality"), expand=True, max_length=100)
        citizenship_field = ft.TextField(label=t("citizenship"), expand=True, max_length=100)
        residence_permit_field = ft.TextField(label=t("residence_permit"), expand=True, max_length=100)
        document_expiry_field = ft.TextField(label=t("document_expiry"), expand=True, max_length=100)
        social_status_field = ft.TextField(label=t("social_status"), expand=True, max_length=100)
        orphan_status_field = ft.TextField(label=t("orphan_status"), expand=True, max_length=100)
        disability_status_field = ft.TextField(label=t("disability_status"), expand=True, max_length=100)
        family_support_field = ft.TextField(label=t("family_support"), expand=True, max_length=100)
        previous_residence_field = ft.TextField(label=t("previous_residence"), expand=True, max_length=100)
        current_residence_field = ft.TextField(label=t("current_residence"), expand=True, max_length=100)
        housing_type_field = ft.TextField(label=t("housing_type"), expand=True, max_length=100)
        parents_education_field = ft.TextField(label=t("parents_education"), expand=True, max_length=100)
        social_help_field = ft.TextField(label=t("social_help"), expand=True, max_length=100)
        expelled_status_field = ft.TextField(label=t("expelled_status"), expand=True, max_length=100)
        order_number_field = ft.TextField(label=t("order_number"), expand=True, max_length=100)
        
        # Выпадающие списки для групп и курсов
        group_dropdown = ft.Dropdown(
            label=t("group"),
            options=[ft.dropdown.Option(group) for group in groups],
            expand=True,
            autofocus=False
        )
        
        course_dropdown = ft.Dropdown(
            label=t("course"),
            options=[ft.dropdown.Option(course) for course in courses],
            expand=True,
            autofocus=False
        )
        
        # Функция закрытия диалога
        def close_add_dialog(e):
            dialog.close()
            page.update()
        
        # Функция для сохранения нового студента
        def save_student(e):
            # Валидация ввода
            if not full_name_field.value or not full_name_field.value.strip():
                show_snackbar(page, t("error_empty_name"), is_error=True)
                return
            
            # Улучшенная валидация даты
            if not date_field.value:
                show_snackbar(page, t("error_empty_date"), is_error=True)
                date_field.error_text = t("error_empty_date")
                page.update()
                return
            
            # Проверяем формат даты
            try:
                birth_date = datetime.datetime.strptime(date_field.value, "%Y-%m-%d").date()
                today = datetime.datetime.now().date()
                
                # Проверяем, не в будущем ли дата
                if birth_date > today:
                    show_snackbar(page, t("error_future_date"), is_error=True)
                    date_field.error_text = t("error_future_date")
                    page.update()
                    return
                    
                # Проверяем, не слишком ли старая дата (больше 100 лет)
                date_100_years_ago = datetime.datetime.now().replace(year=today.year - 100).date()
                if birth_date < date_100_years_ago:
                    show_snackbar(page, t("error_too_old_date"), is_error=True)
                    date_field.error_text = t("error_too_old_date")
                    page.update()
                    return
            except ValueError:
                show_snackbar(page, t("error_invalid_date_format"), is_error=True)
                date_field.error_text = t("error_invalid_date_format")
                page.update()
                return
            
            if not school_field.value or not school_field.value.strip():
                show_snackbar(page, t("error_empty_school"), is_error=True)
                return
            
            if not region_field.value or not region_field.value.strip():
                show_snackbar(page, t("error_empty_region"), is_error=True)
                return
            
            if not city_field.value or not city_field.value.strip():
                show_snackbar(page, t("error_empty_city"), is_error=True)
                return
            
            if not group_dropdown.value:
                show_snackbar(page, t("error_empty_group"), is_error=True)
                return
            
            if not course_dropdown.value:
                show_snackbar(page, t("error_empty_course"), is_error=True)
                return
            
            # Показать диалог загрузки при сохранении
            saving_dialog = ft.AlertDialog(
                content=ft.Column([
                    ft.ProgressRing(width=40, height=40, stroke_width=4),
                    ft.Text(t("saving_student_data"), text_align=ft.TextAlign.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                modal=True
            )
            page.dialog = saving_dialog
            saving_dialog.open = True
            page.update()
            
            try:
                # Сохраняем данные в БД
                conn = connect_to_db()
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO students (
                        full_name, date_of_birth, origin_school, region, district, city,
                        address, group_name, course_number
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                cursor.execute(
                    query,
                    (
                        full_name_field.value.strip(),
                        date_field.value,
                        school_field.value.strip(),
                        region_field.value.strip(),
                        district_field.value.strip() if district_field.value else "",
                        city_field.value.strip(),
                        address_field.value.strip() if address_field.value else "",
                        group_dropdown.value,
                        int(course_dropdown.value)
                    )
                )
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Закрываем диалог
                dialog.close()
                
                # Обновляем список студентов
                update_students_list(page)
                
                # Показываем уведомление об успешном добавлении
                show_snackbar(page, t("student_added"))
                
            except Exception as db_error:
                print(f"Ошибка сохранения студента: {db_error}")
                saving_dialog.open = False
                page.update()
                show_snackbar(page, f"{t('error_adding_student')}: {str(db_error)}", is_error=True)
        
        # Создаем основные поля
        basic_fields = [
            full_name_field,
            ft.Row([
                date_field,
                ft.IconButton(
                    icon=ft.icons.CALENDAR_TODAY,
                    tooltip=t("select_date"),
                    on_click=show_date_picker
                )
            ], spacing=0),
            school_field,
            region_field,
            district_field,
            city_field,
        ]
        
        # Дополнительные поля
        additional_fields = [
            address_field,
            parents_name_field,
            factual_address_field,
            hobbies_field,
        ]
        
        # Еще больше дополнительных полей
        more_fields = [
            nationality_field,
            citizenship_field,
            residence_permit_field,
            document_expiry_field,
            social_status_field,
            orphan_status_field,
            disability_status_field,
            family_support_field,
        ]
        
        # Поля про проживание
        residence_fields = [
            previous_residence_field,
            current_residence_field,
            housing_type_field,
            parents_education_field,
            social_help_field,
            expelled_status_field,
            order_number_field,
        ]
        
        # Группа и курс
        group_course_fields = [
            ft.Row([
                group_dropdown,
                course_dropdown,
            ], spacing=10)
        ]
        
        # Создаем вкладки для организации данных
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text=t("basic_info"),
                    content=ft.Column(basic_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("additional_info"),
                    content=ft.Column(additional_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("more_info"),
                    content=ft.Column(more_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("residence_info"),
                    content=ft.Column(residence_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text=t("group_course"),
                    content=ft.Column(group_course_fields, spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
            ],
            height=450,
            expand=True,
        )
        
        # Создаем кнопки действий
        dialog_actions = [
            ft.TextButton(t("cancel"), on_click=close_add_dialog),
            ft.ElevatedButton(
                text=t("save"),
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                on_click=save_student,
            ),
        ]
        
        # Создаем диалог с помощью CustomDialog
        dialog = CustomDialog(
            page=page,
            title=t("add_student"),
            content=tabs,
            actions=dialog_actions
        )
        
        # Закрываем диалог загрузки и показываем основной диалог
        loading_dialog.open = False
        page.update()
        dialog.open()
        
    except Exception as e:
        print(f"Ошибка при создании диалога: {e}")
        traceback.print_exc()
        # Закрываем диалог загрузки и показываем ошибку
        loading_dialog.open = False
        page.update()
        show_snackbar(page, f"{t('error_loading_dialog')}: {str(e)}", is_error=True)

# Экспортируем функцию students_screen для использования в других модулях
def students_screen(page):
    """Функция для отображения экрана управления студентами."""
    global view_as_cards
    
    is_admin_user = is_admin()
    print(f"Loading students screen, is_admin: {is_admin_user}")
    
    # Create the content container first
    content = ft.Column(
        controls=[],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )
    
    # Создаем индикатор загрузки
    loading_container = ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=4),
            ft.Text("Загрузка данных...", size=14, color=ft.colors.BLUE_400),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        alignment=ft.alignment.center,
        expand=True,
    )
    
    search_field = ft.TextField(
        label=t("search"),
        hint_text=t("search_hint"),
        width=350,
        border_radius=ft.border_radius.all(8),
        prefix_icon=ft.icons.SEARCH,
    )

    def apply_search(e):
        # Отключаем кнопку на время поиска
        search_btn.disabled = True
        search_btn.icon = ft.icons.HOURGLASS_EMPTY
        page.update()
        
        print(f"Searching for: {search_field.value}")
        update_students_list(page, search_query=search_field.value)
        
        # Восстанавливаем кнопку после завершения поиска
        search_btn.disabled = False
        search_btn.icon = ft.icons.SEARCH
        page.update()

    def reset_filter(e):
        # Отключаем кнопку на время сброса
        reset_filter_btn.disabled = True
        reset_filter_btn.icon = ft.icons.HOURGLASS_EMPTY
        page.update()
        
        print("Resetting filters")
        search_field.value = ""
        update_students_list(page)
        show_snackbar(page, t("filters_reset"))
        
        # Восстанавливаем кнопку после завершения
        reset_filter_btn.disabled = False
        reset_filter_btn.icon = ft.icons.CLEAR
        page.update()

    def handle_add_student(e):
        print("Add student button clicked")
        add_student_dialog(page)
        
    def handle_select_group(e):
        print("Select group button clicked")
        select_group_course_dialog(page)
        
    def handle_export_excel(e):
        print("Export to Excel button clicked")
        
        # Проверяем доступность xlsxwriter и пытаемся установить, если не установлен
        if not EXCEL_AVAILABLE and not ensure_xlsxwriter_installed():
            show_snackbar(page, t("excel_module_error"), is_error=True)
            return
        
        # Показываем индикатор загрузки
        loading_dialog = create_loading_dialog(page, t("loading_data"))
        page.dialog = loading_dialog
        loading_dialog.open = True
        page.update()
        
        # Запускаем загрузку всех данных для экспорта
        try:
            conn = connect_to_db()
            if not conn:
                # Закрываем диалог загрузки
                loading_dialog.open = False
                page.update()
                show_snackbar(page, t("connection_error"), is_error=True)
                return
                
            cursor = conn.cursor()
            
            # Используем тот же запрос что и для отображения, но с фильтрами
            query = """
                SELECT * FROM students
                WHERE 1=1
            """
            params = []
            
            if search_field.value and search_field.value.strip():
                query += """ 
                    AND (
                        LOWER(full_name) LIKE LOWER(%s) 
                        OR LOWER(origin_school) LIKE LOWER(%s)
                        OR LOWER(city) LIKE LOWER(%s)
                        OR LOWER(region) LIKE LOWER(%s)
                        OR LOWER(district) LIKE LOWER(%s)
                        OR CAST(group_name AS TEXT) LIKE LOWER(%s)
                    )
                """
                search_param = f"%{search_field.value.strip()}%"
                params.extend([search_param] * 6)
            
            cursor.execute(query, params)
            data = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Закрываем диалог загрузки
            loading_dialog.open = False
            page.update()
            
            if data:
                export_to_excel(page, data)
            else:
                show_snackbar(page, "Нет данных для экспорта", is_error=True)
            
        except Exception as e:
            # Закрываем диалог загрузки, если он открыт
            if hasattr(loading_dialog, 'open') and loading_dialog.open:
                loading_dialog.open = False
                page.update()
                
            print(f"Ошибка при загрузке данных для экспорта: {e}")
            show_snackbar(page, f"Ошибка при загрузке данных: {str(e)}", is_error=True)
    
    def toggle_view(e):
        """Переключает вид отображения между картами и таблицей"""
        global view_as_cards
        view_as_cards = not view_as_cards
        
        # Обновляем текст на кнопке
        toggle_view_btn.text = t("view_as_list") if view_as_cards else t("view_as_cards")
        
        # Обновляем список студентов
        update_students_list(page)
        
        # Показываем сообщение о смене вида
        message = t("view_changed_to_cards") if view_as_cards else t("view_changed_to_list")
        show_snackbar(page, message)
    
    # Создаем кнопки для доступа из обработчиков
    search_btn = ft.IconButton(
        icon=ft.icons.SEARCH,
        tooltip=t("search"),
        icon_color=ft.colors.WHITE,
        bgcolor=ft.colors.BLUE_600,
        on_click=apply_search,
    )
    
    # Кнопка переключения вида отображения
    toggle_view_btn = ft.ElevatedButton(
        text=t("view_as_cards") if not view_as_cards else t("view_as_list"),
        icon=ft.icons.VIEW_MODULE if not view_as_cards else ft.icons.VIEW_LIST,
        on_click=toggle_view,
        bgcolor=ft.colors.BLUE_300,
        color=ft.colors.WHITE,
    )
        
    # Вернулись к более простому стилю кнопок с иконками
    add_student_btn = ft.IconButton(
        icon=ft.icons.ADD,
        tooltip=t("add_student"),
        icon_color=ft.colors.WHITE,
        bgcolor=ft.colors.GREEN,
        on_click=handle_add_student,
    )
    
    select_group_btn = ft.IconButton(
        icon=ft.icons.FILTER_LIST,
        tooltip=t("filters"),
        icon_color=ft.colors.WHITE,
        bgcolor=ft.colors.ORANGE,
        on_click=handle_select_group,
    )
    
    export_excel_btn = ft.IconButton(
        icon=ft.icons.DOWNLOAD,
        tooltip=t("export_excel"),
        icon_color=ft.colors.WHITE,
        bgcolor=ft.colors.BLUE_900,
        on_click=handle_export_excel,
    )
    
    reset_filter_btn = ft.IconButton(
        icon=ft.icons.CLEAR,
        tooltip=t("reset_filters"),
        icon_color=ft.colors.WHITE,
        bgcolor=ft.colors.RED,
        on_click=reset_filter,
    )
    
    # Создаем строку поиска с кнопками
    search_container = ft.Container(
        content=ft.Row(
            [
                search_field,
                search_btn,
                reset_filter_btn,
                # Кнопка переключения вида
                toggle_view_btn
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        ),
        padding=ft.padding.only(left=20, right=20, bottom=10),
    )
    
    # Создаем строку с кнопками действий
    action_container = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    t("students_management"),
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_900
                ),
                ft.Container(expand=True),  # Spacer
                select_group_btn,
                ft.Container(width=5),  # Small spacer between buttons
                export_excel_btn,
                ft.Container(width=5),  # Small spacer between buttons
            ] + ([add_student_btn] if is_admin_user else []),  # Добавляем кнопку только администраторам
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.only(left=20, right=20, top=10),
    )
    
    # Добавляем контейнер для результатов поиска
    results_container = ft.Container(
        content=loading_container,  # Изначально показываем индикатор загрузки
        expand=True,
        padding=ft.padding.only(left=20, right=20, top=10, bottom=20),
    )
    
    # Добавляем элементы на страницу
    content.controls = [
        action_container,
        search_container,
        results_container,
    ]
    
    # Функция для обновления содержимого результатов
    def update_results_content(new_content):
        results_container.content = new_content
        page.update()
    
    # Начинаем загрузку данных
    update_students_list(page, update_container_func=update_results_content)
    
    return content
