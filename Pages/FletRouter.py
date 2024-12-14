# import flet as ft
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# from Pages.dashboard.dashboard import dashboard_screen
# from Pages.authentication.auth_screens import main


# class Router:
    

#     def __init__(self, page, ft):
#         self.page = page
#         self.ft = ft
#         self.routes = {
#             "/": lambda: main(page),
#             "/dash_screen": lambda: dashboard_screen(page),
#         }
#         self.body = ft.Container(content = self.routes['/'])


#     def route_change(self, route):
#         new_content = self.routes.get(route.route)
#         if new_content:
#             self.page.views.clear()
#             self.page.views.append(new_content())
#         else:
#             print(f"Route {route.route} not found.")





# from flet import Page, View, Container, colors, app
  # import sys
  # import os
  # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
  # from Pages.views import views_handler

  # def main(page: Page):
  #     # Функция для обработки изменения маршрута
  #     def route_change(route):
  #         print(f"Current route: {page.route}")
  #         page.views.clear()  # Очищаем текущие представления

  #         if page.route == "/":
  #             page.views.append(views_handler())
  #         elif page.route == "/login":
  #             page.views.append()
  #         else:
  #             # Страница 404 для несуществующих маршрутов
  #             page.views.append(
  #                 View(
  #                     route=page.route,
  #                     controls=[
  #                         Container(
  #                             height=800,
  #                             width=350,
  #                             bgcolor=colors.GREY,
  #                             content="404 - Page Not Found",
  #                         )
  #                     ],
  #                 )
  #             )

  #         page.update()  # Обновляем страницу после изменений

  #     # Устанавливаем обработчик изменений маршрутов
  #     page.on_route_change = route_change

  #     # Перенаправляем на корневой маршрут
  #     page.go("/")


  # app(target=main)