import flet as ft
import psycopg2
from psycopg2 import sql
import traceback  # Import traceback for better error reporting
from Pages.utils import t
from Pages.utils import is_admin

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
        
        # Create connection
        conn = psycopg2.connect(**db_config)
        
        # Test connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        traceback.print_exc()
        return None



def on_group_change(page, e):
    update_students_list(page, selected_group=e.control.value)
    page.update()

def on_course_change(page, e):
    update_students_list(page, selected_course=e.control.value)
    page.update()

def select_group_course_dialog(page):
    try:
        # Add debug for version and platform
        print(f"Flet version: {ft.__version__ if hasattr(ft, '__version__') else 'Unknown'}")
        print(f"Running platform: {ft.get_platform() if hasattr(ft, 'get_platform') else 'Unknown'}")
        print("Opening group/course dialog...")
        
        conn = connect_to_db()
        if not conn:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка подключения к базе данных"),
                open=True
            )
            page.update()
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

        # Create filter dialog controls with better styling
        group_dropdown = ft.Dropdown(
            label=t("select_group"),
            options=[ft.dropdown.Option(group) for group in groups],
            width=300,
        )

        course_dropdown = ft.Dropdown(
            label=t("select_course"),
            options=[ft.dropdown.Option(course) for course in courses],
            width=300,
        )
        
        # Create content for dialog
        content = ft.Column(
            controls=[
                ft.Text(t("select_filters_description"), size=16),
                ft.Container(height=10),  # Spacer
                group_dropdown,
                ft.Container(height=10),  # Spacer
                course_dropdown,
            ],
            spacing=5,
            width=350,
            height=200,
        )
        
        def apply_filters(e):
            print(f"Applying filters - Group: {group_dropdown.value}, Course: {course_dropdown.value}")
            update_students_list(
                page,
                selected_group=group_dropdown.value,
                selected_course=course_dropdown.value
            )
            # Close the dialog
            dialog.close()

        def close_dialog(e):
            print("Closing dialog")
            dialog.close()
            
        # Create actions
        actions = [
            ft.ElevatedButton(t("apply"), on_click=apply_filters),
            ft.ElevatedButton(t("cancel"), on_click=close_dialog),
        ]
        
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
        print(f"DEBUG - Error in filter dialog: {e}")  # Debug log
        traceback.print_exc()  # Print full traceback
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Ошибка загрузки фильтров: {str(e)}"),
            open=True
        )
        page.update()

def view_student_details(page, student_id):
    try:
        conn = connect_to_db()
        if not conn:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка подключения к базе данных"),
                open=True
            )
            page.update()
            return
            
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if student:
            # Create the content for the dialog - scrollable list view
            content = ft.ListView(
                controls=[
                    ft.Text(f"{t('full_name')}: {student[1]}"),
                    ft.Text(f"{t('birth_date')}: {student[2]}"),
                    ft.Text(f"{t('school')}: {student[3]}"),
                    ft.Text(f"{t('region')}: {student[4]}"),
                    ft.Text(f"{t('district')}: {student[5]}"),
                    ft.Text(f"{t('city')}: {student[6]}"),
                    ft.Text(f"{t('address')}: {student[7]}"),
                    ft.Text(f"{t('parents_name')}: {student[8]}"),
                    ft.Text(f"{t('factual_address')}: {student[9]}"),
                    ft.Text(f"{t('hobbies')}: {student[10]}"),
                    ft.Text(f"{t('nationality')}: {student[11]}"),
                    ft.Text(f"{t('citizenship')}: {student[12]}"),
                    ft.Text(f"{t('residence_permit')}: {student[13]}"),
                    ft.Text(f"{t('document_expiry')}: {student[14]}"),
                    ft.Text(f"{t('social_status')}: {student[15]}"),
                    ft.Text(f"{t('orphan_status')}: {t('yes') if student[16] else t('no')}"),
                    ft.Text(f"{t('disability_status')}: {t('yes') if student[17] else t('no')}"),
                    ft.Text(f"{t('family_support')}: {student[18]}"),
                    ft.Text(f"{t('previous_residence')}: {student[19]}"),
                    ft.Text(f"{t('current_residence')}: {student[20]}"),
                    ft.Text(f"{t('housing_type')}: {student[21]}"),
                    ft.Text(f"{t('parents_education')}: {student[22]}"),
                    ft.Text(f"{t('social_help')}: {student[23]}"),
                    ft.Text(f"{t('expelled_status')}: {t('yes') if student[24] else t('no')}"),
                    ft.Text(f"{t('order_number')}: {student[25]}"),
                    ft.Text(f"{t('group')}: {student[27] or t('no_data')}"),
                    ft.Text(f"{t('course')}: {student[28] or t('no_data')}")
                ],
                spacing=10,
                height=400,
                auto_scroll=True,
            )
            
            def close_dialog(e):
                dialog.close()
                
            # Create actions
            actions = [
                ft.ElevatedButton(t("close"), on_click=close_dialog)
            ]
            
            # Create and open the dialog
            dialog = CustomDialog(
                page=page,
                title=f"{t('student_details')}: {student[1]}",
                content=content,
                actions=actions
            )
            
            dialog.open()
            print(f"View details dialog opened for student {student_id}")
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Студент не найден"),
                open=True
            )
            page.update()
        
        cursor.close()
        conn.close()
    except Exception as e:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Ошибка просмотра: {str(e)}"),
            open=True
        )
        page.update()

