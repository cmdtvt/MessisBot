from PIL import Image, ImageFont, ImageDraw #ImageEnhance
import urllib
import requests
import random
import shutil



class ImageEditor():
	def __init__(self,url,name,bio,msgtotal):
		self.basedir = "assets/image-edit/"
		self.name = name
		self.bio = bio
		self.msgtotal = msgtotal
		self.fontSize(40)

		response = requests.get(url, stream=True)
		with open(self.basedir+'source.png', 'wb') as out_file:
			shutil.copyfileobj(response.raw, out_file)
		del response
		self.avatar_image = Image.open(self.basedir+"source.png")


	def fontSize(self,size):
		self.font = ImageFont.truetype(self.basedir+"fonts/TCM.TTF",size)



	def createProfile(self): #### This generates profile info image
		self.img = Image.new('RGB', (1000,800), (255, 255, 255))
		self.background_image = Image.open(self.basedir+"backgrounds/field1.jpeg")
		self.borders_image = Image.open(self.basedir+"borders/border1.png")
		self.foreground_image = Image.open(self.basedir+"foregrounds/foreground1.png")


		self.background_image = self.background_image.resize((1000,350),resample=0)
		self.avatar_image = self.avatar_image.resize((155,155),resample=0)
		self.img.paste(self.background_image, (0,0))
		self.img.paste(self.foreground_image,(0,0),self.foreground_image.convert("RGBA"))
		self.img.paste(self.avatar_image,(61,232),self.avatar_image.convert("RGBA"))
		self.img.paste(self.borders_image,(0,0),self.borders_image.convert("RGBA"))

		self.fontSize(40)
		drawtext = ImageDraw.Draw(self.img)
		drawtext.text((235, 290),self.name,(0,0,0), font=self.font)

		self.fontSize(32)
		drawtext = ImageDraw.Draw(self.img)
		drawtext.text((235, 400),self.bio,(0,0,0), font=self.font)

		self.fontSize(28)
		drawtext = ImageDraw.Draw(self.img)
		drawtext.text((235, 750),"Total messages: "+str(self.msgtotal),(0,0,0), font=self.font)

		#self.background_image.paste(self.img, (50,50))

		self.img.save(self.basedir+"result.png", "PNG")


#url = ""
#image_editor = ImageEditor(url)
#image_editor.createProfile()
#del image_editor
#quit()