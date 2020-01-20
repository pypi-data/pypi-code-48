import arcade

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 260
SCREEN_CENTER_X = SCREEN_WIDTH*0.5
TOP_SPRITE_Y = SCREEN_HEIGHT*0.75
BOTTOM_SPRITE_Y = SCREEN_HEIGHT*0.25
FILE_NAME = ":resources:images/animated_characters/female_person/femalePerson_idle.png"

class Master(arcade.Window):
    def __init__(self):
        arcade.Window.__init__(self, SCREEN_WIDTH,  SCREEN_HEIGHT)
        self.texture_1 = arcade.load_texture(FILE_NAME)
        self.texture_2 = arcade.load_texture(FILE_NAME)
    def run(self):
        arcade.run()
    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_CENTER_X, TOP_SPRITE_Y, self.texture_1.width, self.texture_1.height, self.texture_1)
        arcade.draw_texture_rectangle(SCREEN_CENTER_X, BOTTOM_SPRITE_Y, self.texture_2.width, self.texture_2.height, self.texture_2)

    def on_mouse_release(self, x, y, button, modifiers):
        self.texture_2.height*=1.5


if __name__ == '__main__':
    app = Master()
    app.run()