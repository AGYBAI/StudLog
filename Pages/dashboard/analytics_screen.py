import flet as ft
import psycopg2

def analytics_screen(page: ft.Page):
    # Connect to the database
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch the data from the database
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    # Create a Flet app to display the analytics
    def build(page: ft.Page):
        page.title = "Analytics"
        page.vertical_alignment = ft.MainAxisAlignment.START

        # Display the overall statistics
        overall_stats = ft.Column(
            controls=[
                ft.Text("Overall Statistics"),
                ft.Row([
                    ft.Text("Total Students:"), 
                    ft.Text(str(len(data)))
                ]),
                ft.Row([
                    ft.Text("Students in System:"),
                    ft.Text(str(int(len(data) * 0.21)))
                ])
            ]
        )

        # Display the regional student distribution
        regions = {}
        for row in data:
            region = row[4]
            if region in regions:
                regions[region] += 1
            else:
                regions[region] = 1

        region_distribution = ft.Column(
            controls=[
                ft.Text("Regional Student Distribution"),
                *[ft.Row([ft.Text(region), ft.Text(str(count))]) for region, count in regions.items()]
            ]
        )

        # Combine the statistics and display them
        return ft.Column(
            controls=[overall_stats, region_distribution]
        )

    return ft.Stack(
        controls=[
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=build(page),
                        padding=ft.padding.all(20)
                    )
                ]
            )
        ]
    )

def connect_to_db():
    return psycopg2.connect(
        dbname="railway",
        user="postgres",
        password="dfFudMqjdNUrRDNEvvTVVvBaNztZfxaP",
        host="autorack.proxy.rlwy.net",
        port="33741"
    )