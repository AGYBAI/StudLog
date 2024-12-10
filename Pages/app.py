from flet import *

def main(page: Page):

    def route_change(route):
        page.views.clear()
        page.views.append(
            View(
                route=  '/',
                controls=[
                    Container(
                        height=800,
                        width= 350,
                        bgcolor='red'

                    )
                ]
              )
        )
        
        
    page.on_route_change = route_change
    page.go('/')


app(target=main)