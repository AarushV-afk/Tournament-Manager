import flet as ft
import mysql.connector
import random
import itertools
 
 
def main(page: ft.Page):
    page.title = "Tournament Manager"
    page.scroll = ft.ScrollMode.AUTO
 
    # MySQL connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="tournament_db"
    )
    cursor = conn.cursor(dictionary=True)
 
    # Auto-generate tables
    def setup_database():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                tournament_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
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
 
        conn.commit()
 
    setup_database()
 
    tournament_id = None
    team_ids = []
    team_name_map = {}
    current_tournament_type = "round_robin"
 
    def show_snack(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()
 
    def load_tournament(t_id):
        nonlocal tournament_id, team_ids, team_name_map, current_tournament_type
        tournament_id = t_id
        cursor.execute("SELECT type FROM tournaments WHERE tournament_id = %s", (tournament_id,))
        t_type = cursor.fetchone()
        if t_type:
            current_tournament_type = t_type['type']
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
        tournament_buttons = ft.Column()
        cursor.execute("SELECT * FROM tournaments")
        tournaments = cursor.fetchall()
 
        for t in tournaments:
            tournament_buttons.controls.append(
                ft.Row([
                    ft.ElevatedButton(
                        text=f"{t['name']} (ID: {t['tournament_id']})",
                        on_click=lambda e, tid=t['tournament_id']: load_tournament(tid)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Delete Tournament",
                        on_click=lambda e, tid=t['tournament_id']: delete_tournament(tid)
                    )
                ])
            )
 
        return ft.View(
            "/select",
            controls=[
                ft.Text("Select Tournament", size=30),
                tournament_buttons,
                ft.TextButton("Go to Create Tournament", on_click=lambda _: page.go("/create"))
            ]
        )
 
    def create_tournament_view():
        tournament_name = ft.TextField(label="Tournament Name")
        tournament_type = ft.Dropdown(
            label="Tournament Type",
            options=[ft.dropdown.Option("round_robin"), ft.dropdown.Option("knockout")],
            value="round_robin"
        )
        start_date = ft.TextField(label="Start Date (YYYY-MM-DD)")
 
        def create_tournament(e):
            cursor.execute("INSERT INTO tournaments (name, type, start_date) VALUES (%s, %s, %s)",
                           (tournament_name.value, tournament_type.value, start_date.value))
            conn.commit()
            show_snack("Tournament Created!")
            page.go("/select")
 
        return ft.View(
            "/create",
            controls=[
                ft.Text("Create Tournament", size=30),
                tournament_name,
                tournament_type,
                start_date,
                ft.ElevatedButton("Create", on_click=create_tournament),
                ft.TextButton("Go to Select Tournament", on_click=lambda _: page.go("/select"))
            ]
        )
 
    def tournament_dashboard_view():
        return ft.View(
            "/tournament",
            controls=[
                ft.Text("Tournament Dashboard", size=30),
                ft.TextButton("Manage Teams", on_click=lambda _: page.go("/teams")),
                ft.TextButton("Manage Fixtures & Results", on_click=lambda _: page.go("/fixtures")),
                ft.TextButton("View Points Table", on_click=lambda _: page.go("/points")),
                ft.TextButton("Back to Select Tournament", on_click=lambda _: page.go("/select"))
            ]
        )
 
    def team_management_view():
        team_name = ft.TextField(label="Team Name")
        team_list = ft.Column()
 
        def add_team(e):
            if tournament_id is None:
                show_snack("No tournament loaded")
                return
            cursor.execute("INSERT INTO teams (tournament_id, team_name) VALUES (%s, %s)",
                           (tournament_id, team_name.value))
            conn.commit()
            tid = cursor.lastrowid
            team_ids.append(tid)
            team_name_map[tid] = team_name.value
            team_list.controls.append(ft.Text(team_name.value))
            team_name.value = ""
            page.update()
 
        cursor.execute("SELECT team_name FROM teams WHERE tournament_id = %s", (tournament_id,))
        for t in cursor.fetchall():
            team_list.controls.append(ft.Text(t['team_name']))
 
        return ft.View(
            "/teams",
            controls=[
                ft.Text("Manage Teams", size=30),
                team_name,
                ft.ElevatedButton("Add Team", on_click=add_team),
                team_list,
                ft.TextButton("Back to Dashboard", on_click=lambda _: page.go("/tournament"))
            ]
        )
 
    def fixture_and_results_view():
        fixtures_display = ft.Column()
        generate_or_view_button = ft.ElevatedButton(text="")
 
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
            for i in range(0, len(shuffled) - 1, 2):
                t1 = shuffled[i]
                t2 = shuffled[i + 1]
                cursor.execute("INSERT INTO matches (tournament_id, round, team1_id, team2_id) VALUES (%s, %s, %s, %s)",
                               (tournament_id, 1, t1, t2))
            conn.commit()
            initialize_points_table()
            show_snack("Fixtures Generated")
            update_generate_button()
            load_fixtures()
 
        def check_and_generate_next_knockout_round():
            # Find highest current round
            cursor.execute("SELECT MAX(round) as max_round FROM matches WHERE tournament_id = %s", (tournament_id,))
            max_round = cursor.fetchone()['max_round']
 
            for round_num in range(1, max_round + 1):
                cursor.execute("""
                    SELECT match_id, winner_team_id
                    FROM matches
                    WHERE tournament_id = %s AND round = %s
                """, (tournament_id, round_num))
                matches = cursor.fetchall()
 
                # If any match in this round has no result, return
                if any(m['winner_team_id'] is None for m in matches):
                    return
 
                # If already generated next round, skip
                cursor.execute("SELECT COUNT(*) AS count FROM matches WHERE tournament_id = %s AND round = %s",
                               (tournament_id, round_num + 1))
                if cursor.fetchone()['count'] > 0:
                    continue
 
                # Get winners and shuffle
                winners = [m['winner_team_id'] for m in matches if m['winner_team_id']]
                random.shuffle(winners)
 
                # Handle final winner case
                if len(winners) == 1:
                    show_snack(f"🏆 {team_name_map[winners[0]]} wins the tournament!")
                    return
 
                # Generate next round
                for i in range(0, len(winners) - 1, 2):
                    cursor.execute("""
                        INSERT INTO matches (tournament_id, round, team1_id, team2_id)
                        VALUES (%s, %s, %s, %s)
                    """, (tournament_id, round_num + 1, winners[i], winners[i + 1]))
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
                    fixtures_display.controls.append(ft.Text(f"{match_label} - {result_text}"))
                    continue
 
                match_id = match['match_id']
                t1_id = match['team1_id']
                t2_id = match['team2_id']
 
                def result_handler_factory(winner_id, loser_id, result_type, match_id, label):
                    def handler(e):
                        # update points
                        if result_type == "draw":
                            update_points(winner_id, "draw")
                            update_points(loser_id, "draw")
                            final_winner_id = None
                        else:
                            update_points(winner_id, "win")
                            update_points(loser_id, "loss")
                            final_winner_id = winner_id
 
                        # update match result
                        cursor.execute(
                            "UPDATE matches SET result = %s, winner_team_id = %s WHERE match_id = %s",
                            (result_type, final_winner_id, match_id)
                        )
                        conn.commit()
 
                        # ✅ Call knockout checker here
                        check_and_generate_next_knockout_round()
 
                        show_snack(f"Result recorded: {label} - {result_type.replace('_', ' ').capitalize()}")
                        load_fixtures()
                        page.update()
 
                    return handler
 
                submenu = ft.SubmenuButton(
                    content=ft.Text(match_label),
                    controls=[
                        ft.MenuItemButton(content=ft.Text(f"{match['team1']} Wins"),
                                          on_click=result_handler_factory(t1_id, t2_id, "team1_win", match_id, match_label)),
                        ft.MenuItemButton(content=ft.Text(f"{match['team2']} Wins"),
                                          on_click=result_handler_factory(t2_id, t1_id, "team2_win", match_id, match_label)),
                        ft.MenuItemButton(content=ft.Text("Draw"),
                                          on_click=result_handler_factory(t1_id, t2_id, "draw", match_id, match_label)),
                    ]
                )
 
                fixtures_display.controls.append(submenu)
 
            page.update()
 
 
        update_generate_button()
 
        return ft.View(
            "/fixtures",
            controls=[
                ft.Text("Fixtures & Results", size=30),
                generate_or_view_button,
                fixtures_display,
                ft.TextButton("Back to Dashboard", on_click=lambda _: page.go("/tournament"))
            ]
        )
 
    def points_table_view():
        points_display = ft.Column()
 
        def view_points_table(e):
            points_display.controls.clear()
            cursor.execute("""
                SELECT * FROM points_table 
                WHERE tournament_id = %s 
                ORDER BY points DESC, wins DESC
            """, (tournament_id,))
            for idx, row in enumerate(cursor.fetchall(), start=1):
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                points_display.controls.append(
                    ft.Text(
                        f"{medal} {row['team_name']} | Played: {row['games_played']} | W: {row['wins']} | "
                        f"D: {row['draws']} | L: {row['losses']} | Points: {row['points']}"
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
 
        return ft.View(
            "/points",
            controls=[
                ft.Text("Points Table", size=30),
                ft.Row([
                    ft.ElevatedButton("View Points", on_click=view_points_table),
                    ft.ElevatedButton("Reset Points", on_click=reset_points, bgcolor=ft.Colors.RED_400,
                                      color=ft.Colors.WHITE)
                ]),
                points_display,
                ft.TextButton("Back to Dashboard", on_click=lambda _: page.go("/tournament"))
            ]
        )
 
    def route_change(route):
        page.views.clear()
        if page.route == "/create":
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
        page.update()
 
    page.on_route_change = route_change
    page.go("/select")
 
 
ft.app(target=main)