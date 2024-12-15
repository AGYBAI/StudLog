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
    page.update()  # Обновляем страницу, чтобы изменения вступили в силу

# Функция для создания кнопки выбора языка
def language_selector(page):
    # Текст, который будет отображать выбранный язык
    current_language_text = t("language")  # Получаем перевод для текущего языка

    # Создаем PopupMenuButton для выбора языка
    return ft.PopupMenuButton(
        content=ft.Text(current_language_text, size=16, weight="bold", color=ft.Colors.BLACK),  # Текст на кнопке
        items=[
            ft.PopupMenuItem(
                text="Русский",
                on_click=lambda e: change_language(page, "ru"),
            ),
            ft.PopupMenuItem(
                text="Қазақша",
                on_click=lambda e: change_language(page, "kz"),
            ),
        ],
    )
    page.update()
