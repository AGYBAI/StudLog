import flet as ft
import psycopg2

def connect_to_db():
    return psycopg2.connect(
        dbname="railway",
        user="postgres",
        password="dfFudMqjdNUrRDNEvvTVVvBaNztZfxaP",
        host="autorack.proxy.rlwy.net",
        port="33741"
    )

def analyze_students():
    try:
        # Подключение к базе данных
        conn = connect_to_db()
        cursor = conn.cursor()

        # Анализ социальных статусов студентов
        cursor.execute("""
            SELECT 
                COALESCE(social_status, 'false') as status, 
                COUNT(*) as count, 
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM students), 2) as percentage
            FROM students
            GROUP BY status
            ORDER BY count DESC
        """)
        social_status_stats = cursor.fetchall()

        # Анализ статусов сирот
        cursor.execute("""
            SELECT 
                COALESCE(orphan_status, 'True') as status, 
                COUNT(*) as count, 
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM students), 2) as percentage
            FROM students
            GROUP BY status
            ORDER BY count DESC
        """)
        orphan_status_stats = cursor.fetchall()

        # Анализ национальностей
        cursor.execute("""
            SELECT 
                COALESCE(nationality, 'True') as nat, 
                COUNT(*) as count, 
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM students), 2) as percentage
            FROM students
            GROUP BY nat
            ORDER BY count DESC
            LIMIT 5
        """)
        nationality_stats = cursor.fetchall()

        # Анализ по группам
        cursor.execute("""
            SELECT 
                group_name, 
                COUNT(*) as count, 
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM students), 2) as percentage
            FROM students
            GROUP BY group_name
            ORDER BY count DESC
        """)
        group_stats = cursor.fetchall()

        # Анализ по курсам
        cursor.execute("""
            SELECT 
                course_number, 
                COUNT(*) as count, 
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM students), 2) as percentage
            FROM students
            GROUP BY course_number
            ORDER BY course_number ASC
        """)
        course_stats = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            'social_status': social_status_stats,
            'orphan_status': orphan_status_stats,
            'nationality': nationality_stats,
            'groups': group_stats,
            'courses': course_stats
        }
    except Exception as e:
        print(f"Ошибка при анализе данных: {e}")
        return {
            'social_status': [],
            'orphan_status': [],
            'nationality': [],
            'groups': [],
            'courses': []
        }

def create_pie_chart(data, chart_title):
    if not data:
        return ft.Text(f"Нет данных для {chart_title}", color=ft.colors.RED)

    sections = []
    colors = [ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.PURPLE, ft.Colors.YELLOW, ft.Colors.ORANGE]
    
    for i, (label, count, percentage) in enumerate(data):
        sections.append(
            ft.PieChartSection(
                percentage,
                title=f"{label}: {percentage}%",
                color=colors[i % len(colors)],
                radius=50,
                title_style=ft.TextStyle(
                    size=10, 
                    color=ft.Colors.BLACK, 
                    weight=ft.FontWeight.BOLD
                )
            )
        )
    
    return ft.Column([
        ft.Text(chart_title, size=20, weight=ft.FontWeight.BOLD),
        ft.PieChart(
            sections=sections,
            sections_space=0,
            center_space_radius=40,
            expand=True
        )
    ])

def analytics_screen(page):
    try:
        stats = analyze_students()

        analytics_container = ft.Column([
            ft.Text("Аналитика студентов", size=24, weight=ft.FontWeight.BOLD),
            # ft.Row([
            #     ft.Column([
            #         create_pie_chart(stats['social_status'], "Социальный статус")
            #     ], width=400),
            #     ft.Column([
            #         create_pie_chart(stats['orphan_status'], "Статус сирот")
            #     ], width=400)
            # ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Column([
                    create_pie_chart(stats['nationality'], "Топ-5 национальностей")
                ], width=400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Column([
                    create_pie_chart(stats['groups'], "Статистика по группам")
                ], width=400),
                ft.Column([
                    create_pie_chart(stats['courses'], "Статистика по курсам")
                ], width=400)
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

        return analytics_container
    except Exception as e:
        return ft.Text(f"Ошибка при загрузке аналитики: {e}", color=ft.colors.RED)