def edit_student_dialog(page, student_id):
    # Check admin permissions
    is_admin_user = is_admin()
    print(f"Edit student dialog for student {student_id}, is_admin: {is_admin_user}")
    
    if not is_admin_user:
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Только администраторы могут редактировать студентов"),
            open=True
        )
        page.update()
        return
        
    try:
        conn = connect_to_db()
        if not conn:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка подключения к базе данных"),
                open=True
            )
            page.update()
            return
            
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        if student:
            # Создаем поля с текущими значениями студента
            fio_field = ft.TextField(label=t("full_name"), value=student[1])
            dob_field = ft.TextField(label=t("birth_date"), value=str(student[2]) if student[2] else "")
            school_field = ft.TextField(label=t("school"), value=student[3])
            region_field = ft.TextField(label=t("region"), value=student[4])
            district_field = ft.TextField(label=t("district"), value=student[5])
            city_field = ft.TextField(label=t("city"), value=student[6])
            address_field = ft.TextField(label=t("address"), value=student[7])
            parents_field = ft.TextField(label=t("parents_name"), value=student[8])
            factual_address_field = ft.TextField(label=t("factual_address"), value=student[9])
            hobbies_field = ft.TextField(label=t("hobbies"), value=student[10])
            nationality_field = ft.TextField(label=t("nationality"), value=student[11])
            citizenship_field = ft.TextField(label=t("citizenship"), value=student[12])
            residence_permit_field = ft.TextField(label=t("residence_permit"), value=student[13])
            document_expiry_date_field = ft.TextField(label=t("document_expiry"), value=str(student[14]) if student[14] else "")
            social_status_field = ft.TextField(label=t("social_status"), value=student[15])
            orphan_status_field = ft.Checkbox(label=t("orphan_status"), value=student[16])
            disability_status_field = ft.Checkbox(label=t("disability_status"), value=student[17])
            family_support_info_field = ft.TextField(label=t("family_support"), value=student[18])
            previous_residence_field = ft.TextField(label=t("previous_residence"), value=student[19])
            current_residence_field = ft.TextField(label=t("current_residence"), value=student[20])
            housing_type_field = ft.TextField(label=t("housing_type"), value=student[21])
            parents_job_education_field = ft.TextField(label=t("parents_education"), value=student[22])
            family_social_help_field = ft.TextField(label=t("social_help"), value=student[23])
            expelled_field = ft.Checkbox(label=t("expelled_status"), value=student[24])
            order_number_field = ft.TextField(label=t("order_number"), value=student[25])
            group_name_field = ft.TextField(label=t("group"), value=student[27] if student[27] else "")
            course_number_field = ft.TextField(label=t("course"), value=str(student[28]) if student[28] else "")

            # Create dialog content - scrollable list view
            content = ft.ListView(
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
                height=400,
                auto_scroll=True
            )

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
                    ),)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Студент успешно обновлен!"),
                        open=True
                    )
                    page.update()
                    
                    # Close dialog
                    dialog.close()
                    
                    update_students_list(page)
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Ошибка обновления: {str(ex)}"),
                        open=True
                    )
                    page.update()

            def close_dialog(e):
                dialog.close()
                
            # Create actions
            actions = [
                ft.ElevatedButton(t("save"), on_click=save_edited_student),
                ft.ElevatedButton(t("cancel"), on_click=close_dialog)
            ]
            
            # Create and open the dialog
            dialog = CustomDialog(
                page=page,
                title=t("edit_student"),
                content=content,
                actions=actions
            )
            
            dialog.open()
            print(f"Edit dialog opened for student {student_id}")
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Студент не найден"),
                open=True
            )
            page.update()
        
        cursor.close()
        conn.close()
    except Exception as e:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Ошибка редактирования: {str(e)}"),
            open=True
        )
        page.update()

