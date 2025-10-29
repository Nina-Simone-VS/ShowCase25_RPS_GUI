""" 
FILENAME: HandyMain.py
AUTHOR: Nina-Simone van Staden
DATE: October 2025
DESCRIPTION: Contains UI and Command Thread
"""

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
#from kivymd.uix.screenmanager import MDScreenManager
from kivy.logger import Logger

from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivymd.uix.gridlayout import MDGridLayout

#FOR COUNTDOWN
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

#CAMERA FEEDBACK
from kivy.graphics.texture import Texture
import cv2

#REMOVE when function are in
import random

#Set the fixed window size (1024 x 600) before the App is run
Window.size = (1024, 600)
#Window.resizable = False 

class ScoreRow(MDGridLayout):
    #for properties of custom scoreboard widget
    handy_score = StringProperty('0')
    opponent_score = StringProperty('0')


class GameScreen(MDScreen):
    """ROCK, PAPER, SCISSORS GAME SCREEN"""
    
    #initialise score array (3 rounds set to 0: Handy | Opponent)
    scoreboard = ListProperty([[0,0],[0,0],[0,0]])
    
    #round tracking
    round = NumericProperty(0)
    
    #set string properties
    start_btn_text = StringProperty("Start")
    results_text = StringProperty("Press 'Start' to begin a new 3-round game.")
    
    #paths for changing hand images
    handy_gesture = StringProperty('grey.png')
    opponent_gesture = StringProperty('grey.png')
    
    #countdown
    cd_text = StringProperty("")
    cd_colour= ListProperty(get_color_from_hex('444444')) 
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gestures = ['rock','paper','scissors']
        self.cd_step = 0
    #end constructor
    
    def on_enter(self, *args):
        #reset scoreboard
        self.reset_game()
        
        #reset images
        self.handy_gesture = 'grey.png'
        self.opponent_gesture = 'grey.png'
    #end on enter fn
    
    def det_round_outcome(self, handy_choice, opponent_choice):
        if handy_choice == opponent_choice:
            return 0,0, "It's a Draw!"
        elif (handy_choice == 'rock' and opponent_choice == 'scissors') or (handy_choice == 'paper' and opponent_choice == 'rock') or (handy_choice == 'scissors' and opponent_choice == 'paper'):
            return 1, 0, "Handy Wins!"
        else:
            return 0,1, "Opponent Wins!"
    #end round outcome fn
    
    def calc_round_winner(self):
        """ --- FUNCTION FOR R,P,S GAME ---"""
        gestures = ['rock', 'paper', 'scissors']
        
        # ~~~DELETE RANDOM SELECTION ~~#
        # Randomly choose gestures for both players
        handy_choice = random.choice(gestures)
        opponent_choice = random.choice(gestures)
        
        handy_score, opponent_score, message = self.det_round_outcome(handy_choice, opponent_choice)
        
        #Sset image paths
        self.handy_gesture = f'us_hand_{handy_choice}.png'
        self.opponent_gesture = f'opp_hand_{opponent_choice}.png'
        
        return handy_score, opponent_score, message
    #end calc round winner fn
    
    def reset_game(self):
        #reset
        self.scoreboard = [[0, 0], [0, 0], [0, 0]]
        self.start_btn_text = "Start"
        self.round = 0
        self.handy_gesture= 'grey.png'
        self.opponent_gesture = 'grey.png'
        
        self.cd_colour = get_color_from_hex('444444')
        self.cd_text = ""
        
        Logger.info("Handy: Resetting RPS Game Score.")
        self.results_text = "Press 'Start' to begin a new 3-round game."
    #end reset fn
    
    def start_game(self):
        
        #disable while counting down
        self.ids.start_reset_button.disabled = True
       
        if self.start_btn_text == "Start" or self.start_btn_text == "Play Again":
            self.reset_game()
            Logger.info("Handy: Starting RPS Game.")
            self.start_countdown()
        elif self.round < 3:
            #start countdown for the next round
            self.start_countdown()
    #end start game fn
    
    #COUNTDOWN FNS
    def start_countdown(self, *args):
        self.results_text = "..." 
        self.handy_gesture = 'grey.png'
        self.opponent_gesture = 'grey.png'
        self.cd_colour = get_color_from_hex('444444')        
       
        self.cd_step = 0
        #Call update_cd every 1 second
        Clock.schedule_interval(self.update_cd, 1) 
    #end start countdown fn
    
    def update_cd(self, dt):
        cd_steps = [
            ("Rock", get_color_from_hex("F44336")), # Red
            ("Paper", get_color_from_hex("F56D47")), # Orange 
            ("Scissors", get_color_from_hex("FF9800")), # Yellow 
            ("Shoot!", get_color_from_hex("78AD7F")) # Green 
        ]

        if self.cd_step < len(cd_steps):
            text, color = cd_steps[self.cd_step]
            self.cd_text = text
            self.cd_colour = color
            
            #update pictures
            if text in ['Rock', 'Paper', 'Scissors']:
                gesture_name = text.lower() 
                
                #Update BOTH images to the current gesture
                self.handy_gesture = f'us_hand_{gesture_name}.png' 
                self.opponent_gesture = f'opp_hand_{gesture_name}.png'
            elif text == 'Shoot!':
                # Clear the images (set back to the background placeholder) on 'Shoot!'
                self.handy_gesture = 'grey.png' 
                self.opponent_gesture = 'grey.png'
            #update countdown counter
            self.cd_step += 1
        else:
            #Countdown done
            Clock.unschedule(self.update_cd)
            #reset everything
            self.cd_text = "" 
            self.cd_colour = get_color_from_hex('444444')
            
            #perform rps task
            self.run_round_logic() 
    #end update countdown fn
    
    def run_round_logic(self):
        handy_score, opponent_score, message = self.calc_round_winner()
        
        #update scoreboard
        #MAKE NEW LIST TO UPDATE WHEN THERE'S A DRAW
        t_scoreboard = [list(row) for row in self.scoreboard]
        t_scoreboard[self.round] = [handy_score, opponent_score]
        self.scoreboard = t_scoreboard
        self.results_text = message
        
        self.round += 1
        
        #Check if Game over
        if self.round >= 3:
            total_handy = sum(score[0] for score in self.scoreboard)
            total_opponent = sum(score[1] for score in self.scoreboard)
            
            final_message = f"Game Over! Final Score: {total_handy} | {total_opponent}. "
            
            if total_handy > total_opponent :
                final_message += "Handy wins!" 
            elif total_opponent > total_handy:
                final_message += "Opponent Wins"
            else:
                final_message +="It's a Tie!" 
            
            self.results_text = final_message
            self.start_btn_text = "Play Again"
        else:
            #setup for next round
            self.results_text += f"\nRound {self.round + 1}: Click 'Next'"
            self.start_btn_text = "Next" 
            
        #Re-enable btn
        self.ids.start_reset_button.disabled = False
    #end run round logic fn

