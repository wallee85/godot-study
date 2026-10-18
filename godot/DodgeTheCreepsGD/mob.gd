class_name Mob
extends RigidBody2D


func _ready() -> void:
	var sprite: AnimatedSprite2D = $AnimatedSprite2D
	var animation_names: PackedStringArray = sprite.sprite_frames.get_animation_names()
	var animation_index: int = randi() % animation_names.size()

	sprite.animation = StringName(animation_names[animation_index])
	sprite.play()


func _on_visible_on_screen_notifier_2d_screen_exited() -> void:
	queue_free()
