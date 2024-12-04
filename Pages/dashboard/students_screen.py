import flet as ft


def students_screen():
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
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
            ),
            ft.ElevatedButton(
                "Добавить студента",
                icon=ft.icons.ADD,
                bgcolor=ft.colors.GREEN,
                color=ft.colors.WHITE,
            ),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
    )

    students_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ФИО")),
            ft.DataColumn(ft.Text("Группа")),
            ft.DataColumn(ft.Text("E-mail")),
            ft.DataColumn(ft.Text("Номер телефона")),
            ft.DataColumn(ft.Text("ИИН")),
            ft.DataColumn(ft.Text("Адрес проживания")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Сейдала Елжан Бердибек")),
                    ft.DataCell(ft.Text("ПО - 2502")),
                    ft.DataCell(ft.Text("example@gmail.com")),
                    ft.DataCell(ft.Text("+7 777 777 7777")),
                    ft.DataCell(ft.Text("09020343546")),
                    ft.DataCell(ft.Text("Кошкарбаева 23, Кв. 45")),
                ]
            ),
        ],
        heading_text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
        data_text_style=ft.TextStyle(size=12),
    )

    return ft.Column(
        controls=[
            search_row,
            ft.Divider(thickness=1, color=ft.colors.BLACK),
            ft.Text("Данные группы: ПО - 2502", size=20, weight=ft.FontWeight.BOLD),
            students_table,
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )