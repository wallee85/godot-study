class_name Main
extends Node

@export var mob_scene: PackedScene

@export_group("Difficulty")
@export_range(1, 100, 1) var points_per_level: int = 10
@export_range(1, 20, 1) var max_level: int = 10
@export_range(0.05, 2.0, 0.05) var base_spawn_interval: float = 0.5
@export_range(0.0, 0.1, 0.01) var spawn_interval_step: float = 0.04
@export_range(0.05, 2.0, 0.05) var min_spawn_interval: float = 0.15
@export_range(0.0, 1000.0, 10.0) var base_speed_min: float = 150.0
@export_range(0.0, 1000.0, 10.0) var base_speed_max: float = 250.0
@export_range(0.0, 200.0, 5.0) var speed_bonus_per_level: float = 20.0

var score: int = 0
var level: int = 1

@onready var _player: Player = $Player
@onready var _hud: HUD = $HUD
@onready var _start_position: Marker2D = $StartPosition
@onready var _mob_spawn_location: PathFollow2D = $MobPath/MobSpawnLocation
@onready var _mob_timer: Timer = $MobTimer
@onready var _score_timer: Timer = $ScoreTimer
@onready var _start_timer: Timer = $StartTimer
@onready var _music: AudioStreamPlayer = $Music
@onready var _death_sound: AudioStreamPlayer = $DeathSound


func game_over() -> void:
	_mob_timer.stop()
	_score_timer.stop()
	_hud.show_game_over()
	_music.stop()
	_death_sound.play()


func new_game() -> void:
	get_tree().call_group(&"mobs", &"queue_free")
	score = 0
	level = 1
	_mob_timer.wait_time = base_spawn_interval

	_player.start(_start_position.position)
	_start_timer.start()

	_hud.update_score(score)
	_hud.update_level(level)
	_hud.show_message("Get Ready")
	_music.play()


func _on_mob_timer_timeout() -> void:
	if mob_scene == null:
		push_error("Main.mob_scene is not assigned.")
		return

	var mob: Mob = mob_scene.instantiate() as Mob
	if mob == null:
		push_error("Main.mob_scene must have a Mob script on its root.")
		return

	# 在包围屏幕的路径上随机取一点作为出生位置。
	_mob_spawn_location.progress_ratio = randf()
	mob.position = _mob_spawn_location.position

	# 让敌人朝路径的法线方向飞，并加一点随机偏角。
	var direction: float = _mob_spawn_location.rotation + PI / 2.0
	direction += randf_range(-PI / 4.0, PI / 4.0)
	mob.rotation = direction

	var speed_bonus: float = float(level - 1) * speed_bonus_per_level
	var speed: float = randf_range(base_speed_min + speed_bonus, base_speed_max + speed_bonus)
	mob.linear_velocity = Vector2(speed, 0.0).rotated(direction)
	add_child(mob)


func _on_score_timer_timeout() -> void:
	score += 1
	_hud.update_score(score)
	_update_difficulty()


func _update_difficulty() -> void:
	var new_level: int = mini(floori(float(score) / float(points_per_level)) + 1, max_level)
	if new_level == level:
		return

	level = new_level
	_hud.update_level(level)

	var interval: float = base_spawn_interval - float(level - 1) * spawn_interval_step
	_mob_timer.wait_time = maxf(interval, min_spawn_interval)


func _on_start_timer_timeout() -> void:
	_mob_timer.start()
	_score_timer.start()
