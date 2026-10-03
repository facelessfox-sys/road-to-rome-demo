from pathlib import Path
import re

p = Path('game/scripts/PrettyMain.gd')
s = p.read_text(encoding='utf-8')

s = s.replace('var ambient_clock := 0.0\nvar mars_reaction := 0.0\nvar caption_time := 0.0',
'''var ambient_clock := 0.0
var caption_time := 0.0
var action_timer := 0.0
var feed_timer := 0.0''')
s = s.replace('var mars_head: Sprite2D\nvar hen_brown: Sprite2D\nvar hen_white: Sprite2D',
'''var world_turnip: Sprite2D
var world_leaf: Sprite2D
var feed_fx: Sprite2D''')

s = s.replace('    _setup_animals()\n', '    _setup_items()\n')

s = re.sub(r'func _setup_background\(\) -> void:\n.*?\nfunc _load_textures', '''func _setup_background() -> void:
    var bg_tex: Texture2D = load("res://assets/pretty/hof_showcase.jpg")
    var bg := Sprite2D.new()
    bg.texture = bg_tex
    bg.centered = false
    bg.position = Vector2.ZERO
    bg.z_index = -100
    add_child(bg)

    var patch_tex := AtlasTexture.new()
    patch_tex.atlas = bg_tex
    patch_tex.region = Rect2(345, 520, 45, 64)
    var patch := Sprite2D.new()
    patch.texture = patch_tex
    patch.centered = false
    patch.position = Vector2(300, 520)
    patch.z_index = 5
    add_child(patch)

func _load_textures''', s, flags=re.S)

s = s.replace('    idle_tex = load("res://assets/pretty/titus/idle.webp")',
              '    idle_tex = load("res://assets/pretty/titus/talk.webp")')

s = re.sub(r'func _anchor_player_sprite\(\) -> void:\n.*?\nfunc _setup_ui', '''func _anchor_player_sprite() -> void:
    if player_sprite.texture == null:
        return
    var h := float(player_sprite.texture.get_height())
    var visual_h := 300.0
    var frame_scale := visual_h / maxf(h, 1.0)
    player_sprite.scale = Vector2.ONE * frame_scale
    player_sprite.position = Vector2(0, -visual_h * 0.5)

func _setup_items() -> void:
    world_turnip = Sprite2D.new()
    world_turnip.texture = load("res://assets/pretty/items/turnip_icon.webp")
    world_turnip.position = Vector2(319, 558)
    world_turnip.scale = Vector2.ONE * 0.55
    world_turnip.z_index = 20
    add_child(world_turnip)

    world_leaf = Sprite2D.new()
    world_leaf.texture = load("res://assets/pretty/items/moonleaf_icon.webp")
    world_leaf.position = Vector2(462, 603)
    world_leaf.scale = Vector2.ONE * 0.52
    world_leaf.modulate = Color(0.84, 1.0, 0.64, 1.0)
    world_leaf.z_index = 21
    world_leaf.visible = false
    add_child(world_leaf)

    feed_fx = Sprite2D.new()
    feed_fx.texture = load("res://assets/pretty/items/turnip_icon.webp")
    feed_fx.visible = false
    feed_fx.z_index = 70
    add_child(feed_fx)

func _setup_ui''', s, flags=re.S)

s = re.sub(r'func _process\(delta: float\) -> void:\n.*?\nfunc _unhandled_input', '''func _process(delta: float) -> void:
    ambient_clock += delta
    caption_time = maxf(0.0, caption_time - delta)
    if caption_time <= 0.0 and caption_label.text != "":
        caption_label.text = ""

    _animate_walk(delta)

    if action_timer > 0.0:
        action_timer = maxf(0.0, action_timer - delta)
        if action_timer <= 0.0 and not walking:
            player_sprite.texture = idle_tex
            _anchor_player_sprite()

    if feed_timer > 0.0:
        feed_timer = maxf(0.0, feed_timer - delta)
        var progress: float = 1.0 - feed_timer / 0.65
        var a := Vector2(410, 620)
        var b := Vector2(333, 405)
        feed_fx.position = a.lerp(b, progress) + Vector2(0, -sin(progress * PI) * 52.0)
        feed_fx.rotation = progress * 5.0
        var fade_alpha: float = 1.0 - maxf(0.0, (progress - 0.78) / 0.22)
        feed_fx.modulate = Color(1.0, 1.0, 1.0, fade_alpha)
        if feed_timer <= 0.0:
            feed_fx.visible = false
            feed_fx.modulate = Color.WHITE

func _play_action(tex: Texture2D, seconds: float = 0.65) -> void:
    player_sprite.texture = tex
    _anchor_player_sprite()
    action_timer = seconds

func _unhandled_input''', s, flags=re.S)

s = re.sub(r'func _scale_player\(\) -> void:\n.*?\nfunc _set_verb', '''func _scale_player() -> void:
    var t: float = clampf((player.position.y - 545.0) / 175.0, 0.0, 1.0)
    var perspective: float = lerpf(0.92, 1.00, t)
    player.scale = Vector2.ONE * perspective
    player.z_index = 35 + int(player.position.y / 18.0)

func _set_verb''', s, flags=re.S)

