"""
Pokemon Sleep game data constants.
"""

# Research areas and their favored berries
RESEARCH_AREAS = {
    "greengrass_isle": {
        "name": "グリーングラス島",
        "berries": ["Leppa", "Oran", "Pecha", "Bluk", "Persim", "Figy", "Wiki"],
        "description": "バランスのとれた初心者向けフィールド",
    },
    "cyan_beach": {
        "name": "シアンの砂浜",
        "berries": ["Oran", "Sitrus", "Aspear", "Rawst", "Chesto", "Leppa", "Pecha"],
        "description": "水辺フィールド",
    },
    "taupe_hollow": {
        "name": "トープ洞窟",
        "berries": ["Figy", "Wiki", "Mago", "Aguav", "Iapapa", "Sitrus", "Oran"],
        "description": "洞窟フィールド、食材系が重要",
    },
    "snowdrop_tundra": {
        "name": "スノードロップ原野",
        "berries": ["Aspear", "Rawst", "Chesto", "Bluk", "Nanab", "Leppa", "Oran"],
        "description": "雪原フィールド",
    },
    "lapis_lakeside": {
        "name": "ラピス湖畔",
        "berries": ["Persim", "Razz", "Grepa", "Hondew", "Pomeg", "Kelpsy", "Qualot"],
        "description": "湖畔フィールド",
    },
    "mahogany_hill": {
        "name": "マホガニー丘陵",
        "berries": ["Pamtre", "Belue", "Nomel", "Wepear", "Durin", "Yago", "Cornn"],
        "description": "丘陵フィールド",
    },
    "shiver_snowfields": {
        "name": "シバーの雪原",
        "berries": ["Hondew", "Durin", "Yago", "Pumkin", "Ginema", "Touga", "Eggant"],
        "description": "極寒フィールド、上級者向け",
    },
    "desolate_cave": {
        "name": "廃坑の洞窟",
        "berries": ["Grepa", "Hondew", "Durin", "Kelpsy", "Qualot", "Pomeg", "Nomel"],
        "description": "廃坑フィールド",
    },
    "nap_island": {
        "name": "うたたね諸島",
        "berries": ["Oran", "Sitrus", "Leppa", "Pecha", "Chesto", "Rawst", "Aspear"],
        "description": "島フィールド",
    },
}

# Main skills
MAIN_SKILLS = {
    "charge_energy_s": {"name": "元気チャージS", "type": "energy", "description": "自分の元気を回復する"},
    "charge_energy_m": {"name": "元気チャージM", "type": "energy", "description": "自分の元気を大きく回復する"},
    "energize_all_s": {"name": "みんなを元気にS", "type": "energy", "description": "チーム全員の元気を回復する"},
    "energize_all_m": {"name": "みんなを元気にM", "type": "energy", "description": "チーム全員の元気を大きく回復する"},
    "charge_strength_s": {"name": "ゆめのかけらゲットS", "type": "strength", "description": "ゆめのかけらを少し獲得する"},
    "charge_strength_m": {"name": "ゆめのかけらゲットM", "type": "strength", "description": "ゆめのかけらを獲得する"},
    "charge_strength_l": {"name": "ゆめのかけらゲットL", "type": "strength", "description": "ゆめのかけらをたくさん獲得する"},
    "dream_shard_magnet_s": {"name": "ゆめのかけら磁石S", "type": "dream_shard", "description": "フィールドのゆめのかけらを集める"},
    "dream_shard_magnet_s_range": {"name": "ゆめのかけら磁石S+", "type": "dream_shard", "description": "フィールドのゆめのかけらを広範囲で集める"},
    "ingredient_magnet_s": {"name": "食材磁石S", "type": "ingredient", "description": "食材をランダムで1個入手する"},
    "cooking_power_up_s": {"name": "料理パワーアップS", "type": "cooking", "description": "次の料理の食材消費量を減らす"},
    "extra_helpful_s": {"name": "ちからもちS", "type": "help", "description": "お手伝いを追加で1回行う"},
    "helper_boost": {"name": "ヘルパーブースト", "type": "help", "description": "チーム全員のお手伝い速度を上げる"},
    "metronome": {"name": "メトロノーム", "type": "random", "description": "ランダムなスキルを発動する"},
    "tasty_chance_s": {"name": "ごちそうチャンスS", "type": "cooking", "description": "料理の鍋ボーナス発動率を上げる"},
}

