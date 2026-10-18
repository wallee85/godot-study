class_name Player
extends Area2D

signal hit

@export_range(0.0, 2000.0, 10.0) var speed: float = 400.0

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _collision: CollisionShape2D = $CollisionShape2D
@onready var _trail: GPUParticles2D = $Trail

var _screen_size: Vector2 = Vector2.ZERO
var _current_animation: StringName = &""
var _is_animating: bool = false
var _flip_h: bool = false
var _flip_v: bool = false


func _ready() -> void:
	_screen_size = get_viewport_rect().size

	# 记住编辑器里的初始状态，后面只在与目标状态不同时写属性。
	_current_animation = _sprite.animation
	_flip_h = _sprite.flip_h
	_flip_v = _sprite.flip_v

	# 标题界面时玩家不可见，也不需要跑逻辑、参与碰撞。
	_collision.disabled = true
	set_process(false)
	hide()


func _process(delta: float) -> void:
	var direction: Vector2 = Input.get_vector(
		&"move_left", &"move_right", &"move_up", &"move_down"
	)
	var is_moving: bool = direction != Vector2.ZERO

	_update_animation(direction, is_moving)

	if not is_moving:
		return

	position = (position + direction * speed * delta).clamp(Vector2.ZERO, _screen_size)


## 开始（或重开）一局：复位玩家位置、动画和碰撞。
func start(pos: Vector2) -> void:
	position = pos
	rotation = 0.0

	_sprite.stop()
	_is_animating = false

	_collision.disabled = false
	show()
	set_process(true)


func _on_body_entered(_body: Node2D) -> void:
	hide()
	set_process(false)
	hit.emit()

	# 物理回调里不能直接改碰撞属性，要推迟到本帧物理计算之后。
	_collision.set_deferred(&"disabled", true)


func _update_animation(direction: Vector2, is_moving: bool) -> void:
	if is_moving != _is_animating:
		_is_animating = is_moving
		if is_moving:
			_sprite.play()
		else:
			_sprite.stop()

	if not is_moving:
		return

	if direction.x != 0.0:
		_set_animation(&"right")
		_set_flip(direction.x < 0.0, false)
		_trail.rotation = 0.0
	else:
		_set_animation(&"up")
		_set_flip(_flip_h, direction.y > 0.0)


func _set_animation(animation: StringName) -> void:
	if _current_animation == animation:
		return

	_current_animation = animation
	_sprite.animation = animation


func _set_flip(flip_h: bool, flip_v: bool) -> void:
	if _flip_h != flip_h:
		_flip_h = flip_h
		_sprite.flip_h = flip_h

	if _flip_v != flip_v:
		_flip_v = flip_v
		_sprite.flip_v = flip_v
