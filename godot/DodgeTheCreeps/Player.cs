using Godot;

namespace DodgeTheCreeps;

/// <summary>
/// 玩家角色。本文件是项目的 C# 写法样板，包含以下实践：
/// 1. 节点引用只在 _Ready 缓存一次，热路径不再 GetNode；
/// 2. 动作名 / 动画名 / 属性名统一用 StringName，避免每帧 string 转换；
/// 3. 用 Input.GetVector 一次取方向，代替多次 IsActionPressed；
/// 4. Position 读一次 → 局部变量里算完 → 只写一次（Vector2 是值类型）；
/// 5. 动画、翻转等属性只在状态变化时写入（脏检查）；
/// 6. 热路径零分配：不用 LINQ、不建闭包、不每帧 new；
/// 7. 失效时关闭处理，复活时再打开，避免隐藏状态下白跑逻辑。
/// </summary>
public partial class Player : Area2D
{
	[Signal]
	public delegate void HitEventHandler();

	[Export]
	public float Speed { get; set; } = 400f;

	private static readonly StringName MoveLeft = "move_left";
	private static readonly StringName MoveRight = "move_right";
	private static readonly StringName MoveUp = "move_up";
	private static readonly StringName MoveDown = "move_down";

	private static readonly StringName AnimRight = "right";
	private static readonly StringName AnimUp = "up";

	private AnimatedSprite2D _sprite;
	private CollisionShape2D _collision;

	private Vector2 _screenSize;
	private StringName _currentAnimation;
	private bool _isAnimating;
	private bool _flipH;
	private bool _flipV;

	public override void _Ready()
	{
		_sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
		_collision = GetNode<CollisionShape2D>("CollisionShape2D");

		// 视口尺寸是固定基准分辨率，缓存一次即可，不要每帧问引擎。
		_screenSize = GetViewportRect().Size;

		_currentAnimation = _sprite.Animation;
		_flipH = _sprite.FlipH;
		_flipV = _sprite.FlipV;

		// 还没 Start 之前不该被撞到，也不需要每帧跑逻辑。
		_collision.Disabled = true;
		SetProcess(false);

		Hide();
	}

	public override void _Process(double delta)
	{
		// 一次调用拿到方向，长度已被限制在 1（键盘斜向即单位向量），无需再 Normalize。
		Vector2 direction = Input.GetVector(MoveLeft, MoveRight, MoveUp, MoveDown);
		bool isMoving = direction != Vector2.Zero;

		UpdateAnimation(direction, isMoving);

		if (!isMoving)
		{
			return;
		}

		// Position 是引擎属性，每次读写都要跨 native 边界；这里只读一次、只写一次。
		Vector2 position = Position;
		position += direction * Speed * (float)delta;
		position = position.Clamp(Vector2.Zero, _screenSize);
		Position = position;
	}

	/// <summary>开始（或重开）本局：复位状态并重新接管玩家。</summary>
	public void Start(Vector2 position)
	{
		Position = position;

		_sprite.Stop();
		_isAnimating = false;

		_collision.Disabled = false;
		Show();
		SetProcess(true);
	}

	public void OnBodyEntered(PhysicsBody2D body)
	{
		Hide();

		// 先停掉处理再通知外部：监听者即使在 Hit 回调里立刻重开，也不会被这里覆盖。
		SetProcess(false);

		EmitSignal(SignalName.Hit);

		// 物理回调里不能直接改碰撞属性，必须延迟到本帧物理计算之后。
		_collision.SetDeferred(CollisionShape2D.PropertyName.Disabled, true);
	}

	private void UpdateAnimation(Vector2 direction, bool isMoving)
	{
		if (isMoving != _isAnimating)
		{
			_isAnimating = isMoving;

			if (isMoving)
			{
				_sprite.Play();
			}
			else
			{
				_sprite.Stop();
			}
		}

		if (!isMoving)
		{
			return;
		}

		if (direction.X != 0f)
		{
			SetAnimation(AnimRight);
			SetFlip(direction.X < 0f, false);
		}
		else
		{
			SetAnimation(AnimUp);
			SetFlip(_flipH, direction.Y > 0f);
		}
	}

	private void SetAnimation(StringName animation)
	{
		if (_currentAnimation == animation)
		{
			return;
		}

		_currentAnimation = animation;
		_sprite.Animation = animation;
	}

	private void SetFlip(bool flipH, bool flipV)
	{
		if (_flipH != flipH)
		{
			_flipH = flipH;
			_sprite.FlipH = flipH;
		}

		if (_flipV != flipV)
		{
			_flipV = flipV;
			_sprite.FlipV = flipV;
		}
	}
}