class CameraFeed:
    def __init__(self):
        self.capture = None
        self.texture= None
        self.is_running = False
    #end constructor
    
    def start(self, image_widget):
        if not self.is_running:
            self.capture = cv2.VideoCapture(0)
            
            if self.capture.isOpened():
                self.is_running = True
                self.image_widget = image_widget
                #update 1/30 of a second (30 FPS)
                Clock.schedule_interval(self.update, 1.0 / 30.0)
            else:
                Logger.error("Camera: Could not open video capture.")
                self.stop()
    #end start camera fn
    
    def stop(self):
        if self.is_running:
            Clock.unschedule(self.update)
            self.capture.release()
            
            self.capture = None
            self.is_running = False
            self.image_widget.texture = None # Clear image display
    #end stop camera fn
    
    def update(self, dt):
        #update image texture/widget (dt = delta time anf ret = return val)
        if self.is_running and self.capture.isOpened():
            ret, frame = self.capture.read()
            
            if ret:
                buf = cv2.flip(frame, -1).tobytes() #-1 = both x&y flips
                
                # Convert buffer to a texture
                self.texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]), 
                    colorfmt='bgr'
                )
                self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                
                #texture applied to kivy Image widget
                self.image_widget.texture = self.texture
    
    
class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass
    #end constructor
    
    #nav to main screen must delay start camera
    def on_enter(self, *args):
        Clock.schedule_once(self.start_camera, 0)
    #end OPEN main screen fn
    
    def start_camera(self, dt):
        if 'camera_image_widget' in self.ids:
            app = MDApp.get_running_app()
            app.camera_manager.start(self.ids.camera_image_widget)
        else:
            Logger.error("Camera: Couldn't find camera_image_widget ID in MainScreen")
    #end safely start cam fn
    
    #stop camera when leaving main screen
    def on_leave(self, *args):
        app = MDApp.get_running_app()
        app.camera_manager.stop()
    #end CLOSE main screen fn
    
    def on_mimic_press(self):
        """--- FUNCTION TO MIMIC CAMERA'S HANDS ---"""
        print("--- Mimic Mode Activated! (ADD OUR HAND MOVEY FUNCTION) ---")
        # In a real application, you would add your program logic here.
        Logger.info("Handy: Mimic Mode function called.")
    #end mimic btn press fn
        
    def switch_to_game(self):
        """Function to switch to the GameScreen using the ScreenManager."""
        self.manager.current = 'game'
        Logger.info("Handy: Swap to Game Screen.")
    #end game btn press fn



class HandyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple" # Use a standard, close palette
        self.theme_cls.theme_style = "Dark" 
        
        #load camera manager
        self.camera_manager = CameraFeed()
        
        #bring in kivy designs
        return Builder.load_file("handymain.kv")                                          
    #end build fn
    
    def on_stop(self):
        if hasattr(self, 'camera_manager'):
            self.camera_manager.stop()
            
        Logger.info("Handy: app will shutdown/stop")
        print("\nHandy is shutting down.")
    #end on stopping app
        
if __name__ == '__main__':
    HandyApp().run()