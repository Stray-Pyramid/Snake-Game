import pygame
import math
import os

_image_library = {}

def get_image(path):
	global _image_library
	image = _image_library.get(path)
	if image is None:
		conjoined_path = path.replace('/', os.sep).replace('\\', os.sep)
		image = pygame.image.load(conjoined_path)
		_image_library[path] = image
	return image

def circle_rect_collide(circle_p, circle_r, rect):
	# https://stackoverflow.com/questions/24727773/detecting-rectangle-collision-with-a-circle
	# Designate top, bottom, left, right points of circle
	cleft, ctop = circle_p[0] - circle_r, circle_p[1] - circle_r
	cright, cbottom = circle_p[0] + circle_r, circle_p[1] + circle_r

	# trivial reject if bounding boxes do not intersect
	if rect.right < cleft or rect.left > cright or rect.bottom < ctop or rect.top > cbottom:
		return False

	# check whether any point of rectangle is inside circle's radius
	for x in (rect.left, rect.left + rect.width):
		for y in (rect.top, rect.top + rect.height):
			# compare distance between circle's center point and each point of
			# the rectangle with the circle's radius
			if math.hypot(x - circle_p[0], y - circle_p[1]) <= circle_r:
				return True  # collision detected

	# check if center of circle is inside rectangle
	if rect.collidepoint(circle_p):
		return True  # overlaid

	# check if top, bottom, left, right point of circle is inside rectangle
	if rect.collidepoint((circle_p[0], circle_p[1] + circle_r))\
			or rect.collidepoint((circle_p[0], circle_p[1] - circle_r))\
			or rect.collidepoint((circle_p[0] + circle_r, circle_p[1]))\
			or rect.collidepoint((circle_p[0] - circle_r, circle_p[1])):
		return True


	return False  # no collision detected