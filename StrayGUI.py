# StrayGUI - a gui for pygame with css styling
# based off of factorio's gui
# By StrayPyramid 13/04/2019
# Released under a "Simplified BSD" license

import pygame

pygame.font.init()

DEBUG = False
MARGIN_DEBUG_COLOUR =   (255,   0,   0)
PADDING_DEBUG_COLOUR =  (255, 165,   0)
CONTENTS_DEBUG_COLOUR = (255, 255,   0)

# This is bad. change this.
WINDOW_SIZE = (1024, 768)

class Size(object):
	def __init__(self, size: tuple = None):
		if size is None:
			self.width = 0
			self.height = 0
		else:
			self.width = size[0]
			self.height = size[1]


class Position(object):
	def __init__(self, pos: tuple = None):
		if pos is None:
			self.x = 0
			self.y = 0
		else:
			self.x = pos[0]
			self.y = pos[1]


class Spacing(object):
	def __init__(self, *args):
		# So it can handle both tuples and individual elements
		if len(args) == 1:
			if isinstance(args[0], Spacing):
				self.left = args[0].left
				self.right = args[0].right
				self.top = args[0].top
				self.bottom = args[0].bottom
			else:
				self.top = args[0][0]
				self.right = args[0][1]
				self.bottom = args[0][2]
				self.left = args[0][3]
		elif len(args) == 4:
			self.top = args[0]
			self.right = args[1]
			self.bottom = args[2]
			self.left = args[3]
		else:
			print("Error: Spacing object received invalid number of arguments!")


class TextAlign(object):
	LEFT = "left"
	CENTER = "center"
	RIGHT = "right"
	JUSTIFIED = "justified"


# class Position(Enum):
#	static = 1   # Default value. Elements render in order, as they appear in the document flow
#	absolute = 1 # The element is posed relative to its first posed (not static) ancestor element
#	fixed = 1	 # The element is posed relative to the browser window
#	relative = 1 # The element is posed relative to its normal pos, so "left:20px" adds 20 pixels to the element's LEFT pos
#	#sticky = 1
#	initial = 1  # Sets this property to its default value. Read about initial
#	inherit = 1  # Inherits this property from its parent element. Read about inherit

# types include: frame, label, sprite, button, sprite-button
# less important types: checkbox, radiobutton, progressbar, table