# Sub-skills
SUB_SKILLS = {
    "berry_finding_s": "きのみのかたまりS",
    "berry_finding_m": "きのみのかたまりM",
    "ingredient_finder_s": "食材確率アップS",
    "ingredient_finder_m": "食材確率アップM",
    "helping_speed_s": "お手伝いスピードアップS",
    "helping_speed_m": "お手伝いスピードアップM",
    "skill_level_up_s": "スキルレベルアップS",
    "skill_level_up_m": "スキルレベルアップM",
    "energy_recovery_bonus": "元気回復ボーナス",
    "inventory_up_s": "おてつだいきのみS",
    "inventory_up_m": "おてつだいきのみM",
    "inventory_up_l": "おてつだいきのみL",
    "sleep_exp_bonus": "ねむりEXPボーナス",
    "dream_shard_bonus": "ゆめのかけらボーナス",
    "research_exp_bonus": "リサーチEXPボーナス",
    "helping_bonus": "おてつだいボーナス",
    "skill_trigger_s": "スキル発動確率アップS",
    "skill_trigger_m": "スキル発動確率アップM",
    "bfs_plus": "BFS+",
}

# Pokemon natures and their stat effects
NATURES = {
    "hardy": {"name": "がんばりや", "up": None, "down": None},
    "lonely": {"name": "さみしがり", "up": "attack", "down": "defense"},
    "brave": {"name": "ゆうかん", "up": "attack", "down": "speed"},
    "adamant": {"name": "いじっぱり", "up": "attack", "down": "sp_attack"},
    "naughty": {"name": "やうちゃん", "up": "attack", "down": "sp_defense"},
    "bold": {"name": "ずぶとい", "up": "defense", "down": "attack"},
    "docile": {"name": "すなお", "up": None, "down": None},
    "relaxed": {"name": "のんき", "up": "defense", "down": "speed"},
    "impish": {"name": "わんぱく", "up": "defense", "down": "sp_attack"},
    "lax": {"name": "のうてんき", "up": "defense", "down": "sp_defense"},
    "timid": {"name": "おくびょう", "up": "speed", "down": "attack"},
    "hasty": {"name": "せっかち", "up": "speed", "down": "defense"},
    "serious": {"name": "まじめ", "up": None, "down": None},
    "jolly": {"name": "ようき", "up": "speed", "down": "sp_attack"},
    "naive": {"name": "むじゃき", "up": "speed", "down": "sp_defense"},
    "modest": {"name": "ひかえめ", "up": "sp_attack", "down": "attack"},
    "mild": {"name": "おっとり", "up": "sp_attack", "down": "defense"},
    "quiet": {"name": "れいせい", "up": "sp_attack", "down": "speed"},
    "bashful": {"name": "てれや", "up": None, "down": None},
    "rash": {"name": "うっかりや", "up": "sp_attack", "down": "sp_defense"},
    "calm": {"name": "おだやか", "up": "sp_defense", "down": "attack"},
    "gentle": {"name": "おとなしい", "up": "sp_defense", "down": "defense"},
    "sassy": {"name": "なまいき", "up": "sp_defense", "down": "speed"},
    "careful": {"name": "しんちょう", "up": "sp_defense", "down": "sp_attack"},
    "quirky": {"name": "きまぐれ", "up": None, "down": None},
}

