# Slither Snake
# By StrayPyramid 13/04/2019
# Released under a "Simplified BSD" license

import pygame
import sys
import math
import random
import datetime

import StrayGUI
from Snake_Styles import *
from SnakeFruits_Class import *
import pygame_utils

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()


WINDOW_SIZE = (1024, 768)
BACKGROUND_COLOUR = (148, 212, 237)
GAME_NAME = "Slither Snake"

#pygame.FULLSCREEN
main_screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption(GAME_NAME)



clock = pygame.time.Clock()


class State(object):
	@staticmethod
	def update(self, dt):
		print("Error: update not defined!")
	
	@staticmethod
	def draw(self):
		print("Error: draw not defined!")


class Menu(State):
	def __init__(self):
		self.guiBox = StrayGUI.Frame(style=body_style)
		self.title_label = self.guiBox.add(kind="label", caption=GAME_NAME, style=title_style)
		self.helpA_label = self.guiBox.add(kind="label", caption="You are SNEK. Eat the coloured pears, and avoid the grey pears.")
		self.helpB_label = self.guiBox.add(kind="label", caption="Hitting the border will cause death! That is all.")
		self.play_button = self.guiBox.add(kind="button", caption="Play", style=button_style)
		self.exit_button = self.guiBox.add(kind="button", caption="Exit", style=button_style)
		
		
	def handle_input(self):
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		self.guiBox.react(events)
		
	def update(self, dt):
		if self.play_button.clicked:
			return Game()
		
		if self.exit_button.clicked:
			pygame.quit()
			sys.exit()
		
		self.guiBox.render()

		return self

	def draw(self, screen):
		# Draw GUI elements
		self.guiBox.draw(screen)
		

class Game(State):
	
	game_area = WINDOW_SIZE
	FRUIT_SPAWN_MARGIN = 20
	
	
	# https://www.youtube.com/watch?v=G3JhFvgipU4
	pygame.mixer.music.load("jazz_music.mp3")
	
	munch_sfx = pygame.mixer.Sound("Munch SFX.wav")
	
	BG_MUSIC_FADEOUT_TIME = 500
	
	def __init__(self):

		self.snake = None
		self.fruits = []
		self.alive_for = 0
		
		
		# Spawn a new snake, remove any existing fruits
		self.reset()

		self.guiBox = StrayGUI.Frame(kind="frame", style=body_style)
		self.snake_length_label = self.guiBox.add(kind="label", style=label_style)
		self.pause_button = self.guiBox.add(kind="button", caption="Pause", style=button_style)
		self.exit_button = self.guiBox.add(kind="button", caption="Exit", style=button_style)

	def reset(self):
		start_x = random.randint(WINDOW_SIZE[0] / 2 - WINDOW_SIZE[0] / 4, WINDOW_SIZE[0] / 2 + WINDOW_SIZE[0] / 4)
		start_y = random.randint(WINDOW_SIZE[1] / 2 - WINDOW_SIZE[1] / 4, WINDOW_SIZE[1] / 2 + WINDOW_SIZE[1] / 4)

		self.snake = Snake((start_x, start_y), random.random() * (2 * math.pi))
		self.fruits = []
		self.spawn_fruit()
		self.alive_for = 0
		
		pygame.mixer.music.rewind()
		pygame.mixer.music.play()

	def spawn_fruit(self, fruit_type=None):
		# Decide what type of fruit it is
		if fruit_type is None:
			rand_float = random.random()
			if rand_float < 0.6:
				fruit_type = Fruit.GOOD
			elif rand_float < 0.8:
				fruit_type = Fruit.EXCEPTIONAL
			else:
				fruit_type = Fruit.GODLY

		# Pick a location for the new fruit
		while True:
			fruit_spawn_pos = (random.randint(self.FRUIT_SPAWN_MARGIN, self.game_area[0] - self.FRUIT_SPAWN_MARGIN - Fruit.FRUIT_SIZE[0]),
							   random.randint(self.FRUIT_SPAWN_MARGIN, self.game_area[1] - self.FRUIT_SPAWN_MARGIN - Fruit.FRUIT_SIZE[1]))
			
			new_fruit = Fruit(fruit_spawn_pos, fruit_type)
			
			collides_with_fruit = False
			for fruit in self.fruits:
				if fruit.rect.colliderect(new_fruit.rect):
					collides_with_fruit = True
					break
			
			if collides_with_fruit:
				print("Colliding with fruit")
				continue
			
			collides_width_snake = False
			for segment in self.snake.segments:
				if pygame_utils.circle_rect_collide(segment.pos, self.snake.SEGMENT_SIZE[0] * 2, new_fruit.rect):
					collides_width_snake = True
					
			if collides_width_snake:
				print("Colliding with snake")
				continue
			
			break
		
		self.fruits.append(new_fruit)

	def handle_input(self):
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		self.guiBox.react(events)
		
		pressed = pygame.key.get_pressed()
		self.snake.handle_input(pressed)

	def update(self, dt):
		if self.pause_button.clicked:
			return Pause(self)

		if self.exit_button.clicked:
			pygame.quit()
			sys.exit()
		
		self.alive_for += dt
		
		#If snake out of bounds, game over
		head_pos = self.snake.head_pos
		if 0 > head_pos[0] or head_pos[0] > self.game_area[0] or 0 > head_pos[1] or head_pos[1] > self.game_area[1]:
			print("Game over!")
			pygame.mixer.music.fadeout(self.BG_MUSIC_FADEOUT_TIME)
			return Gameover(self, "ran into a wall")

		# Check if snake colliding with fruit
		for fruit in self.fruits:
			for snake_part in self.snake.segments:
				if pygame_utils.circle_rect_collide(snake_part.pos, self.snake.SEGMENT_SIZE[0], fruit.rect):
					if fruit.type == fruit.BAD:
						pygame.mixer.music.fadeout(self.BG_MUSIC_FADEOUT_TIME)
						return Gameover(self, "ate a bad pear")
					else:
						print("Picked up fruit!")
						self.munch_sfx.play()
						self.snake.grow(fruit.type)
						self.fruits.remove(fruit)
						self.spawn_fruit(Fruit.BAD)
						self.spawn_fruit()
					break
				
		# Update the snake
		self.snake.update(dt)
		
		# Update GUI
		self.snake_length_label.caption = "Length: %s" % len(self.snake.segments)
		self.guiBox.render()

		return self

	def draw(self, surface):
		# Draw entities
		self.snake.draw(surface)

		# Draw Fruits
		for fruit in self.fruits:
			fruit.draw(surface)

		# Draw GUI elements
		self.guiBox.draw(surface)