def delete_student(page, student_id):
    # Check admin permissions
    is_admin_user = is_admin()
    print(f"Delete student dialog for student {student_id}, is_admin: {is_admin_user}")
    
    if not is_admin_user:
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Только администраторы могут удалять студентов"),
            open=True
        )
        page.update()
        return
        
    # Create dialog content
    content = ft.Text(t("delete_confirm_message"))
    
    def confirm_delete(e):
        try:
            conn = connect_to_db()
            if not conn:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Ошибка подключения к базе данных"),
                    open=True
                )
                page.update()
                return
                
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Студент успешно удален!"),
                open=True
            )
            page.update()
            
            # Close dialog
            dialog.close()
            
            update_students_list(page)
            
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Ошибка удаления: {str(ex)}"),
                open=True
            )
            page.update()
    
    def close_dialog(e):
        dialog.close()
        
    # Create actions
    actions = [
        ft.ElevatedButton(t("yes"), on_click=confirm_delete),
        ft.ElevatedButton(t("no"), on_click=close_dialog)
    ]
    
    # Create and open the dialog
    dialog = CustomDialog(
        page=page,
        title=t("confirm_delete"),
        content=content,
        actions=actions
    )
    
    dialog.open()
    print(f"Delete confirmation dialog opened for student {student_id}")

def create_action_buttons(student_id, page):
    is_admin_user = is_admin()
    print(f"Creating action buttons for student {student_id}, is_admin: {is_admin_user}")
    
    # Always show view button for all users
    buttons = [
        ft.IconButton(
            icon=ft.icons.VISIBILITY,
            tooltip=t("view"),
            icon_color=ft.Colors.BLUE_600,
            on_click=lambda e, sid=student_id: view_student_details(page, sid)
        )
    ]
    
    # Only admin can see edit and delete actions
    if is_admin_user:
        print("Adding edit and delete buttons for admin")
        buttons.extend([
            ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip=t("edit"),
                icon_color=ft.Colors.BLUE_600,
                on_click=lambda e, sid=student_id: edit_student_dialog(page, sid)
            ),
            ft.IconButton(
                icon=ft.icons.DELETE,
                tooltip=t("delete"),
                icon_color=ft.Colors.RED,
                on_click=lambda e, sid=student_id: delete_student(page, sid)
            )
        ])
    
    return buttons

