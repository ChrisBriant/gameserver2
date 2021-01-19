export PATH=$PATH:/usr/local/share/

python3 manage.py test risla.tests.ChatTests.test_game
python3 manage.py test risla.tests.ChatTests.test_rooms
python3 manage.py test risla.tests.ChatTests.different_browser
python3 manage.py test risla.tests.ChatTests.player_disconnect
python3 manage.py test risla.tests.ChatTests.owner_disconnect
python3 manage.py test risla.tests.ChatTests.all_disconnect
python3 manage.py test risla.tests.ChatTests.test_leave
python3 manage.py test risla.tests.ChatTests.all_leave
python3 manage.py test risla.tests.ChatTests.test_questions
python3 manage.py test risla.tests.ChatTests.test_play_game_start_new
python3 manage.py test risla.tests.ChatTests.test_room_destroys