# Pokemon Sleep relevant nature effects (on helping speed & skill freq)
NATURE_SLEEP_EFFECTS = {
    # Helping Speed Up (お手伝い速度 +)
    "timid": {"help_speed": 1, "skill_freq": 0, "energy": 0},
    "hasty": {"help_speed": 1, "skill_freq": 0, "energy": 0},
    "jolly": {"help_speed": 1, "skill_freq": 0, "energy": 0},
    "naive": {"help_speed": 1, "skill_freq": 0, "energy": 0},
    # Helping Speed Down
    "brave": {"help_speed": -1, "skill_freq": 0, "energy": 0},
    "relaxed": {"help_speed": -1, "skill_freq": 0, "energy": 0},
    "quiet": {"help_speed": -1, "skill_freq": 0, "energy": 0},
    "sassy": {"help_speed": -1, "skill_freq": 0, "energy": 0},
    # Skill Freq Up
    "modest": {"help_speed": 0, "skill_freq": 1, "energy": 0},
    "mild": {"help_speed": 0, "skill_freq": 1, "energy": 0},
    "rash": {"help_speed": 0, "skill_freq": 1, "energy": 0},
    "quiet": {"help_speed": -1, "skill_freq": 1, "energy": 0},
    # Skill Freq Down
    "adamant": {"help_speed": 0, "skill_freq": -1, "energy": 0},
    "impish": {"help_speed": 0, "skill_freq": -1, "energy": 0},
    "careful": {"help_speed": 0, "skill_freq": -1, "energy": 0},
    # Energy Up
    "bold": {"help_speed": 0, "skill_freq": 0, "energy": 1},
    "lax": {"help_speed": 0, "skill_freq": 0, "energy": 1},
    "naughty": {"help_speed": 0, "skill_freq": 0, "energy": 1},
    # Neutral
    "hardy": {"help_speed": 0, "skill_freq": 0, "energy": 0},
    "lonely": {"help_speed": 0, "skill_freq": 0, "energy": 0},
    "docile": {"help_speed": 0, "skill_freq": 0, "energy": 0},
    "serious": {"help_speed": 0, "skill_freq": 0, "energy": 0},
    "bashful": {"help_speed": 0, "skill_freq": 0, "energy": 0},
    "quirky": {"help_speed": 0, "skill_freq": 0, "energy": 0},
    "calm": {"help_speed": 0, "skill_freq": 0, "energy": 1},
    "gentle": {"help_speed": 0, "skill_freq": 0, "energy": 1},
}

# Pokemon specialties
SPECIALTIES = {
    "berry": "きのみ",
    "ingredient": "食材",
    "skill": "スキル",
}

# Goal types for team building
TEAM_GOALS = {
    "strength": "ゆめのかけら最大化",
    "ingredients": "食材収集最大化",
    "cooking": "料理効率最大化",
    "weekly_event": "週間イベント対応",
    "balanced": "バランス重視",
}

# Example Pokemon database (commonly used Pokemon in Pokemon Sleep)
COMMON_POKEMON = [
    "Bulbasaur", "Charmander", "Squirtle", "Caterpie", "Pidgey", "Rattata",
    "Pikachu", "Raichu", "Clefairy", "Clefable", "Jigglypuff", "Wigglytuff",
    "Meowth", "Persian", "Psyduck", "Golduck", "Growlithe", "Arcanine",
    "Slowpoke", "Slowbro", "Magnemite", "Magneton", "Doduo", "Dodrio",
    "Gastly", "Haunter", "Gengar", "Drowzee", "Hypno", "Kangaskhan",
    "Scyther", "Jynx", "Electabuzz", "Magmar", "Lapras", "Eevee",
    "Vaporeon", "Jolteon", "Flareon", "Snorlax", "Dratini", "Dragonair",
    "Dragonite", "Mewtwo", "Mew",
    # Gen 2
    "Chikorita", "Cyndaquil", "Totodile", "Togepi", "Togetic", "Marill",
    "Azumarill", "Espeon", "Umbreon", "Wobbuffet", "Snubbull", "Granbull",
    "Heracross", "Teddiursa", "Ursaring", "Delibird", "Houndour", "Houndoom",
    # Gen 3+
    "Treecko", "Torchic", "Mudkip", "Ralts", "Gardevoir", "Gallade",
    "Absol", "Bagon", "Salamence", "Beldum", "Metang", "Metagross",
    "Lucario", "Riolu", "Croagunk", "Toxicroak", "Glaceon", "Leafeon",
    "Sylveon", "Goodra", "Mimikyu", "Dedenne",
]
