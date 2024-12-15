import re
import flet as ft
import os
import json
from psycopg2 import connect
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Pages.authentication.auth_screens import save_session



def profile_screen(page: ft.Page):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.CircleAvatar(
                                content=ft.Icon(ft.icons.ACCOUNT_CIRCLE, size=100),
                                radius=60,
                            ),
                            padding=ft.padding.all(16),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Данияр Канатов", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Почта e-mail:", size=16, color=ft.Colors.GREY),
                                ft.Text("example@gmail.com", size=16),
                                ft.Text("Номер телефона:", size=16, color=ft.Colors.GREY),
                                ft.Text("+7 777 777 7777", size=16),
                                ft.Text("Куратор группы:", size=16, color=ft.Colors.GREY),
                                ft.Text("ПО - 2502", size=16),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Изменить фото", icon=ft.icons.EDIT),
                        ft.ElevatedButton("Редактировать профиль", icon=ft.icons.EDIT_NOTE),
                    ],
                    spacing=16,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=24,
        ),
        padding=ft.padding.all(16),
    )