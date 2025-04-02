import flet as ft
import psycopg2
from Pages.utils import t

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
        print(f"Analytics - Attempting to connect to database at {db_config['host']}:{db_config['port']}")
        
        # Create connection
        conn = psycopg2.connect(**db_config)
        
        # Test connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        
        print("Analytics - Database connection successful!")
        return conn
    except Exception as e:
        print(f"Analytics - Database connection error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def analyze_students():
    conn = None
    try:
        # Connect to database
        conn = connect_to_db()
        if not conn:
            return {
                'error': "Could not connect to database",
                'social_status': [],
                'orphan_status': [],
                'nationality': [],
                'groups': [],
                'courses': []
            }
            
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

        return {
            'social_status': social_status_stats,
            'orphan_status': orphan_status_stats,
            'nationality': nationality_stats,
            'groups': group_stats,
            'courses': course_stats
        }
    except Exception as e:
        print(f"Ошибка при анализе данных: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'social_status': [],
            'orphan_status': [],
            'nationality': [],
            'groups': [],
            'courses': []
        }
    finally:
        if conn:
            conn.close()

def create_pie_chart(data, chart_title):
    if not data:
        return ft.Text(f"{t('no_data')} {chart_title}", color=ft.Colors.RED)

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
        
        # Check if there was an error
        if 'error' in stats:
            return ft.Column([
                ft.Text(t("analytics_title"), size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(
                        f"{t('loading_error')}: {stats['error']}", 
                        color=ft.Colors.RED_500,
                        size=16,
                        weight=ft.FontWeight.W500
                    ),
                    margin=ft.margin.only(top=20),
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        "Try Again",
                        on_click=lambda _: page.update_content(page.nav_rail.selected_index)
                    ),
                    margin=ft.margin.only(top=10),
                    alignment=ft.alignment.center
                )
            ])

        # Check if there's data to display
        has_data = (
            len(stats['nationality']) > 0 or 
            len(stats['groups']) > 0 or 
            len(stats['courses']) > 0
        )
        
        if not has_data:
            return ft.Column([
                ft.Text(t("analytics_title"), size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(
                        t("no_data"),
                        size=16,
                        weight=ft.FontWeight.W500
                    ),
                    margin=ft.margin.only(top=20),
                    alignment=ft.alignment.center
                )
            ])
            
        # Build analytics UI
        analytics_container = ft.Column([
            ft.Text(t("analytics_title"), size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    create_pie_chart(stats['nationality'], t("nationality_chart"))
                ], width=400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Column([
                    create_pie_chart(stats['groups'], t("groups_chart"))
                ], width=400),
                ft.Column([
                    create_pie_chart(stats['courses'], t("courses_chart"))
                ], width=400)
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

        return analytics_container
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ft.Column([
            ft.Text(t("analytics_title"), size=24, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Text(
                    f"{t('loading_error')}: {str(e)}", 
                    color=ft.Colors.RED_500,
                    size=16,
                    weight=ft.FontWeight.W500
                ),
                margin=ft.margin.only(top=20)
            )
        ])