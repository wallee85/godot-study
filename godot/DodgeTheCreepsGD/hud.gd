class_name HUD
extends CanvasLayer

signal start_game

@onready var _score_label: Label = $ScoreLabel
@onready var _level_label: Label = $LevelLabel
@onready var _message_label: Label = $MessageLabel
@onready var _start_button: Button = $StartButton
@onready var _message_timer: Timer = $MessageTimer


func show_message(text: String) -> void:
	_message_label.text = text
	_message_label.show()
	_message_timer.start()


func show_game_over() -> void:
	show_message("Game Over")
	await _message_timer.timeout

	_message_label.text = "Dodge the\nCreeps!"
	_message_label.show()
	await get_tree().create_timer(1.0).timeout

	_start_button.show()


func update_score(value: int) -> void:
	_score_label.text = str(value)


func update_level(value: int) -> void:
	_level_label.text = "Lv.%d" % value


func _on_start_button_pressed() -> void:
	_start_button.hide()
	start_game.emit()


func _on_message_timer_timeout() -> void:
	_message_label.hide()