def update_students_list(page, search_query=None, selected_group=None, selected_course=None):
    global content  # Make sure we have access to the content Column
    content.controls.clear()
    
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Build the query with all possible filters
        query = """
            SELECT id, full_name, date_of_birth, origin_school, region, district, city, group_name, course_number
            FROM students
            WHERE 1=1
        """
        params = []

        # Add search filter
        if search_query:
            query += """ 
                AND (
                    LOWER(full_name) LIKE LOWER(%s) 
                    OR LOWER(origin_school) LIKE LOWER(%s)
                    OR LOWER(city) LIKE LOWER(%s)
                    OR LOWER(district) LIKE LOWER(%s)
                    OR CAST(group_name AS TEXT) LIKE LOWER(%s)
                )
            """
            search_param = f"%{search_query}%"
            params.extend([search_param] * 5)

        # Add group filter
        if selected_group:
            query += " AND LOWER(group_name) = LOWER(%s)"
            params.append(selected_group)

        # Add course filter
        if selected_course:
            query += " AND course_number = %s"
            params.append(selected_course)

        query += " ORDER BY full_name"  # Add ordering

        print(f"DEBUG - Executing query: {query} with params: {params}")  # Debug log
        cursor.execute(query, params)
        rows = cursor.fetchall()
        print(f"DEBUG - Found {len(rows)} students")  # Debug log

        # Create data table
        students_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(t("full_name"))),
                ft.DataColumn(ft.Text(t("birth_date"))),
                ft.DataColumn(ft.Text(t("school"))),
                ft.DataColumn(ft.Text(t("district"))),
                ft.DataColumn(ft.Text(t("city"))),
                ft.DataColumn(ft.Text(t("group"))),
                ft.DataColumn(ft.Text(t("actions"))),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[1] or ''))),  # full_name
                        ft.DataCell(ft.Text(str(row[2] or ''))),  # date_of_birth
                        ft.DataCell(ft.Text(str(row[3] or ''))),  # school
                        ft.DataCell(ft.Text(str(row[5] or ''))),  # district
                        ft.DataCell(ft.Text(str(row[6] or ''))),  # city
                        ft.DataCell(ft.Text(str(row[7] or ''))),  # group
                        ft.DataCell(
                            ft.Row(
                                controls=create_action_buttons(row[0], page),
                                alignment=ft.MainAxisAlignment.CENTER,
                            )
                        ),
                    ]
                ) for row in rows
            ]
        )

        # Update the content with the new table
        content.controls.append(
            ft.Container(
                content=students_table,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                padding=10,
                expand=True,
            )
        )

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"DEBUG - Error updating students list: {e}")  # Debug log
        content.controls.append(
            ft.Text(f"Ошибка загрузки данных: {str(e)}", color="red")
        )
    finally:
        page.update()

class CustomDialog:
    def __init__(self, page, title, content, actions=None):
        self.page = page
        self.visible = False
        
        # Create a full-screen modal overlay with translucent background
        self.dialog = ft.Container(
            width=page.width if hasattr(page, 'width') else None,
            height=page.height if hasattr(page, 'height') else None,
            expand=True,  # Expand to fill available space
            bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK),  # Translucent background
            alignment=ft.alignment.center,  # Center the card
            content=ft.Card(
                elevation=10,  # Add shadow for better visibility
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=10, thickness=1),
                        content,
                        ft.Divider(height=10, thickness=1),
                        ft.Container(
                            content=ft.Row(
                                actions or [],
                                alignment=ft.MainAxisAlignment.END
                            ),
                            padding=ft.padding.only(top=10)
                        )
                    ]),
                ),
                width=720,  # Set fixed width for the card
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

