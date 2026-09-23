import os
import glob
import json
import pickle
import time
import seleniumbase.undetected as uc

# Monkey-patch browser for Linux Brave installation
uc.find_chrome_executable = lambda: "/usr/bin/brave-browser"
import soccerdata as sd

CACHE_DIR = "/home/jvamg/soccerdata/data/WhoScored"
CR7_PLAYER_ID = 5583
MESSI_PLAYER_ID = 11119

TARGET_LEAGUES_SEASONS = [
    ("ESP-La Liga", ["1415", "1516"]),
    ("ITA-Serie A", ["1819", "1920", "2021"]),
    ("ENG-Premier League", ["2122"]),
    ("INT-European Championship", ["2016", "2020"]),
    ("INT-World Cup", ["2018"]),
]

def extract_goals_from_match_json(json_path, target_player_id=CR7_PLAYER_ID, player_name="Cristiano Ronaldo"):
    with open(json_path, "r") as fp:
        try:
            data = json.load(fp)
        except Exception:
            return []
    
    events = data.get("events", [])
    goals_data = []
    
    for i, ev in enumerate(events):
        p_id = ev.get("playerId")
        is_goal = ev.get("isGoal") or (ev.get("type", {}).get("displayName") == "Goal")
        
        # Check if it is a goal by target player
        if is_goal and (p_id == target_player_id or (ev.get("playerName") and player_name in ev.get("playerName"))):
            shot_x = ev.get("x")
            shot_y = ev.get("y")
            period = ev.get("period", {}).get("value") if isinstance(ev.get("period"), dict) else ev.get("period")
            minute = ev.get("minute")
            second = ev.get("second")
            
            # Trace backwards in events to find receipt location
            receipt_x, receipt_y = shot_x, shot_y
            receipt_event_type = "Shot (Direct)"
            
            # Look backwards in the same period
            j = i - 1
            player_touches = []
            while j >= 0:
                prev_ev = events[j]
                prev_period = prev_ev.get("period", {}).get("value") if isinstance(prev_ev.get("period"), dict) else prev_ev.get("period")
                if prev_period != period:
                    break
                
                prev_pid = prev_ev.get("playerId")
                prev_type = prev_ev.get("type", {}).get("displayName", "")
                
                # If target player had preceding actions in this possession
                if prev_pid == target_player_id:
                    # If player made a pass before this, contiguous individual possession started AFTER that pass!
                    if prev_type == "Pass":
                        break
                    player_touches.append(prev_ev)
                    j -= 1
                    continue
                else:
                    # Not target player: check if it was an assist / pass
                    if prev_type == "Pass":
                        pass_end_x = prev_ev.get("endX")
                        pass_end_y = prev_ev.get("endY")
                        if pass_end_x is not None and pass_end_y is not None:
                            receipt_x = pass_end_x
                            receipt_y = pass_end_y
                            receipt_event_type = "Assisted Pass End"
                        break
                    else:
                        # Ball recovery, tackle, turnover, etc.
                        break
                j -= 1
            
            # If target player had contiguous touches before the shot without an intervening pass:
            if player_touches and receipt_event_type != "Assisted Pass End":
                earliest = player_touches[-1]
                receipt_x = earliest.get("x", receipt_x)
                receipt_y = earliest.get("y", receipt_y)
                receipt_event_type = f"Touch: {earliest.get('type', {}).get('displayName', 'Action')}"
            
            # Convert Opta coords (0-100, 0-100) to StatsBomb coords (120x80)
            sb_shot_x = shot_x * 1.2
            sb_shot_y = shot_y * 0.8
            sb_receipt_x = receipt_x * 1.2
            sb_receipt_y = receipt_y * 0.8
            
            goals_data.append({
                "source": "WhoScored",
                "match_id": data.get("matchId", 0),
                "minute": minute,
                "second": second,
                "shot_x": sb_shot_x,
                "shot_y": sb_shot_y,
                "receipt_x": sb_receipt_x,
                "receipt_y": sb_receipt_y,
                "opta_shot_x": shot_x,
                "opta_shot_y": shot_y,
                "opta_receipt_x": receipt_x,
                "opta_receipt_y": receipt_y,
                "receipt_type": receipt_event_type,
            })
            
    return goals_data

