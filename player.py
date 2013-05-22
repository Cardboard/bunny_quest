import os
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
	super(Player, self).__init__(*groups)
	self.rect = pygame.Rect(location[0], location[1], 16,16)
	self.frame = 0
	self.width = 16
	self.height = 16
	self.dy = 0
	self.resting = True
	self.checkpoint = 1
	# images and animation
	self.image = pygame.image.load(os.path.join('graphics', 'bunny.png'))
	self.images = {}
	self.current_image = 'idle'
	self.flipped = False # flip image vertically or not
	self.images = {'idle': [[], 4], 'run': [[], 6], 'jump': [[], 1], 'vault': [[], 4]}
	self.anim_speed = 50
	self.anim = 0
	self.anim_over = True # makes sure jumping animation is over before changing image
	self.images['idle'][0] = self.splitFrames(0,0,self.images['idle'][1])
	self.images['run'][0] = self.splitFrames(0,self.height,self.images['run'][1])
	self.images['jump'][0] = self.splitFrames(\
		2,self.height,self.images['jump'][1])
	self.images['vault'][0] = self.splitFrames(0,self.height*2,self.images['vault'][1])
	# sound effects
	self.sounds = {'jump':pygame.mixer.Sound(os.path.join('sound', 'jump.wav')),\
		'vault':pygame.mixer.Sound(os.path.join('sound', 'vault.wav')),\
		'death':pygame.mixer.Sound(os.path.join('sound', 'death2.wav'))}


		

    def splitFrames(self, startx, starty, num_frames):
	images = []
	for x in range(startx*self.width, self.width*(startx+num_frames), self.width):
	    newframe = pygame.transform.scale(
	    self.image.subsurface((x, starty, self.width, self.height)),
		(self.width*1, self.height*1))
	    images.append(newframe)
	return images

    def frameCheck(self, dt):
	if self.current_image == 'jump':
	    self.anim_speed = 0
	    self.frame = 0
	else:
	    self.anim_speed = 50
	if self.current_image == 'vault'\
	and self.frame == self.images['vault'][1]-1:
	    self.anim_over = True
	    self.current_image = 'idle'
	    self.frame = 0
	if self.anim >= self.anim_speed:
	    if self.frame >= self.images[self.current_image][1]-1:
		self.frame = 0
		if self.anim_over == False:
		    self.anim_over = True
	    else:
		self.frame += 1
	    self.anim = 0
	else:
	    self.anim += dt
    
    def update(self, dt, game):
	last = self.rect.copy()
	self.dy += 1 
	self.dy = min(self.dy, 16)
	self.rect.y += self.dy/2

	key = pygame.key.get_pressed()
	if key[pygame.K_LEFT]:
	    self.rect.x -= 125  * dt / 1000
	    self.flipped = True
	    self.anim_over = False
	    if self.resting and self.current_image != 'vault':
		self.current_image = 'run'
	if key[pygame.K_RIGHT]:
	    self.rect.x += 125 * dt / 1000
	    self.flipped = False
	    self.anim_over = False
	    if self.resting and self.current_image != 'vault':
		self.current_image = 'run'
	if not(key[pygame.K_LEFT] or key[pygame.K_RIGHT]) and self.resting:
	    if self.anim_over:
		self.current_image = 'idle'
	if self.resting and key[pygame.K_SPACE]:
	    self.current_image = 'jump'
	    self.sounds['jump'].play()
	    self.dy = -12
	    self.resting = False

	# collision
	# walls/ground
	new = self.rect
	for cell in game.tilemap.layers['triggers'].collide(new, 'block'):
	    block = cell['block']
	    if last.right <= cell.left and new.right > cell.left:
		if 'v' in block:
		    self.dy = -7
		    if self.current_image != 'vault':
			self.frame = 0
			self.sounds['vault'].play()
		    self.current_image = 'vault'
		new.right = cell.left
	    if last.left >= cell.right and new.left < cell.right:
		if 'v' in block:
		    self.dy = -7
		    if self.current_image != 'vault':
			self.frame = 0
			self.sounds['vault'].play()
		    self.current_image = 'vault'
		new.left = cell.right
	    if 't' in block and last.bottom <= cell.top and new.bottom > cell.top:
		new.bottom = cell.top
		self.dy = 0
		self.resting = True
	    if 'b' in block and last.top >= cell.bottom and new.top < cell.bottom:
		new.top = cell.bottom
		self.dy = 0
	# lava lava lava
	if game.tilemap.layers['triggers'].collide(new, 'death'):
	    for cell in game.tilemap.layers['triggers'].find('checkpoint'):
		if cell.properties.values()[0] == self.checkpoint:
		    self.rect.center = (cell.px, cell.py)
		    self.sounds['death'].play()
	# checkpoints
	for cell in game.tilemap.layers['triggers'].collide(new, 'save'):
	    value = cell.properties.values()[0]
	    self.checkpoint = value

	# set image to correct image
	self.frameCheck(dt)
	self.image = pygame.transform.flip(self.images[self.current_image][0][self.frame], self.flipped, False)
	game.tilemap.set_focus(self.rect.x, self.rect.y)
