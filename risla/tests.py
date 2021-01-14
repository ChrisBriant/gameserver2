from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import random, string, re


class ChatTests(ChannelsLiveServerTestCase):
    serve_static = True  # emulate StaticLiveServerTestCase

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            # NOTE: Requires "chromedriver" binary to be installed in $PATH
            cls.driver = webdriver.Chrome()
            pass

        except:
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        #cls.driver.quit()
        super().tearDownClass()


    def test_game(self):
        try:
            self._open_new_window()
        finally:
            pass
            #self._close_all_new_windows()


    def _open_new_window(self):
        #Open three tabs and add a name for each
        #self.driver = webdriver.chrome()
        for i in range(0,3):
            self.driver.execute_script('window.open("");')
            self.driver.switch_to_window(self.driver.window_handles[-1])
            self.driver.get('http://localhost:8000/risla')
            self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
            self.driver.find_element_by_id("addname").click()
        #Open first tab and create a room
        self.driver.switch_to_window(self.driver.window_handles[1])
        letters = string.ascii_letters
        roomname = ''.join(random.choice(letters) for i in range(6))
        self.driver.find_element_by_id("roomname").send_keys(roomname)
        self.driver.find_element_by_id("createroom").click()
        #Other two join the room
        self.driver.switch_to_window(self.driver.window_handles[2])
        join = self.driver.find_element_by_class_name('join-btn')
        print(join)
        join.click()
        self.driver.switch_to_window(self.driver.window_handles[3])
        join = self.driver.find_element_by_class_name('join-btn')
        print(join)
        join.click()
        #Start a game
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('start').click()
        #A user guesses correctly
        #1. get the celbrity name
        self.driver.switch_to_window(self.driver.window_handles[2])
        label = self.driver.find_element_by_class_name('celeb')
        nameguess = label.text.replace('Famous person name: ', '')
        #2. enter the name
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('question-input').send_keys(nameguess)
        self.driver.find_element_by_id('send-question').click()

        #Next player takes turn
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('question-input').send_keys('Am I a an object?')
        self.driver.find_element_by_id('send-question').click()
        #Other player response no
        self.driver.switch_to_window(self.driver.window_handles[3])
        self.driver.find_element_by_id('no').click()
        #Turn switch over
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('end-turn-btn').click()
        #Player c asks a question
        self.driver.switch_to_window(self.driver.window_handles[3])
        self.driver.find_element_by_id('question-input').send_keys('Am a rich?')
        self.driver.find_element_by_id('send-question').click()
        #Player b responds
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('yes').click()
        #Player c makes correct guess - trigger end of game
        self.driver.switch_to_window(self.driver.window_handles[3])
        self.driver.find_element_by_id('end-turn-btn').click()
        #get the celeb
        self.driver.switch_to_window(self.driver.window_handles[2])
        label = self.driver.find_elements_by_class_name('celeb')[1]
        nameguess = label.text.replace('Famous person name: ', '')
        self.driver.switch_to_window(self.driver.window_handles[3])
        self.driver.find_element_by_id('question-input').send_keys(nameguess)
        self.driver.find_element_by_id('send-question').click()

    def test_rooms(self):
        try:
            for i in range(0,4):
                self.driver.execute_script('window.open("");')
                self.driver.switch_to_window(self.driver.window_handles[-1])
                self.driver.get('http://localhost:8000/risla')
                self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
                self.driver.find_element_by_id("addname").click()
            #Create a room
            self.driver.switch_to_window(self.driver.window_handles[1])
            letters = string.ascii_letters
            roomname = ''.join(random.choice(letters) for i in range(6))
            self.driver.find_element_by_id("roomname").send_keys(roomname)
            self.driver.find_element_by_id("createroom").click()
            #Another player joins
            self.driver.switch_to_window(self.driver.window_handles[2])
            join = self.driver.find_element_by_class_name('join-btn')
            join.click()
            #Create another room
            self.driver.switch_to_window(self.driver.window_handles[3])
            letters = string.ascii_letters
            roomname = ''.join(random.choice(letters) for i in range(6))
            self.driver.find_element_by_id("roomname").send_keys(roomname)
            self.driver.find_element_by_id("createroom").click()
            #A player starts the game, we expect to see the room list update
            self.driver.switch_to_window(self.driver.window_handles[1])
            self.driver.find_element_by_id('start').click()
            self.driver.switch_to_window(self.driver.window_handles[4])
        finally:
            pass
            #self._close_all_new_windows()

    def different_browser(self):
        #Create two rooms and join a second player
        for i in range(0,2):
            self.driver.execute_script('window.open("");')
            self.driver.switch_to_window(self.driver.window_handles[-1])
            self.driver.get('http://localhost:8000/risla')
            self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
            self.driver.find_element_by_id("addname").click()
        self.driver.switch_to_window(self.driver.window_handles[1])
        letters = string.ascii_letters
        roomname = ''.join(random.choice(letters) for i in range(6))
        self.driver.find_element_by_id("roomname").send_keys(roomname)
        self.driver.find_element_by_id("createroom").click()
        self.driver.switch_to_window(self.driver.window_handles[2])
        join = self.driver.find_element_by_class_name('join-btn')
        join.click()
        #Open Firefox manually and check you can join the room

    def player_disconnect(self):
        #Test what happens when player disconnects session mid game
        #Set up three sessions
        for i in range(0,3):
            self.driver.execute_script('window.open("");')
            self.driver.switch_to_window(self.driver.window_handles[-1])
            self.driver.get('http://localhost:8000/risla')
            self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
            self.driver.find_element_by_id("addname").click()
        self.driver.switch_to_window(self.driver.window_handles[1])
        letters = string.ascii_letters
        roomname = ''.join(random.choice(letters) for i in range(6))
        self.driver.find_element_by_id("roomname").send_keys(roomname)
        self.driver.find_element_by_id("createroom").click()
        self.driver.switch_to_window(self.driver.window_handles[2])
        join = self.driver.find_element_by_class_name('join-btn')
        join.click()
        self.driver.switch_to_window(self.driver.window_handles[3])
        join = self.driver.find_element_by_class_name('join-btn')
        join.click()
        #Disconnect the middle player
        #self.driver.switch_to_window(self.driver.window_handles[2])
        #self.driver.close()
        #Works okay before game is started
        #MID GAME TEST
        # self.driver.execute_script('window.open("");')
        # self.driver.switch_to_window(self.driver.window_handles[-1])
        # self.driver.get('http://localhost:8000/risla')
        # self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
        # self.driver.find_element_by_id("addname").click()
        #Start Game
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('start').click()
        #Disconnect the middle player
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.close()
        #Start convo
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('question-input').send_keys('Is this really happening?')
        self.driver.find_element_by_id('send-question').click()
        #Other player response no
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('no').click()
        #Turn switch over
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('end-turn-btn').click()
        #Test end game in this mode
        label = self.driver.find_elements_by_class_name('celeb')[0]
        nameguess = label.text.replace('Famous person name: ', '')
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('question-input').send_keys(nameguess)
        self.driver.find_element_by_id('send-question').click()
        #self.driver.switch_to_window(self.driver.window_handles[1])


    def owner_disconnect(self):
        #Test what happens when player disconnects session mid game
        #Set up three sessions
        for i in range(0,3):
            self.driver.execute_script('window.open("");')
            self.driver.switch_to_window(self.driver.window_handles[-1])
            self.driver.get('http://localhost:8000/risla')
            self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
            self.driver.find_element_by_id("addname").click()
        self.driver.switch_to_window(self.driver.window_handles[1])
        letters = string.ascii_letters
        roomname = ''.join(random.choice(letters) for i in range(6))
        self.driver.find_element_by_id("roomname").send_keys(roomname)
        self.driver.find_element_by_id("createroom").click()
        self.driver.switch_to_window(self.driver.window_handles[2])
        join = self.driver.find_element_by_class_name('join-btn')
        join.click()
        self.driver.switch_to_window(self.driver.window_handles[3])
        join = self.driver.find_element_by_class_name('join-btn')
        join.click()
        #Disconnect the middle player
        #self.driver.switch_to_window(self.driver.window_handles[2])
        #self.driver.close()
        #Works okay before game is started
        #MID GAME TEST
        # self.driver.execute_script('window.open("");')
        # self.driver.switch_to_window(self.driver.window_handles[-1])
        # self.driver.get('http://localhost:8000/risla')
        # self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
        # self.driver.find_element_by_id("addname").click()
        #Start Game
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('start').click()
        #Disconnect the owner
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.close()
        #Start convo
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('question-input').send_keys('Is this really happening?')
        self.driver.find_element_by_id('send-question').click()
        #Other player response no
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('no').click()
        #Turn switch over
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('end-turn-btn').click()
        #Test end game in this mode
        label = self.driver.find_elements_by_class_name('celeb')[0]
        nameguess = label.text.replace('Famous person name: ', '')
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('question-input').send_keys(nameguess)
        self.driver.find_element_by_id('send-question').click()
        #self.driver.switch_to_window(self.driver.window_handles[1])

    def all_disconnect(self):
        #Test what happens when all players disconnect mid game
        for i in range(0,3):
            self.driver.execute_script('window.open("");')
            self.driver.switch_to_window(self.driver.window_handles[-1])
            self.driver.get('http://localhost:8000/risla')
            self.driver.find_element_by_id("nickname").send_keys(chr(i+65))
            self.driver.find_element_by_id("addname").click()
        self.driver.switch_to_window(self.driver.window_handles[1])
        letters = string.ascii_letters
        roomname = ''.join(random.choice(letters) for i in range(6))
        self.driver.find_element_by_id("roomname").send_keys(roomname)
        self.driver.find_element_by_id("createroom").click()
        self.driver.switch_to_window(self.driver.window_handles[2])
        join = self.driver.find_element_by_class_name('join-btn')
        join.click()
        self.driver.switch_to_window(self.driver.window_handles[3])
        join = self.driver.find_element_by_class_name('join-btn')
        join.click()
        #Start Game
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('start').click()
        #Disconnect the owner
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.close()
        #Start convo
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('question-input').send_keys('Is this really happening?')
        self.driver.find_element_by_id('send-question').click()
        #Other player response no
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.find_element_by_id('no').click()
        #Turn switch over
        self.driver.switch_to_window(self.driver.window_handles[1])
        self.driver.find_element_by_id('end-turn-btn').click()
        self.driver.switch_to_window(self.driver.window_handles[2])
        self.driver.close()
