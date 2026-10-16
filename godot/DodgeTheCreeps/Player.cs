using Godot;
using System;

namespace DodgeTheCreeps;

public partial class Player : Area2D
{
	[Signal]
	public delegate void HitEventHandler();

	[Export]
	public int Speed { get; set; } = 400;// how fast the player moves

	public Vector2 ScreenSize { get; set; }

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		ScreenSize = GetViewportRect().Size;
		Hide();
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		var velocity = Vector2.Zero;

		if (Input.IsActionPressed("move_right"))
		{
			velocity.X += 1;
		}
		if (Input.IsActionPressed("move_left"))
		{
			velocity.X -= 1;
		}
		if (Input.IsActionPressed("move_down"))
		{
			velocity.Y += 1;
		}
		if (Input.IsActionPressed("move_up"))
		{
			velocity.Y -= 1;
		}

		var animatedSprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");

		if (velocity.Length() > 0)
		{
			velocity = velocity.Normalized() * Speed;
			animatedSprite.Play();
		}
		else
		{
			animatedSprite.Stop();
		}

		Position += velocity * (float)delta;

		Position = new Vector2(
			Mathf.Clamp(Position.X, 0, ScreenSize.X),
			Mathf.Clamp(Position.Y, 0, ScreenSize.Y)
		);

		if (velocity.X != 0)
		{
			animatedSprite.Animation = "right";
			animatedSprite.FlipV = false;
			animatedSprite.FlipH = velocity.X < 0;
		}
		else if (velocity.Y != 0)
		{
			animatedSprite.Animation = "up";
			animatedSprite.FlipV = velocity.Y > 0;
		}
	}

	public void Start(Vector2 position)
	{
		Position = position;
		Show();
		GetNode<CollisionShape2D>("CollisionShape2D").Disabled = false;
	}

	public void OnBodyEntered(PhysicsBody2D body)
	{
		Hide(); // Player disappears after being hit.
		EmitSignal(SignalName.Hit);
		// Must be deferred as we can't change physics properties on a physics callback.
		GetNode<CollisionShape2D>("CollisionShape2D").SetDeferred(CollisionShape2D.PropertyName.Disabled, true);
	}
}
