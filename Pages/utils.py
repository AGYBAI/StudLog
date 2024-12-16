import flet as ft
from Pages.translations import translations  # Импортируем переводы из файла translations.py

# Глобальная переменная для текущего языка
current_language = "kz"  # По умолчанию русский язык

# Функция для получения перевода
def t(key):
    # Возвращаем перевод для текущего языка, если он существует
    return translations.get(current_language, {}).get(key, key)

# Функция для изменения языка
def change_language(page, lang):
    global current_language
    current_language = lang  # Устанавливаем новый язык
    page.update()  # Перерисовываем все элементы страницы

# Функция для создания Dropdown для выбора языка
def language_selector(page):
    return ft.Dropdown(
        width=150,  # Устанавливаем ширину выпадающего списка
        value=current_language,  # Устанавливаем текущий выбранный язык
        options=[
            ft.dropdown.Option("ru", text="Русский"),  # Опция для русского языка
            ft.dropdown.Option("kz", text="Қазақша"),  # Опция для казахского языка
        ],
        on_change=lambda e: change_language(page, e.control.value),  # Изменение языка при выборе
        border_color=ft.Colors.BLUE_600,  # Цвет обводки
        border_width=2,  # Толщина обводки
        border_radius=8,  # Скругленные углы
        text_style=ft.TextStyle(size=14, weight="bold", color=ft.Colors.BLACK),  # Стили текста
    )