s = re.sub(r'func _take\(id: String\) -> void:\n.*?\nfunc _talk', '''func _take(id: String) -> void:
    if id == "turnip":
        if took_turnip:
            _say("Titus", "Die strategische Rübe befindet sich bereits in meinem Besitz.", 3.0)
            return
        took_turnip = true
        inventory.append("turnip")
        _play_action(take_tex, 0.75)
        world_turnip.visible = false
        _say("Titus", "Strategische Reserve.", 2.8)
        _refresh_inventory()
        _set_objective("Mini-Ziel: Füttere Mars Ultor mit der Rübe.")
        return

    if id == "moonleaf":
        if took_leaf:
            _say("Titus", "Ich habe bereits genug Mondblatt.", 2.8)
            return
        if not mars_fed:
            _say("Titus", "Dafür müsste ich an Mars vorbei. Mars hält Abstand für eine persönliche Beleidigung.", 4.2)
            return
        took_leaf = true
        inventory.append("moonleaf")
        _play_action(celebrate_tex, 1.1)
        world_leaf.visible = false
        _refresh_inventory()
        _set_objective("Mini-Ziel erfüllt: Mondblatt gesichert.")
        _say("Titus", "Ha! Schritt eins auf dem Weg zur Legion: einen Esel bestechen. Ruhm fühlt sich anders an.", 5.0)
        return

    _say("Titus", "Das passt selbst mit sehr viel Optimismus nicht in meine Tasche.", 3.4)

func _talk''', s, flags=re.S)

s = re.sub(r'func _talk\(id: String\) -> void:\n.*?\nfunc _use', '''func _talk(id: String) -> void:
    _play_action(talk_tex, 0.9)
    if id == "mars":
        _say("Titus", "Mars, alter Kamerad. Wir zwei gegen die Welt. ...Mars? ...Mars?", 3.8)
    elif id == "chicken":
        _say("Titus", "Kein Wort zu Vater, verstanden?", 2.7)
    else:
        _say("Titus", "Ich fürchte, dieser Gesprächspartner ist eher von der stillen Sorte.", 3.4)

func _use''', s, flags=re.S)

s = re.sub(r'func _use\(id: String\) -> void:\n.*?\nfunc _refresh_inventory', '''func _use(id: String) -> void:
    if selected_item == "":
        _say("Titus", "Womit denn?", 2.4)
        return

    if selected_item == "turnip" and id == "mars":
        if mars_fed:
            _say("Titus", "Mars hat seine Bestechung bereits erhalten. Ein Mann muss Grenzen setzen.", 3.8)
            return
        mars_fed = true
        _play_action(use_tex, 0.85)
        inventory.erase("turnip")
        selected_item = ""
        _refresh_inventory()
        world_leaf.visible = true
        feed_fx.position = Vector2(410, 620)
        feed_fx.rotation = 0.0
        feed_fx.modulate = Color.WHITE
        feed_fx.visible = true
        feed_timer = 0.65
        _set_objective("Mini-Ziel: Jetzt das Mondblatt nehmen.")
        _say("Titus", "Disziplin. Gehorsam. Bestechlichkeit. Fast wie bei der Legion.", 4.5)
        return

    if selected_item == "turnip":
        _say("Titus", "Ich bezweifle, dass die Rübe hier ihre wahre Bestimmung findet.", 3.2)
        return

    if selected_item == "moonleaf":
        _say("Titus", "Das Mondblatt brauche ich für meinen Plan. Nicht verschwenden, Titus.", 3.2)
        return

func _refresh_inventory''', s, flags=re.S)

s = re.sub(r'func _reset\(\) -> void:\n.*\Z', '''func _reset() -> void:
    verb = "look"
    inventory.clear()
    selected_item = ""
    took_turnip = false
    mars_fed = false
    took_leaf = false
    walking = false
    pending_hotspot = ""
    player.position = Vector2(745, 665)
    player_sprite.flip_h = false
    player_sprite.texture = idle_tex
    _anchor_player_sprite()
    _scale_player()
    world_turnip.visible = true
    world_leaf.visible = false
    feed_fx.visible = false
    feed_timer = 0.0
    action_timer = 0.0
    _set_objective("Mini-Ziel: Finde einen Weg an Mars Ultor vorbei.")
    _say("Titus", "Noch einmal. Diesmal mit noch mehr militärischer Präzision.", 3.8)
    _update_verb_border()
    _refresh_inventory()
''', s, flags=re.S)

for forbidden in ('_setup_animals()', 'mars_head.', 'hen_brown.', 'hen_white.'):
    if forbidden in s:
        raise SystemExit(f'Hotfix incomplete, still contains: {forbidden}')

p.write_text(s, encoding='utf-8')
print('Patched', p, 'bytes=', len(s.encode()))
