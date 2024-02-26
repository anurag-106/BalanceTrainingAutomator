import os
import pyautogui
from PIL import ImageGrab
import time
import subprocess
import json
import re
import datetime
from datetime import datetime, timedelta

class GamesAutomator:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.login_status = False
        self.key_mappings = {
            "Start_Stop": "pageup",
            "Up": "f6",
            "Down": "f9",
            "Next": "f8",
            "OK": "pagedown",
            "Rewind": "f7"
        }
        self.recordings_dir = "C:\\Virtusense\\Azure Kinect Recordings\\Gait\\Pavani\\dev testing area"
        self.log_dir = "C:\\Virtusense\\VSClient\\Logs\\VSKinectPlugin"
        self.report_dir = "C:\\Virtusense\\Azure Kinect Recordings\\Reports"
        self.vsclient_path = "C:\\VirtuSense\\VSClient\\bin\\VSClient.exe" 
        self.previous_real_name_path = "previous_real_name.txt"
        self.project_dir = "C:\\Users\\User\\Desktop\\BalanceAutomation"
        self.json_file_path = "C:\\Virtusense\\Azure Kinect Recordings\\video_keyboard_inputs.json"
        self.json_data = self.read_json()

    def read_json(self):
        with open(self.json_file_path, 'r') as file:
            return json.load(file)

    def login(self):
        self.kill_process()
        self.run_playback_powershell_script()
        pyautogui.hotkey('winleft', 'r')
        pyautogui.typewrite(self.vsclient_path)
        pyautogui.press('enter')
        self.find_and_click_target("login.png", 20)
        pyautogui.typewrite('sam')
        pyautogui.press("tab")
        pyautogui.typewrite('123123')
        pyautogui.press('enter')
        self.login_status = True

    def mouseclick(self,x, y):
        pyautogui.click(x, y)

    import subprocess

    def run_playback_powershell_script(self):
        script = '''
        $filepath = "C:\\Virtusense\\VSClient\\bin\\VSClientSettings.xml"
        $lineNumber = 63
        $newContent = "	  <type>VSKinect2Plugin.AzureKinectPlaybackPlugin</type>"
        $lines = Get-Content $filepath
        $lines[62] = $newContent  # Adjusted for zero-based indexing
        $lines | Set-Content $filepath
        '''
        subprocess.run(["powershell", "-Command", script], check=True)




    def find_and_click_target(self, image_path, timeout_seconds, conf=None, region=None, scroll=None):
        start_time = time.time()
        attempt = 0
        while (time.time() - start_time) < timeout_seconds:
            attempt += 1
            found = pyautogui.locateCenterOnScreen(image_path, confidence=conf, region=region) if conf else pyautogui.locateCenterOnScreen(image_path, region=region)
            if found:
                self.mouseclick(*found)
                print(f"Found on attempt {attempt} - Time taken: {time.time() - start_time}s at cordinates {found}")
                return True
            else:
                if attempt == 1:
                    print(f"Attempt {attempt}: '{image_path}' not found in region '{region}'. Retrying...")
                else:
                    print(f"Attempt {attempt}: Retrying...")

                if scroll and attempt > 2 :  # Scroll only after second attempt
                    print('Scrolling started')
                    center_x, center_y = self.screen_width // 2, self.screen_height // 2
                    pyautogui.moveTo(center_x, center_y)
                    pyautogui.scroll(-100)  # Scrolls up; use pyautogui.scroll(100) to scroll down
                
                time.sleep(1)  # Wait a bit before retrying

        print(f"Failed to find '{image_path}' after {timeout_seconds}s.")
        return False
    
    def read_previous_real_name(self):
        try:
            with open("previous_real_name.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def write_previous_real_name(self,real_name):
        with open("previous_real_name.txt", "w") as f:
            f.write(real_name)

    def switch_video(self, video='los1.mkv'):
        self.kill_process()  # Assuming kill_process is another method in your class
        os.chdir(self.recordings_dir)
        previous_real_name = self.read_previous_real_name()  # Method to read the previous name from a file
        time.sleep(10)  # Wait to ensure the process is fully terminated

        try:
            if previous_real_name:
                os.rename("normal.mkv", previous_real_name)
        except FileNotFoundError:
            pass  # Ignore if the file doesn't exist

        try:
            os.rename(video, "normal.mkv")
            self.write_previous_real_name(video)  # Method to write the new name to a file
            print(f"'{video}' is now named 'normal.mkk'")
        except FileNotFoundError:
            print(f"'{video}' not found. No changes were made.")
        finally:
            os.chdir(self.project_dir) 


    def kill_process(self, process_name="VSClient.exe"):
        try:
            if self.login_status:
                subprocess.run(["taskkill", "/F", "/IM", process_name], check=True)
                print(f"Terminated {process_name} successfully.")
            else:
                print(f"{process_name} not active.")
        except subprocess.CalledProcessError:
            print(f"Failed to terminate {process_name}.")

    def training_page(self):
        if not self.login_status:
            self.login()
        # Define the region for the upper right quarter of the screen
        region = (self.screen_width // 2, 0, self.screen_width // 2, self.screen_height // 2)
        self.find_and_click_target("TRAINING.png", 10, region=region)

    def timed_keyboard_inputs(self,input_sequence):
        #Automates keyboard inputs at specified time intervals.  
        #:param input_sequence: List of tuples containing (key, delay_in_seconds)
        start_time = time.time()
        for key, delay in input_sequence:
            # Calculate elapsed time to adjust sleeping time
            elapsed_time = time.time() - start_time
            sleep_time = delay - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)
            pyautogui.press(key)
            print(f"Pressed {key} after {delay} seconds")

    def los_training_session(self):
        # Implementation for LOS training
        video = self.json_data["los_training"]["video_input"]
        keyboard_inputs = self.json_data["los_training"]["keyboard_input"]
        xml_report_data = self.json_data["los_training"]["report"]
        self.videoswitch(video) #change the video to los video
        self.training_page()
        self.find_and_click_target("LOS_TRAINING1.png", 10)
        self.find_and_click_target("START_TRAINING.png", 20)
        self.find_and_click_target("LOS_TRAINING_START.png", 20)
        self.timed_keyboard_inputs(keyboard_inputs)
        self.kill_process()
        self.extract_current_report_data()

 
    def simon_says_session(self):
        # Implementation based on the Simon_says_Session function

    def load_report_values(self):
        # Implementation based on the Load_report_values function

    # Additional methods for mouseclick, read/write previous real name, etc.
  
# Usage example
if __name__ == "__main__":
    automator = GamesAutomator()
    automator.los_training_session()