class Gameover(State):
	oof_sfx = pygame.mixer.Sound("oof.wav")
	
	def __init__(self, previous_state, death_reason):
		self.previous_state = previous_state

		self.guiBox = StrayGUI.Frame(style=body_style)
		self.title_label = self.guiBox.add(kind="label", caption="You Died!", style=title_style)
		self.play_button = self.guiBox.add(kind="button", caption="Play Again", style=button_style)
		self.exit_button = self.guiBox.add(kind="button", caption="Exit", style=button_style)

		# Statistics
		tt_alive = datetime.timedelta(milliseconds=int(self.previous_state.alive_for))
		hours_alive = int(tt_alive.seconds / 3600)
		minutes_alive = int((tt_alive.seconds - (hours_alive * 3600))/60)
		seconds_alive = int(tt_alive.seconds - (minutes_alive * 60) - (hours_alive * 3600))
		age_string = "%s hours, %s minutes, and %s seconds." % (hours_alive, minutes_alive, seconds_alive)

		self.snake_length_label = self.guiBox.add(kind="label", caption="Your snake was %s pieces long!" % previous_state.snake.length, style=label_style)
		self.snake_age_label = self.guiBox.add(kind="label", caption="You were alive for %s" % age_string, style=label_style)
		self.snake_death_label = self.guiBox.add(kind="label", caption="You died because you %s" % death_reason, style=label_style)
		
		self.guiBox.render()
		
		self.oof_sfx.play()

	def handle_input(self):
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		self.guiBox.react(events)

	def update(self, dt):
		if self.play_button.clicked:
			self.previous_state.reset()
			return self.previous_state

		if self.exit_button.clicked:
			pygame.quit()
			sys.exit()
		
		self.guiBox.render()
		return self

	def draw(self, screen):
		# Draw GUI elements
		self.guiBox.draw(screen)

class Pause(State):
	def __init__(self, previous_state):
		self.previous_state = previous_state
		
		self.guiBox = StrayGUI.Frame(style=body_style)
		self.resume_button = self.guiBox.add(kind="button", caption="Resume", style=pause_style)

	def handle_input(self):
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		self.guiBox.react(events)
		
	def update(self, dt):
		if self.resume_button.clicked:
			return self.previous_state
		
		self.guiBox.render()
		return self
	
	def draw(self, surface):
		self.previous_state.draw(surface)
		
		s = pygame.Surface(WINDOW_SIZE)
		s.set_alpha(120)
		s.fill((0, 0, 0))
		surface.blit(s, (0, 0))
		
		self.guiBox.draw(surface)


def main():
	active_state = Menu()
	
	is_running = True
	while is_running:
		active_state.handle_input()
		next_state = active_state.update(clock.get_time()) # The number of milliseconds that passed between the previous two calls to Clock.tick().
		
		if next_state != active_state:
			next_state.update(0)
			active_state = next_state
		
		main_screen.fill(BACKGROUND_COLOUR)
		active_state.draw(main_screen)
		pygame.display.flip()
		clock.tick(60)
	
	pygame.quit()

if __name__ == "__main__":
	main()