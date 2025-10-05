import flet as ft
import mysql.connector
import random
import itertools
import datetime
import pandas as pd

def main(pg: ft.Page):
    global page
    page=pg
    page.title = "Tournament Manager"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.DEEP_PURPLE_ACCENT,
            secondary=ft.Colors.TEAL_ACCENT,
            surface=ft.Colors.GREY_900
        ),
        font_family="Roboto"
    )
    page.padding = 20
    page.update()
 
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="tournament_db"
    )
    cursor = conn.cursor(dictionary=True)
 
    def setup_database():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                tournament_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                sport VARCHAR(100),
                type ENUM('round_robin', 'knockout'),
                start_date DATE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INT AUTO_INCREMENT PRIMARY KEY,
                tournament_id INT,
                team_name VARCHAR(255),
                FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id INT AUTO_INCREMENT PRIMARY KEY,
                tournament_id INT,
                round INT,
                team1_id INT,
                team2_id INT,
                winner_team_id INT DEFAULT NULL,
                result ENUM('team1_win', 'team2_win', 'draw') DEFAULT NULL,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
                FOREIGN KEY (team1_id) REFERENCES teams(team_id) ON DELETE CASCADE,
                FOREIGN KEY (team2_id) REFERENCES teams(team_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS points_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_id INT,
                tournament_id INT,
                team_name VARCHAR(255),
                games_played INT,
                wins INT,
                losses INT,
                draws INT,
                points INT,
                FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INT AUTO_INCREMENT PRIMARY KEY,
                team_id INT,
                player_name VARCHAR(255),
                FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE
            )
        """)
 
        conn.commit()
 
    setup_database()
 
    tournament_id = None
    team_ids = []
    team_name_map = {}
    current_tournament_type = "round_robin"
    SPORT_MAX_PLAYERS = {
        "Football": 11,
        "Cricket": 11,
        "Basketball": 5,
        "Badminton": 2,
        "Hockey": 11
    }

 
    def show_snack(msg):
        page.open(ft.SnackBar(ft.Text(msg)))
 
        page.update()
 
 
    def home_view():
        return ft.View(
        route="/",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "🏆 Tournament Manager",
                            size=40,
                            weight="bold",
                            color=ft.Colors.DEEP_PURPLE_ACCENT,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Divider(height=30, color=ft.Colors.GREY_700),
                        ft.ElevatedButton(
                            text="📘 Instructions",
                            icon=ft.Icons.INFO_OUTLINE,
                            width=250,
                            bgcolor=ft.Colors.TEAL_ACCENT,
                            color=ft.Colors.BLACK,
                            on_click=lambda _: page.go("/instructions")
                        ),
                        ft.ElevatedButton(
                            text="🏆 Select Tournament",
                            icon=ft.Icons.LIST_ALT_OUTLINED,
                            width=250,
                            bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
                            color=ft.Colors.WHITE,
                            on_click=lambda _: page.go("/select")
                        ),
                        ft.ElevatedButton(
                            text="✏️ Create Tournament",
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            width=250,
                            bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
                            color=ft.Colors.WHITE,
                            on_click=lambda _: page.go("/create")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=25
                ),
                padding=40,
                border_radius=12,
                bgcolor=ft.Colors.GREY_900,
                shadow=ft.BoxShadow(
                    spread_radius=2,
                    blur_radius=10,
                    color=ft.Colors.DEEP_PURPLE_ACCENT,
                    offset=ft.Offset(2, 4)
                )
            )
        ],
        bgcolor="#111418"
    )
 
    def instructions_view():
        instructions_text = ft.Text(
        "Welcome to the Tournament Manager!\n\n"
        "• Create and manage tournaments.\n"
        "• Choose between Round Robin or Knockout formats.\n"
        "• Enter match results and view standings.\n"
        "• Track team progress and declare winners.\n\n"
        "Navigate using the buttons to create or select tournaments.",
        size=16,
        color=ft.Colors.WHITE70,
        selectable=True
    )
 
        back_button = ft.ElevatedButton(
            text="Back to Home",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: page.go("/"),
            bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
            color=ft.Colors.BLACK,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )
 
        return ft.View(
            "/instructions",
             controls=[
                ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Instructions", size=28, weight="bold", color=ft.Colors.DEEP_PURPLE_ACCENT),
                        ft.Divider(height=20, color=ft.Colors.GREY_700),
                        instructions_text,
                        ft.Divider(height=30),
                        back_button,
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                margin=ft.margin.all(20),
                bgcolor=ft.Colors.GREY_900,
                border_radius=12,
                width=500,
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=12,
                    color=ft.Colors.DEEP_PURPLE_ACCENT,
                    offset=ft.Offset(0, 0),
                    blur_style=ft.ShadowBlurStyle.OUTER,
                )
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
 
    def load_tournament(t_id):
        nonlocal tournament_id, team_ids, team_name_map, current_tournament_type
        tournament_id = t_id
        cursor.execute("SELECT type, sport FROM tournaments WHERE tournament_id = %s", (tournament_id,))
        t_data = cursor.fetchone()
        if t_data:
            current_tournament_type = t_data['type']
            current_tournament_sport = t_data['sport']
        cursor.execute("SELECT team_id, team_name FROM teams WHERE tournament_id = %s", (tournament_id,))
        teams = cursor.fetchall()
        team_ids.clear()
        team_name_map.clear()
        for t in teams:
            team_ids.append(t['team_id'])
            team_name_map[t['team_id']] = t['team_name']
        show_snack("Tournament loaded")
        page.go("/tournament")
 
    def delete_tournament(t_id):
        cursor.execute("DELETE FROM points_table WHERE tournament_id = %s", (t_id,))
        cursor.execute("DELETE FROM matches WHERE tournament_id = %s", (t_id,))
        cursor.execute("DELETE FROM teams WHERE tournament_id = %s", (t_id,))
        cursor.execute("DELETE FROM tournaments WHERE tournament_id = %s", (t_id,))
        conn.commit()
        show_snack("Tournament deleted successfully!")
        page.go("/create")
 
    def tournament_selection_view():
        cursor.execute("SELECT * FROM tournaments")
        tournaments = cursor.fetchall()
 
        tournament_cards = []
 
        for t in tournaments:
            tournament_name = t["name"]
            tournament_id = t["tournament_id"]
            tournament_sport = t["sport"] or "Unknown Sport",
 
            tournament_card = ft.Container(
                content=ft.Row(
                    [
                        ft.Column([
                            ft.Text(tournament_name, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f"Sport: {tournament_sport}", size=14, color=ft.Colors.GREY_400),
                            ft.Text(f"Tournament ID: {tournament_id}", size=14, color=ft.Colors.GREY_500),
                        ], expand=True),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.DEEP_PURPLE_ACCENT,
                            tooltip="Delete Tournament",
                            on_click=lambda e, tid=tournament_id: delete_tournament(tid)
                        ),
                        ft.ElevatedButton(
                            "Load",
                            icon=ft.Icons.OPEN_IN_NEW,
                            on_click=lambda e, tid=tournament_id: load_tournament(tid),
                            bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=15,
                margin=ft.margin.only(bottom=15),
                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                border_radius=12,
                shadow=ft.BoxShadow(
                    blur_radius=12,
                    color=ft.Colors.GREY_600,
                    spread_radius=0.5,
                    offset=ft.Offset(0, 2)
                )
            )
 
            tournament_cards.append(tournament_card)
 
        create_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, size=18),
                ft.Text("Create Tournament", weight=ft.FontWeight.BOLD)
            ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8),
            on_click=lambda _: page.go("/create"),
            bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            )
        )
 
        return ft.View(
            route="/select",
            bgcolor=ft.Colors.GREY_900,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Tournament Manager", size=32, weight="bold", color=ft.Colors.DEEP_PURPLE_ACCENT),
                            ft.Divider(height=10, color=ft.Colors.GREY_700),
                            ft.Text("Select a tournament to continue", size=18, color=ft.Colors.GREY_400),
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.Column(tournament_cards, scroll=ft.ScrollMode.AUTO, expand=True),
                            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                            create_button,
                            ft.TextButton(  # <- back to home button
                            "← Back to Home",
                            on_click=lambda _: page.go("/"),
                            style=ft.ButtonStyle(
                            text_style=ft.TextStyle(
                            color=ft.Colors.GREY_400,
                            decoration=ft.TextDecoration.UNDERLINE)))
                        ],
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    padding=20,
                    margin=ft.margin.all(15),
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    width=500,
                    alignment=ft.alignment.center,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.Colors.DEEP_PURPLE_ACCENT,
                        offset=ft.Offset(0, 0),
                        blur_style=ft.ShadowBlurStyle.OUTER,
                    )
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
 
 
    def create_tournament_view():
        tournament_name_input = ft.TextField(
            hint_text="Enter tournament name",
            hint_style=ft.TextStyle(color=ft.Colors.GREY_500)
        )
        sport_dropdown = ft.Dropdown(
            label="Select Sport",
            options=[
                ft.dropdown.Option("Football"),
                ft.dropdown.Option("Cricket"),
                ft.dropdown.Option("Basketball"),
                ft.dropdown.Option("Badminton"),
                ft.dropdown.Option("Hockey")
                ],
                value="Football",
                label_style=ft.TextStyle(size=14, weight="bold"),
            )

 
        tournament_name = ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        size=14,
                        weight="bold",
                        color=ft.Colors.GREY_400,
                        opacity=0.8,
                    ),
                    padding=ft.padding.only(bottom=5),
                ),
                tournament_name_input,
            ],
            tight=True,
        )
 
        tournament_type = ft.Dropdown(
            label="Tournament Type",
            options=[ft.dropdown.Option("round_robin"), ft.dropdown.Option("knockout")],
            value="round_robin",
            label_style=ft.TextStyle(size=14, weight="bold"),
        )
 
        selected_date = ft.Text("No date selected", italic=True, color=ft.Colors.GREY_400)
 
 
 
        def on_date_selected(e):
            if e.data:
                dt = datetime.datetime.strptime(e.data.split('T')[0], "%Y-%m-%d").date()
                selected_date.value = dt.strftime("%d %B, %Y")
                selected_date.color = ft.Colors.TEAL_ACCENT
                page.update()
 
        date_picker = ft.DatePicker(on_change=on_date_selected)
        page.overlay.append(date_picker)
 
        def open_date_picker(e):
            page.open(date_picker)
 
        pick_date_btn = ft.ElevatedButton(
            "Pick Start Date",
            icon=ft.Icons.DATE_RANGE,
            on_click=open_date_picker,
            bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
 
        def create_tournament(e):
            if selected_date.value == "No date selected":
                show_snack("Please select a valid start date.")
                return
            if not tournament_name_input.value.strip():
                show_snack("Please enter a tournament name.")
                return
 
            dt = datetime.datetime.strptime(selected_date.value, "%d %B, %Y").date()
            cursor.execute(
                "INSERT INTO tournaments (name, sport, type, start_date) VALUES (%s, %s, %s, %s)",
                (tournament_name_input.value.strip(), sport_dropdown.value, tournament_type.value, dt.isoformat())
            )
            conn.commit()
            show_snack("Tournament Created!")
            page.go("/select")
 
        create_btn = ft.ElevatedButton(
            "Create Tournament",
            icon=ft.Icons.ADD,
            on_click=create_tournament,
            bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
            color=ft.Colors.BLACK,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            width=350
        )
 
        go_select_btn = ft.TextButton(
            "Go to Select Tournament",
            on_click=lambda _: page.go("/select"),
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(
                    color=ft.Colors.GREY_400,
                    decoration=ft.TextDecoration.UNDERLINE
                )
            )
        )
 
        return ft.View(
            "/create",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Create Tournament", size=32, weight="bold", color=ft.Colors.DEEP_PURPLE_ACCENT),
                            ft.Divider(height=20, color=ft.Colors.GREY_700),
                            tournament_name,
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            tournament_type,
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            sport_dropdown,
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            pick_date_btn,
                            selected_date,
                            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                            create_btn,
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            go_select_btn,
                            ft.TextButton(
                            "← Back to Home",
                            on_click=lambda _: page.go("/"),
                            style=ft.ButtonStyle(
                            text_style=ft.TextStyle(
                            color=ft.Colors.GREY_400,
                            decoration=ft.TextDecoration.UNDERLINE)))
                        ],
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=20,
                    margin=ft.margin.all(15),
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    width=400,
                    alignment=ft.alignment.center,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.Colors.DEEP_PURPLE_ACCENT,
                        offset=ft.Offset(0, 0),
                        blur_style=ft.ShadowBlurStyle.OUTER,
                    )
                )
 
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
 
    def tournament_dashboard_view():
        return ft.View(
            "/tournament",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Tournament Dashboard",
                                size=30,
                                weight="bold",
                                color=ft.Colors.DEEP_PURPLE_ACCENT
                            ),
                            ft.Divider(height=25, color=ft.Colors.GREY_700),
                            ft.ElevatedButton("Manage Teams", on_click=lambda _: page.go("/teams"), width=300),
                            ft.ElevatedButton("Manage Fixtures & Results", on_click=lambda _: page.go("/fixtures"),
                                              width=300),
                            ft.ElevatedButton("View Points Table", on_click=lambda _: page.go("/points"), width=300),
                            ft.OutlinedButton("Back to Select Tournament", on_click=lambda _: page.go("/select"),
                                              width=300),
                        ],
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=30,
                    width=450,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.35, ft.Colors.DEEP_PURPLE_ACCENT),
                        offset=ft.Offset(2, 4)
                    )
                )
            ]
        )
 
    def team_management_view():
        team_name_input = ft.TextField(
            label="Team Names (one per line)",
            multiline=True,
            min_lines=5,
            width=400,
            hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
            text_style=ft.TextStyle(color=ft.Colors.WHITE)
        )
        team_list = ft.ListView(expand=True, spacing=5, height=250, padding=5, auto_scroll=False)
        upload_result_text = ft.Text(color=ft.Colors.DEEP_PURPLE_ACCENT)
 
        def add_team(e):
            if tournament_id is None:
                show_snack("No tournament loaded")
                return
 
            names = [name.strip() for name in team_name_input.value.strip().split('\n') if name.strip()]
            if not names:
                show_snack("Please enter at least one team name.")
                return
 
            for name in names:
                cursor.execute(
                    "INSERT INTO teams (tournament_id, team_name) VALUES (%s, %s)",
                    (tournament_id, name)
                )
                conn.commit()
                tid = cursor.lastrowid
                team_ids.append(tid)
                team_name_map[tid] = name
                team_list.controls.append(ft.Text(name, color=ft.Colors.WHITE))
 
            team_name_input.value = ""
            show_snack(f"{len(names)} team(s) added!")
            page.update()

        def upload_handler(e: ft.FilePickerResultEvent):
            if not e.files:
                return
 
            file_path = e.files[0].path
            try:
                df = pd.read_excel(file_path)
 
                if "Team Name" not in df.columns:
                    upload_result_text.value = "Excel must contain a 'Team Name' column."
                    page.update()
                    return
 
                added = 0
                for name in df["Team Name"]:
                    name = str(name).strip()
                    if name:
                        cursor.execute(
                            "INSERT INTO teams (tournament_id, team_name) VALUES (%s, %s)",
                            (tournament_id, name)
                        )
                        conn.commit()
                        tid = cursor.lastrowid
                        team_ids.append(tid)
                        team_name_map[tid] = name
                        team_list.controls.append(ft.Text(name, color=ft.Colors.WHITE))
                        added += 1
 
                upload_result_text.value = f"{added} teams imported from Excel!"
                page.update()
 
            except Exception as ex:
                upload_result_text.value = f"Error reading file: {str(ex)}"
                page.update()
 
        file_picker = ft.FilePicker(on_result=upload_handler)
        page.overlay.append(file_picker)
 
        cursor.execute("SELECT team_name FROM teams WHERE tournament_id = %s", (tournament_id,))
        for t in cursor.fetchall():
            team_list.controls.append(ft.Text(t['team_name'], color=ft.Colors.WHITE))
 
        return ft.View(
            "/teams",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Manage Teams", size=28, weight="bold", color=ft.Colors.DEEP_PURPLE_ACCENT),
                            ft.Divider(height=20, color=ft.Colors.GREY_700),
                            team_name_input,
                            ft.ElevatedButton("Add Team", on_click=add_team, width=300),
                            ft.ElevatedButton("Import from Excel",
                                              on_click=lambda _: file_picker.pick_files(allow_multiple=False),
                                              width=300),
                            upload_result_text,
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.Text("Team List:", size=16, color=ft.Colors.GREY_400),
                            ft.Container(
                                content=team_list,
                                height=250,
                                width=400,
                                bgcolor=ft.Colors.GREY_900,
                                border=ft.Border(
                                    left=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    right=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    top=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    bottom=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                ),
                                border_radius=8,
                                padding=10
                            ),
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.OutlinedButton(
                                "Back to Dashboard",
                                on_click=lambda _: page.go("/tournament"),
                                width=300,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(color=ft.Colors.DEEP_PURPLE_ACCENT, width=1),
                                    text_style=ft.TextStyle(color=ft.Colors.DEEP_PURPLE_ACCENT)
                                )
                            ),
 
                            ft.Container(height=10)
                        ],
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=30,
                    width=500,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.35, ft.Colors.DEEP_PURPLE_ACCENT),
                        offset=ft.Offset(2, 4)
                    )
                )
            ]
        )
 
    def fixture_and_results_view():
        fixtures_display = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=False,
            height=350,
            width=450,
        )
 
        generate_or_view_button = ft.ElevatedButton(text="", width=300)
 
        def check_fixtures_exist():
            cursor.execute("SELECT COUNT(*) AS count FROM matches WHERE tournament_id = %s", (tournament_id,))
            return cursor.fetchone()['count'] > 0
 
        def update_generate_button():
            if check_fixtures_exist():
                generate_or_view_button.text = "View Fixtures"
                generate_or_view_button.on_click = lambda e: load_fixtures()
            else:
                generate_or_view_button.text = "Generate Fixtures"
                generate_or_view_button.on_click = lambda \
                    e: generate_round_robin() if current_tournament_type == "round_robin" else generate_knockout()
            page.update()
 
        def generate_round_robin():
            if check_fixtures_exist():
                show_snack("Fixtures already generated.")
                return
            pairs = list(itertools.combinations(team_ids, 2))
            for round_no, (t1, t2) in enumerate(pairs, start=1):
                cursor.execute("INSERT INTO matches (tournament_id, round, team1_id, team2_id) VALUES (%s, %s, %s, %s)",
                               (tournament_id, round_no, t1, t2))
            conn.commit()
            initialize_points_table()
            show_snack("Fixtures Generated")
            update_generate_button()
            load_fixtures()
 
        def generate_knockout():
            if check_fixtures_exist():
                show_snack("Fixtures already generated.")
                return
 
            shuffled = team_ids[:]
            random.shuffle(shuffled)
 
            round_number = 1
            total_teams = len(shuffled)
 
            # If odd, give one team a bye
            if total_teams % 2 != 0:
                bye_team = shuffled.pop()
                cursor.execute(
                    "INSERT INTO matches (tournament_id, round, team1_id, team2_id, winner_team_id, result) "
                    "VALUES (%s, %s, %s, NULL, %s, %s)",
                    (tournament_id, round_number, bye_team, bye_team, 'team1_win')
                )
                update_points(bye_team, "win")  # optional, depending on how you want to score byes
 
            for i in range(0, len(shuffled), 2):
                t1 = shuffled[i]
                t2 = shuffled[i + 1]
                cursor.execute(
                    "INSERT INTO matches (tournament_id, round, team1_id, team2_id) VALUES (%s, %s, %s, %s)",
                    (tournament_id, round_number, t1, t2)
                )
 
            conn.commit()
            initialize_points_table()
            show_snack("Knockout Fixtures Generated (Bye added if odd)")
            update_generate_button()
            load_fixtures()
 
        def check_and_generate_next_knockout_round():
            cursor.execute("SELECT MAX(round) as max_round FROM matches WHERE tournament_id = %s", (tournament_id,))
            max_round = cursor.fetchone()['max_round']
            for round_num in range(1, max_round + 1):
                cursor.execute("SELECT match_id, winner_team_id FROM matches WHERE tournament_id = %s AND round = %s",
                               (tournament_id, round_num))
                matches = cursor.fetchall()
                if any(m['winner_team_id'] is None for m in matches):
                    return
                cursor.execute("SELECT COUNT(*) AS count FROM matches WHERE tournament_id = %s AND round = %s",
                               (tournament_id, round_num + 1))
                if cursor.fetchone()['count'] > 0:
                    continue
                winners = [m['winner_team_id'] for m in matches if m['winner_team_id']]
                random.shuffle(winners)
                if len(winners) == 1:
                    page.views.clear()
                    page.views.append(tournament_winner_view(winners[0]))
                    page.update()
                    return
                for i in range(0, len(winners) - 1, 2):
                    cursor.execute(
                        "INSERT INTO matches (tournament_id, round, team1_id, team2_id) VALUES (%s, %s, %s, %s)",
                        (tournament_id, round_num + 1, winners[i], winners[i + 1]))
                conn.commit()
 
        def initialize_points_table():
            for tid in team_ids:
                cursor.execute("SELECT * FROM points_table WHERE team_id = %s", (tid,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO points_table (team_id, tournament_id, team_name, games_played, wins, losses, draws, points) "
                        "SELECT team_id, %s, team_name, 0, 0, 0, 0, 0 FROM teams WHERE team_id = %s",
                        (tournament_id, tid))
            conn.commit()
 
        def update_points(team_id, result):
            if result == 'win':
                cursor.execute(
                    "UPDATE points_table SET games_played = games_played + 1, wins = wins + 1, points = points + 3 WHERE team_id = %s",
                    (team_id,))
            elif result == 'loss':
                cursor.execute(
                    "UPDATE points_table SET games_played = games_played + 1, losses = losses + 1 WHERE team_id = %s",
                    (team_id,))
            elif result == 'draw':
                cursor.execute(
                    "UPDATE points_table SET games_played = games_played + 1, draws = draws + 1, points = points + 1 WHERE team_id = %s",
                    (team_id,))
            conn.commit()
 
        def load_fixtures():
            fixtures_display.controls.clear()
            cursor.execute("""
                SELECT m.match_id, m.team1_id, m.team2_id, m.result,
                    t1.team_name AS team1, t2.team_name AS team2
                FROM matches m
                JOIN teams t1 ON m.team1_id = t1.team_id
                JOIN teams t2 ON m.team2_id = t2.team_id
                WHERE m.tournament_id = %s
            """, (tournament_id,))
            matches = cursor.fetchall()
 
            for match in matches:
                match_label = f"{match['team1']} vs {match['team2']}"
                if match['result']:
                    result_text = {
                        "team1_win": f"{match['team1']} won",
                        "team2_win": f"{match['team2']} won",
                        "draw": "Match drawn"
                    }.get(match['result'], "Result Unknown")
                    fixtures_display.controls.append(ft.Text(f"{match_label} - {result_text}", color=ft.Colors.WHITE))
                    continue
 
                match_id = match['match_id']
                t1_id = match['team1_id']
                t2_id = match['team2_id']
 
                def result_handler_factory(winner_id, loser_id, result_type, match_id, label):
                    def handler(e):
                        if result_type == "draw":
                            update_points(winner_id, "draw")
                            update_points(loser_id, "draw")
                            final_winner_id = None
                        else:
                            update_points(winner_id, "win")
                            update_points(loser_id, "loss")
                            final_winner_id = winner_id
                        cursor.execute("UPDATE matches SET result = %s, winner_team_id = %s WHERE match_id = %s",
                                       (result_type, final_winner_id, match_id))
                        conn.commit()
                        check_and_generate_next_knockout_round()
                        show_snack(f"Result recorded: {label} - {result_type.replace('_', ' ').capitalize()}")
                        load_fixtures()
                        page.update()
 
                    return handler
 
                submenu_controls = [
                    ft.MenuItemButton(
                        content=ft.Text(f"{match['team1']} Wins"),
                        on_click=result_handler_factory(t1_id, t2_id, "team1_win", match_id, match_label)
                    ),
                    ft.MenuItemButton(
                        content=ft.Text(f"{match['team2']} Wins"),
                        on_click=result_handler_factory(t2_id, t1_id, "team2_win", match_id, match_label)
                    )
                ]
 
                if current_tournament_type == "round_robin":
                    submenu_controls.append(
                        ft.MenuItemButton(
                            content=ft.Text("Draw"),
                            on_click=result_handler_factory(t1_id, t2_id, "draw", match_id, match_label)
                        )
                    )
 
                submenu = ft.SubmenuButton(
                    content=ft.Text(match_label, color=ft.Colors.WHITE),
                    controls=submenu_controls
                )
 
                fixtures_display.controls.append(submenu)
            page.update()
 
        update_generate_button()
        load_fixtures()
 
        return ft.View(
            "/fixtures",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Fixtures & Results", size=28, weight="bold", color=ft.Colors.DEEP_PURPLE_ACCENT),
                            ft.Divider(height=20, color=ft.Colors.GREY_700),
                            generate_or_view_button,
                            ft.Container(
                                content=fixtures_display,
                                height=350,
                                width=450,
                                bgcolor=ft.Colors.GREY_900,
                                border=ft.Border(
                                    left=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    right=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    top=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    bottom=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                ),
                                border_radius=8,
                                padding=10,
                            ),
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.OutlinedButton(
                                "Back to Dashboard",
                                on_click=lambda _: page.go("/tournament"),
                                width=300,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(color=ft.Colors.DEEP_PURPLE_ACCENT, width=1),
                                    text_style=ft.TextStyle(color=ft.Colors.DEEP_PURPLE_ACCENT)
                                )
                            ),
                        ],
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=30,
                    width=500,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.35, ft.Colors.DEEP_PURPLE_ACCENT),
                        offset=ft.Offset(2, 4)
                    )
                )
            ],
            bgcolor="#111418"
 
        )
 
    def points_table_view():
        points_display = ft.ListView(expand=True, spacing=5, height=250, padding=5, auto_scroll=False)
        status_text = ft.Text(color=ft.Colors.DEEP_PURPLE_ACCENT)
 
        def view_points_table(e):
            points_display.controls.clear()
            cursor.execute("""
                SELECT * FROM points_table 
                WHERE tournament_id = %s 
                ORDER BY points DESC, wins DESC
            """, (tournament_id,))
            rows = cursor.fetchall()
            if not rows:
                status_text.value = "No data available."
            else:
                status_text.value = ""
                for idx, row in enumerate(rows, start=1):
                    medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                    points_display.controls.append(
                        ft.Text(
                            f"{medal} {row['team_name']} | Played: {row['games_played']} | W: {row['wins']} | "
                            f"D: {row['draws']} | L: {row['losses']} | Points: {row['points']}",
                            color=ft.Colors.WHITE
                        )
                    )
            page.update()
 
        def reset_points(e):
            cursor.execute("""
                UPDATE points_table
                SET games_played = 0, wins = 0, losses = 0, draws = 0, points = 0
                WHERE tournament_id = %s
            """, (tournament_id,))
            conn.commit()
            show_snack("Points have been reset.")
            view_points_table(None)
 
        def declare_winner(e):
            cursor.execute("""
                SELECT team_id FROM points_table
                WHERE tournament_id = %s
                ORDER BY points DESC, wins DESC
                LIMIT 1
            """, (tournament_id,))
            winner = cursor.fetchone()
            if winner:
                page.views.clear()
                page.views.append(tournament_winner_view(winner["team_id"]))
                page.update()
            else:
                show_snack("No teams found in points table.")
 
        return ft.View(
            "/points",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Points Table", size=28, weight="bold", color=ft.Colors.DEEP_PURPLE_ACCENT),
                            ft.Divider(height=20, color=ft.Colors.GREY_700),
                            ft.Row(
                                [
                                    ft.ElevatedButton("View Points", on_click=view_points_table, width=120),
                                    ft.ElevatedButton("Reset Points", on_click=reset_points, bgcolor=ft.Colors.RED_400,
                                                      color=ft.Colors.WHITE, width=120),
                                    ft.ElevatedButton("Declare Winner", on_click=declare_winner,
                                                      bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE, width=140)
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=12
                            ),
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            status_text,
                            ft.Container(
                                content=points_display,
                                height=250,
                                width=400,
                                bgcolor=ft.Colors.GREY_900,
                                border=ft.Border(
                                    left=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    right=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    top=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                    bottom=ft.BorderSide(color=ft.Colors.GREY_800, width=1),
                                ),
                                border_radius=8,
                                padding=10,
                            ),
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.OutlinedButton(
                                "Back to Dashboard",
                                on_click=lambda _: page.go("/tournament"),
                                width=300,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(color=ft.Colors.DEEP_PURPLE_ACCENT, width=1),
                                    text_style=ft.TextStyle(color=ft.Colors.DEEP_PURPLE_ACCENT)
                                )
                            ),
                            ft.Container(height=10)
                        ],
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=30,
                    width=500,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.35, ft.Colors.DEEP_PURPLE_ACCENT),
                        offset=ft.Offset(2, 4)
                    ),
                )
            ]
        )
 
    def tournament_winner_view(winner_team_id):
        winner_name = team_name_map.get(winner_team_id, "Unknown Team")
        return ft.View(
            "/winner",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("🏆 Tournament Winner 🏆", size=32, weight="bold", color=ft.Colors.YELLOW_ACCENT),
                            ft.Divider(height=20, color=ft.Colors.GREY_700),
                            ft.Text(winner_name, size=26, weight="bold", color=ft.Colors.WHITE),
                            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                            ft.ElevatedButton(
                                "Back to Home",
                                icon=ft.Icons.HOME,
                                on_click=lambda _: page.go("/select"),
                                bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
                                color=ft.Colors.WHITE,
                                width=300
                            )
                        ],
                        spacing=25,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    padding=30,
                    width=500,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=12,
                        color=ft.Colors.with_opacity(0.4, ft.Colors.DEEP_PURPLE_ACCENT),
                        offset=ft.Offset(2, 4)
                    )
                )
            ]
        )
 
 
 
 

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view())
        elif page.route =='/instructions':
            page.views.append(instructions_view())
        elif page.route == "/create":
            page.views.append(create_tournament_view())
        elif page.route == "/select":
            page.views.append(tournament_selection_view())
        elif page.route == "/tournament":
            page.views.append(tournament_dashboard_view())
        elif page.route == "/teams":
            page.views.append(team_management_view())
        elif page.route == "/fixtures":
            page.views.append(fixture_and_results_view())
        elif page.route == "/points":
            page.views.append(points_table_view())
        elif page.route == "/winner":
            page.views.append(ft.View("/winner", controls=[ft.Text("Winner view accessed directly.")]))
        page.update()
 
 
    page.on_route_change = route_change
    page.go("/")
 
 
 
 
 
ft.app(target=main)