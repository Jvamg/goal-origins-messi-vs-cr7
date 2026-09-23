#!/usr/bin/env python3
"""
Mapeamento de Origem de Gols via StatsBomb Open Data
Extrai lances de gol e a coordenada exata de recepção (1º toque da posse individual final).
"""

import os
import pickle
import pandas as pd
from statsbombpy import sb

def extract_receipt_from_statsbomb_match(match_id, target_player_name):
    try:
        events = sb.events(match_id=match_id)
    except Exception:
        return []
    
    if events.empty or "shot_outcome" not in events.columns:
        return []
    
    goals = events[(events["player"] == target_player_name) & (events["shot_outcome"] == "Goal")]
    if goals.empty:
        return []
    
    extracted = []
    events = events.sort_values(by=["period", "minute", "second", "index"])
    
    for _, shot in goals.iterrows():
        poss_id = shot.get("possession")
        period = shot.get("period")
        shot_loc = shot.get("location")
        if not isinstance(shot_loc, (list, tuple)) or len(shot_loc) < 2:
            continue
            
        poss_events = events[(events["period"] == period) & (events["possession"] == poss_id)]
        poss_events = poss_events.loc[:shot.name]
        
        # Retroceder no lance para identificar a posse individual final
        receipt_x, receipt_y = shot_loc[0], shot_loc[1]
        player_events_reversed = []
        
        for idx in reversed(poss_events.index):
            ev = poss_events.loc[idx]
            if idx == shot.name:
                continue
            
            p = ev.get("player")
            t = ev.get("type")
            
            if p == target_player_name:
                # Se o jogador passou a bola anteriormente, a posse anterior resetou
                if t == "Pass":
                    break
                loc = ev.get("location")
                if isinstance(loc, (list, tuple)) and len(loc) >= 2:
                    player_events_reversed.append((loc[0], loc[1], t))
            else:
                # Se foi passe de companheiro em direção a ele
                if t == "Pass" and ev.get("pass_recipient") == target_player_name:
                    end_loc = ev.get("pass_end_location")
                    if isinstance(end_loc, (list, tuple)) and len(end_loc) >= 2:
                        receipt_x, receipt_y = end_loc[0], end_loc[1]
                    break
                else:
                    break
                    
        if player_events_reversed:
            earliest = player_events_reversed[-1]
            receipt_x, receipt_y = earliest[0], earliest[1]
            
        extracted.append({
            "source": "StatsBomb",
            "match_id": match_id,
            "period": period,
            "minute": shot.get("minute"),
            "second": shot.get("second"),
            "shot_x": shot_loc[0],
            "shot_y": shot_loc[1],
            "receipt_x": receipt_x,
            "receipt_y": receipt_y
        })
        
    return extracted

if __name__ == "__main__":
    print("Módulo StatsBomb Scraper pronto.")
