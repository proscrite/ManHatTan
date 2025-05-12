from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from skimage.io import imread
from skimage import img_as_ubyte
from skimage.transform import resize
import numpy as np


PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Battlers/'

def show_pkm(nid):
    # nid = 94
    nid = np.random.randint(900)
    print('NID: ', nid)
    impath = PATH_ANIM+str(nid).zfill(3)+'.png'
    anim0 = imread(impath)
    anim = image_to_texture(anim0)
    # upscaled_image = resize(im_rgba, (400, 400, 4), anti_aliasing=True)
    
    nframe = 0
    
    frame = anim[:, anim.shape[0] * nframe: anim.shape[0] * (nframe+1) , :]

    return frame

def image_to_texture(frame):
    """
    Convert a NumPy array (frame) to a Kivy Texture using skimage.
    """
    # Ensure the frame is in RGBA format
    if frame.shape[2] == 3:  # If the image has 3 channels (RGB)
        alpha_channel = np.ones((frame.shape[0], frame.shape[1], 1), dtype=np.uint8) * 255  # Fully opaque
        frame_rgba = np.concatenate((frame, alpha_channel), axis=-1)
    elif frame.shape[2] == 4:  # If the image has an alpha channel
        frame_rgb = frame[:, :, :3]  # Keep only RGB channels
        alpha_channel = np.ones((frame_rgb.shape[0], frame_rgb.shape[1], 1), dtype=np.uint8) * 255  # Fully opaque
        frame_rgba = np.concatenate((frame_rgb, alpha_channel), axis=-1)
        
        if (alpha_channel < 255).any():
            print("The image contains transparency.")
        else:
            print("The alpha channel exists but does not contain transparency.")

    else:
        print('Shape: ', frame.shape[2])

    # upscaled_image = resize(frame_rgba, (400, 400, 4), anti_aliasing=True)

    # Convert image to 8-bit unsigned integers
    frame_ubyte = img_as_ubyte(frame_rgba)

    # Create a texture and upload data
    texture = Texture.create(size=(frame_ubyte.shape[1], frame_ubyte.shape[0]))
    texture.blit_buffer(frame_ubyte.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
    texture.flip_vertical()
    return texture

def preprocess_anim(frame):
    """
    Convert a NumPy array (frame) to a Kivy Texture.
    """

    size_frame = frame.shape[0]
    n_channels = frame.shape[2]
    nframes = int(frame.shape[1] / size_frame)

    texture = image_to_texture(frame)
    # # Add an alpha channel to convert RGB to RGBA
    # if n_channels == 3:  # If the image has 3 channels (RGB)
    #     alpha_channel = np.ones((frame.shape[0], frame.shape[1], 1), dtype=np.uint8) * 255  # Fully opaque
    #     frame_rgba = np.concatenate((frame, alpha_channel), axis=-1)
    # elif n_channels == 4:  # If the image has an alpha channel
    #     frame_rgba = frame[:, :, :3]  # Keep only RGB channels
    # else:
    #     print('Shape: ', frame.shape[2])
    
    # # Convert image to 8-bit unsigned integers
    # frame_byte = img_as_ubyte(frame_rgba)
    # upscaled_image = resize(frame_byte, (400, 400*nframes, 3), anti_aliasing=True)
    
    return frame, nframes, texture

class AnimationApp(App):
    def build(self):
        # Create a BoxLayout to hold the Image widget
        self.layout = BoxLayout()
        
        # Add the Image widget to display the frames
        self.image = Image()
        self.layout.add_widget(self.image)
        
        self.frame_index = 0
        nid = np.random.randint(900)
        nid = 9
        impath = PATH_ANIM+str(nid).zfill(3)+'.png'
        anim = imread(impath)

        anim, nframes, texture = preprocess_anim(anim)

        self.frames = [ anim[:, anim.shape[0] * i: anim.shape[0] * (i+1), :]   for i in range(nframes)]
        # self.frames = [resize(f, (400, 400, 3), anti_aliasing=True) for f in mini_frames]
        # self.frames = [f"PATH_ANIM+'003.png" for i in range(20)]  # Path to your frames
        
        # Schedule the frame update
        
        # Clock.schedule_interval(self.update_frame, 1 / 24)  # 24 frames per second
        
        return self.layout

    def update_frame(self, dt):
        # Get the current frame
        frame = self.frames[self.frame_index]
        
        # Convert the frame to a Kivy texture
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]))
        texture.blit_buffer(
            frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte'
        )
        texture.flip_vertical()
        
        # Update the Image widget with the new texture
        self.image.texture = texture
        
        # Increment the frame index and loop back at the end
        self.frame_index = (self.frame_index + 1) % len(self.frames)

# Run the app
if __name__ == "__main__":
    AnimationApp().run()