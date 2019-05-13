import math
import pygame
from pygame_utils import get_image

class Entity(object):
	def __init__(self, pos=(0, 0)):
		self.pos = pos

class Fruit(Entity):
	BAD_FRUIT_SPRITE = get_image("images/bad_pear.png")
	GOOD_FRUIT_SPRITE = get_image("images/good_pear.png")
	EXCEPTIONAL_FRUIT_SPRITE = get_image("images/exceptional_pear.png")
	GODLY_FRUIT_SPRITE = get_image("images/godly_pear.png")

	FRUIT_SIZE = BAD_FRUIT_SPRITE.get_size()

	BAD = 0
	GOOD = 1
	EXCEPTIONAL = 2
	GODLY = 3

	def __init__(self, pos, type_of_fruit):
		Entity.__init__(self, pos)
		self.type = type_of_fruit
		self.rect = pygame.Rect(pos, self.FRUIT_SIZE)

	def draw(self, surface):
		if self.type == Fruit.BAD:
			surface.blit(self.BAD_FRUIT_SPRITE, self.pos)
		elif self.type == Fruit.GOOD:
			surface.blit(self.GOOD_FRUIT_SPRITE, self.pos)
		elif self.type == Fruit.EXCEPTIONAL:
			surface.blit(self.EXCEPTIONAL_FRUIT_SPRITE, self.pos)
		elif self.type == Fruit.GODLY:
			surface.blit(self.GODLY_FRUIT_SPRITE, self.pos)


class SnakeSegment(object):
	
	def __init__(self, pos, rotation):
		self.pos_history = [pos]
		self.dir_history = [rotation]
	
	@property
	def pos(self):
		return self.pos_history[0]
	
	@property
	def direction(self):
		return self.dir_history[0]

class Snake(Entity):

	SPEED = .2
	TURN_SPEED = .05
	SEGMENT_SIZE = (8, 8)
	SEGMENT_SEPARATION = 3 # num of updates apart
	
	HEAD_SPRITE = get_image("images/snake_head.png")
	BODY_SPRITE = get_image("images/snake_body.png")
	TAIL_SPRITE = get_image("images/snake_tail.png")
	
	
	def __init__(self, pos, direction):
		Entity.__init__(self, pos)

		self.direction = direction
		self.alive = True
		self.segments = [SnakeSegment(pos, 0), SnakeSegment(pos, 0)]

	@property
	def head_pos(self):
		return self.segments[0].pos
	
	@property
	def length(self):
		return len(self.segments)
	
	def grow(self, num):
		#Spawn segments on the tail of the snake
		for _ in range(num):
			snake_tail_pos = self.segments[-1].pos
			self.segments.append(SnakeSegment(snake_tail_pos, 0))


	def handle_input(self, key_states):
		if key_states[pygame.K_a] or key_states[pygame.K_LEFT]:
			self.direction += self.TURN_SPEED

		if key_states[pygame.K_d] or key_states[pygame.K_RIGHT]:
			self.direction -= self.TURN_SPEED

	def update(self, dt):
		# Update the head of the snake
		x = self.head_pos[0] + ((self.SPEED * dt) * math.sin(self.direction))
		y = self.head_pos[1] + ((self.SPEED * dt) * math.cos(self.direction))

		self.segments[0].pos_history.insert(0, (x, y))
		self.segments[0].dir_history.insert(0, self.direction)
		
		# Update the rest of the snake
		for i in range(0, len(self.segments) - 1):
			if len(self.segments[i].pos_history) <= self.SEGMENT_SEPARATION:
				break

			self.segments[i + 1].pos_history.insert(0, self.segments[i].pos_history.pop())
			self.segments[i + 1].dir_history.insert(0, self.segments[i].dir_history.pop())
			
		if len(self.segments[-1].pos_history) > self.SEGMENT_SEPARATION:
			del self.segments[-1].pos_history[-1]
			del self.segments[-1].dir_history[-1]
	
	def draw_segment(self, surface, segment, sprite):
		s = pygame.Surface(self.SEGMENT_SIZE, pygame.SRCALPHA)
		s.blit(sprite, (0, 0))
		s = pygame.transform.rotate(s, math.degrees(segment.dir_history[0]) - 90)
		
		surface.blit(s, (segment.pos[0] - (self.SEGMENT_SIZE[0]/2), segment.pos[1] - (self.SEGMENT_SIZE[0]/2)))
		
	def draw(self, surface):
		self.draw_segment(surface, self.segments[0], self.HEAD_SPRITE)
		for segment in self.segments[1:-1]:
			self.draw_segment(surface, segment, self.BODY_SPRITE)
		self.draw_segment(surface, self.segments[-1], self.TAIL_SPRITE)
		
		