def students_screen(page):
    is_admin_user = is_admin()
    print(f"Loading students screen, is_admin: {is_admin_user}")
    
    search_field = ft.TextField(
        label=t("search"),
        hint_text=t("search_hint"),
        width=400,
        border_radius=ft.border_radius.all(8),
    )

    def apply_search(e):
        print(f"Searching for: {search_field.value}")
        update_students_list(page, search_query=search_field.value)
        page.update()

    def reset_filter(e):
        print("Resetting filters")
        search_field.value = ""
        update_students_list(page)
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Фильтры сброшены."),
            open=True
        )
        page.update()

    def handle_add_student(e):
        print("Add student button clicked")
        add_student_dialog(page)
        
    def handle_select_group(e):
        print("Select group button clicked")
        select_group_course_dialog(page)
        
    # Create all buttons, then decide which ones to show based on role
    add_student_btn = ft.ElevatedButton(
        t("add_student"),
        icon=ft.icons.ADD,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        on_click=handle_add_student,
    )
    
    select_group_btn = ft.ElevatedButton(
        t("select_group"),
        icon=ft.icons.SELECT_ALL,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        on_click=handle_select_group,
    )
    
    reset_filter_btn = ft.ElevatedButton(
        t("reset_filter"),
        icon=ft.icons.CLEAR,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=reset_filter,
    )
    
    # Basic controls for all users
    search_row_controls = [
        search_field,
        ft.ElevatedButton(
            t("search"),
            icon=ft.icons.SEARCH,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            on_click=apply_search,
        ),
    ]
    
    # Add buttons based on role
    print(f"Adding controls based on role, is_admin: {is_admin_user}")
    
    # All users should be able to add and select
    search_row_controls.append(add_student_btn)
    search_row_controls.append(select_group_btn)
    
    # Only admin can reset filters 
    if is_admin_user:
        search_row_controls.append(reset_filter_btn)
    
    search_row = ft.Row(
        controls=search_row_controls,
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
            ft.Text("Студенттер:", size=20, weight=ft.FontWeight.BOLD),
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
    # Add debugging for admin role
    is_admin_user = is_admin()
    print(f"Opening add student dialog, is_admin: {is_admin_user}")
    
    # Для курса сделаем выпадающий список с фиксированными значениями
    course_number_field = ft.Dropdown(
        label=t("course"),
        width=300,
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2"),
            ft.dropdown.Option("3")
        ]
    )

    # Поля для ввода данных студента (как в вашем оригинальном коде)
    fio_field = ft.TextField(label=t("full_name"))
    dob_field = ft.TextField(label=t("birth_date"))
    school_field = ft.TextField(label=t("school"))
    region_field = ft.TextField(label=t("region"))
    district_field = ft.TextField(label=t("district"))
    city_field = ft.TextField(label=t("city"))
    address_field = ft.TextField(label=t("address"))
    parents_field = ft.TextField(label=t("parents_name"))
    factual_address_field = ft.TextField(label=t("factual_address"))
    hobbies_field = ft.TextField(label=t("hobbies"))
    nationality_field = ft.TextField(label=t("nationality"))
    citizenship_field = ft.TextField(label=t("citizenship"))
    residence_permit_field = ft.TextField(label=t("residence_permit"))
    document_expiry_date_field = ft.TextField(label=t("document_expiry"))
    social_status_field = ft.TextField(label=t("social_status"))
    orphan_status_field = ft.Checkbox(label=t("orphan_status"))
    disability_status_field = ft.Checkbox(label=t("disability_status"))
    family_support_info_field = ft.TextField(label=t("family_support"))
    previous_residence_field = ft.TextField(label=t("previous_residence"))
    current_residence_field = ft.TextField(label=t("current_residence"))
    housing_type_field = ft.TextField(label=t("housing_type"))
    parents_job_education_field = ft.TextField(label=t("parents_education"))
    family_social_help_field = ft.TextField(label=t("social_help"))
    expelled_field = ft.Checkbox(label=t("expelled_status"))
    order_number_field = ft.TextField(label=t("order_number"))
    group_name_field = ft.TextField(label=t("group"))
    
    # Create dialog content - with scrollable list view
    content = ft.ListView(
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
        height=400,
        auto_scroll=True,
    )
    
    def save_student(e):
        print("Saving student data...")
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
            if not conn:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Ошибка подключения к базе данных"),
                    open=True
                )
                page.update()
                return
                
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
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Студент успешно добавлен!"),
                open=True
            )
            
            # Close dialog
            dialog.close()
            
            # Refresh student list
            update_students_list(page)
            print("Student added successfully")
        except Exception as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Ошибка при сохранении: {str(e)}"),
                open=True
            )
            page.update()
            print(f"Ошибка при сохранении данных: {e}")

    def close_dialog(e):
        print("Closing add student dialog")
        dialog.close()
        
    # Create actions
    actions = [
        ft.ElevatedButton(t("save"), on_click=save_student),
        ft.ElevatedButton(t("cancel"), on_click=close_dialog),
    ]
    
    # Create and open custom dialog
    dialog = CustomDialog(
        page=page,
        title=t("add_student"),
        content=content,
        actions=actions
    )
    
    dialog.open()
    print("Custom add student dialog should be visible now")

# Экспортируем функцию students_screen для использования в других модулях