class Frame(object):
	
	DEFAULT_STYLE = {
		'pos': 'relative',
		'h-align': "center",
		'v-align': "center",
		'margin': Spacing(0, 0, 0, 0),
		'padding': Spacing(0, 0, 0, 0),
		'colour': (0, 0, 0),
		'background-colour': None,
		'font-size': 12,
		'font': 'Arial'
	}
	
	def __init__(self, kind="frame", caption=None, tooltip=None, enabled=True, ignored_by_interaction=False,
				 style=None):
		
		self.style = self.DEFAULT_STYLE
		self.set_style(style)

		###
		self.kind = kind
		self.parent = None
		self.children = []
		self.visible = True
		self.caption = caption
		self.tooltip = tooltip
		self.enabled = enabled
		self.ignored_by_interaction = ignored_by_interaction

		##
		self.text_surface = None
		self.clicked = False
		self.mouse_over = False

		#
		self.margin_rect = pygame.Rect(0, 0, 0, 0)
		self.padding_rect = None
		self.content_rect = None

	@property
	def pos(self):
		return self.margin_rect.topleft

	@pos.setter
	def pos(self, new_pos):
		self.margin_rect.topleft = new_pos
		self.padding_rect.topleft = (self.pos[0] + self.style["margin"].left, self.pos[1] + self.style["margin"].top)
		self.content_rect.topleft = (self.padding_rect.left + self.style["padding"].left, self.padding_rect.top + self.style["padding"].top)

	def add(self, kind="frame", caption=None, tooltip=None, enabled=True, ignored_by_interaction=False, style=None):
		new_gui_element = Frame(kind, caption, tooltip, enabled, ignored_by_interaction, style)
		new_gui_element.parent = self
		self.children.append(new_gui_element)
		return new_gui_element

	# Must be called before reacting to new events
	def react(self, events):
		reacted = False
		self.clicked = False

		for child in self.children:
			reacted = child.react(events)

		if self.kind == "button" and reacted is False:
			for event in events:
				if event.type == pygame.MOUSEBUTTONDOWN:
					if self.point_is_inside(pygame.mouse.get_pos()):
						self.clicked = True

	def clear(self):
		for child in self.children:
			child.clear()
			child.destroy()

	def destroy(self):
		self.clear()
		self.parent.children.remove(self)
		del self
	
	def set_style(self, style):
		if style is None:
			return
		
		if "padding" in style:
			style["padding"] = Spacing(style["padding"])
		
		if "margin" in style and type(style["margin"]) == tuple:
			style["margin"] = Spacing(style["margin"])
		
		self.style = {**self.style, **style}  # Merge the two styles

	def point_is_inside(self, pos):
		return self.padding_rect.collidepoint(pos)

	def render(self):
		if self.enabled is False:
			return

		# We need to know:
		# HOW BIG IS IT
		# WHERE IS IT

		# Render: child -> parent
		# Draw: parent -> child

		# Absolute pos
		# Relative pos

		# Render the children first, and then base size around them
		max_width = 0
		total_width = 0
		max_height = 0
		total_height = 0
		
		
		for child in self.children:
			child.render()

			if child.margin_rect.width > max_width:
				max_width = child.margin_rect.width

			if child.margin_rect.height > max_height:
				max_height = child.margin_rect.height

			total_width += child.margin_rect.width
			total_height += child.margin_rect.height

		# Render the caption so we know how large it is
		if (self.kind == "label" or self.kind == "button") and self.caption is not None:
			font = pygame.font.SysFont(self.style["font"], self.style["font-size"])
			self.text_surface = font.render(self.caption, True, self.style["colour"])

			text_width =  self.text_surface.get_width()
			text_height = self.text_surface.get_height()

			if text_width > max_width:
				max_width = text_width

			if text_height > max_height:
				max_height = text_height

			total_width += text_width
			total_height += text_height

		# Size of element is based on if width and height are set in style properties
		# is they are set, element gets its render height and width from style
		# if they are not set, element calculates height and width from child elements

		# At the moment, all child elements are stacked vertically, aligned to the left.
		content_width = 0
		content_height = 0
		
		if "width" in self.style:
			if type(self.style["width"]) == int:
				content_width = self.style["width"]
			elif type(self.style["width"]) == str:
				# TODO: percentage width needs to be taken from parents width.
				# At the moment, this isn't possible due to the order of rendering.
				width_percentage = int(self.style["width"][:-1]) / 100
				content_width = WINDOW_SIZE[0] * width_percentage
		else:
			content_width = max_width
		
		if "height" in self.style:
			if type(self.style["height"]) == int:
				content_height = self.style["height"]
			elif type(self.style["height"]) == str:
				# TODO: percentage height needs to be taken from parents height.
				# At the moment, this isn't possible due to the order of rendering.
				height_percentage = int(self.style["height"][:-1]) / 100
				content_height = WINDOW_SIZE[0] * height_percentage
		else:
			content_height = max_height
		
		
		
		
		
		self.content_rect = pygame.Rect(0, 0, content_width, content_height)
		self.padding_rect = pygame.Rect(0, 0, self.style["padding"].left + self.style["padding"].right + content_width,
											  self.style["padding"].top + self.style["padding"].bottom + content_height)

		if self.style["margin"] == 'auto' and "width" in self.style:
			self.margin_rect = pygame.Rect(self.pos[0], self.pos[1], self.parent.margin_rect.width, self.padding_rect.height)
		else:
			self.margin_rect = pygame.Rect(self.pos[0], self.pos[1], self.style["margin"].left + self.style["margin"].right + self.padding_rect.width,
											 self.style["margin"].top + self.style["margin"].bottom + self.padding_rect.height)

		self.padding_rect.center = self.margin_rect.center
		self.content_rect.center = self.margin_rect.center

		total_height = 0
		for child in self.children:
			child.pos = (self.content_rect.left, self.content_rect.top + total_height)
			total_height += child.margin_rect.height
		
		# Detect if the mouse if over the element
		self.mouse_over = self.point_is_inside(pygame.mouse.get_pos())
		
	def draw(self, screen):
		if self.enabled is False:
			return

		# Draw background
		if self.mouse_over and "hover-colour" in self.style and self.style[
			"hover-colour"] is not None:
			screen.fill(self.style["hover-colour"], self.padding_rect)
		else:
			if "background-colour" in self.style and self.style["background-colour"] is not None:
				screen.fill(self.style["background-colour"], self.padding_rect)  # Draw background

		if DEBUG:
			pygame.draw.rect(screen, MARGIN_DEBUG_COLOUR, self.margin_rect, 1)
			pygame.draw.rect(screen, PADDING_DEBUG_COLOUR, self.padding_rect, 1)
			pygame.draw.rect(screen, CONTENTS_DEBUG_COLOUR, self.content_rect, 1)


		# Draw Border
		border_width = self.style["border-width"] if "border-width" in self.style else 0
		border_colour = self.style["border-colour"] if "border-colour" in self.style else (255, 255, 255)
		border_style = self.style["border-style"] if "border-style" in self.style else "solid"

		if border_width > 0:
			pygame.draw.rect(screen, border_colour, self.padding_rect, border_width)


		# Draw text
		if self.text_surface is not None:
			# Default: text is aligned to left
			text_pos = self.content_rect.topleft

			if "text-align" in self.style and self.style["text-align"] is not None:
				if self.style["text-align"] == TextAlign.CENTER:
					# TODO
					text_pos = (self.content_rect.centerx - self.text_surface.get_width()/2, self.content_rect.top)

				elif self.style["text-align"] == TextAlign.RIGHT:
					# TODO
					text_pos = (self.content_rect.topright - self.text_surface.get_width(), self.content_rect.top)

				elif self.style["text-align"] == TextAlign.JUSTIFIED:
					pass

			screen.blit(self.text_surface, text_pos)  # Draw text

		# Draw children
		for child in self.children:
			child.draw(screen)