def get_matches_for_player_from_schedules(target_player_id=CR7_PLAYER_ID, player_name="Cristiano Ronaldo"):
    matches_found = {}
    for f in glob.glob(f"{CACHE_DIR}/matches/*.json"):
        with open(f, "r") as fp:
            try:
                data = json.load(fp)
            except Exception:
                continue
        tourneys = data.get("tournaments", [])
        for t in tourneys:
            for m in t.get("matches", []):
                m_id = m.get("id")
                incidents = m.get("incidents", [])
                for inc in incidents:
                    if inc.get("type") == 1 and (
                        inc.get("playerId") == target_player_id 
                        or player_name in inc.get("playerName", "")
                    ):
                        matches_found[m_id] = {
                            "match_id": m_id,
                            "home": m.get("homeTeamName"),
                            "away": m.get("awayTeamName"),
                            "date": m.get("startTimeUtc"),
                        }
                        break
    return matches_found

TARGET_LEAGUES_SEASONS = [
    ("ESP-La Liga", ["1415", "1516"]),
    ("ITA-Serie A", ["1819", "1920", "2021"]),
    ("ENG-Premier League", ["2122"]),
]

def save_and_plot_progress():
    all_goals = []
    for f in glob.glob(f"{CACHE_DIR}/events/*/*.json"):
        goals = extract_goals_from_match_json(f, CR7_PLAYER_ID, "Cristiano Ronaldo")
        all_goals.extend(goals)
    
    print(f"\n==========================================")
    print(f"TOTAL CR7 GOALS EXTRACTED FROM WHOSCORED SO FAR: {len(all_goals)}")
    print(f"==========================================")
    
    with open("cr7_whoscored_goals.pkl", "wb") as fp:
        pickle.dump(all_goals, fp)
    print("Salvo em cr7_whoscored_goals.pkl")
    
    # Regenerate plots
    os.system(".venv/bin/python3 visualizar_origem_gols_carreira.py")

def process_target_leagues():
    for league, seasons in TARGET_LEAGUES_SEASONS:
        print(f"\n========================================================")
        print(f"Processando: {league} - Temporadas: {seasons}")
        print(f"========================================================")
        try:
            ws = sd.WhoScored(leagues=league, seasons=seasons, headless=True)
            try:
                # 1. Carregar calendário / tabela
                print("-> Baixando calendário de jogos...")
                ws.read_schedule()
                
                # 2. Identificar partidas com gols do Cristiano Ronaldo
                cr7_matches = get_matches_for_player_from_schedules(CR7_PLAYER_ID, "Cristiano Ronaldo")
                
                # Checar quais já estão em cache
                cached_event_files = glob.glob(f"{CACHE_DIR}/events/*/*.json")
                cached_ids = set()
                for f in cached_event_files:
                    try:
                        m_id = int(os.path.basename(f).replace(".json", ""))
                        cached_ids.add(m_id)
                    except ValueError:
                        pass
                
                # Filtrar apenas as partidas desta liga/temporada que faltam
                # Pegar os match_ids dos fixtures carregados
                league_sched_files = []
                for s in seasons:
                    league_sched_files.extend(glob.glob(f"{CACHE_DIR}/matches/{league}_{s}_*.json"))
                
                league_cr7_ids = set()
                for f in league_sched_files:
                    with open(f, "r") as fp:
                        try:
                            data = json.load(fp)
                        except Exception:
                            continue
                    for t in data.get("tournaments", []):
                        for m in t.get("matches", []):
                            m_id = m.get("id")
                            for inc in m.get("incidents", []):
                                if inc.get("type") == 1 and (
                                    inc.get("playerId") == CR7_PLAYER_ID 
                                    or "Cristiano Ronaldo" in inc.get("playerName", "")
                                ):
                                    league_cr7_ids.add(m_id)
                                    break
                
                missing_league_ids = [m_id for m_id in league_cr7_ids if m_id not in cached_ids]
                print(f"-> Partidas com gols do CR7 nesta liga: {len(league_cr7_ids)}")
                print(f"-> Partidas a baixar: {len(missing_league_ids)}")
                
                if missing_league_ids:
                    print(f"-> Baixando {len(missing_league_ids)} partidas...")
                    ws.read_events(match_id=missing_league_ids, output_fmt="raw")
                else:
                    print("-> Todas as partidas já estavam em cache.")
                    
            finally:
                if hasattr(ws, "_driver") and ws._driver:
                    ws._driver.quit()
                    
            # Atualiza dados e gráficos a cada liga concluída
            save_and_plot_progress()
            
        except Exception as e:
            print(f"Erro ao processar {league}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    process_target_leagues()
