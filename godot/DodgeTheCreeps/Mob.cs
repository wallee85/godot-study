using Godot;
using System;

namespace DodgeTheCreeps;

public partial class Mob : RigidBody2D
{
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		var animatedSprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
		string[] mobTypes = animatedSprite.SpriteFrames.GetAnimationNames();
		animatedSprite.Play(mobTypes[GD.Randi() % mobTypes.Length]);
	}

	public void OnVisibleOnScreenNotifier2DScreenExited()
	{
		QueueFree();
	}
}
