# Update List

## Version 1.0.0

1. Add version to Dice Bot.
2. Show update list in the log window.

## Version 1.0.1

1. Add restart app option to indicate whether restarts the app after detecting focusing app error (Thanks to JueXiu_Huang).

## Version 1.0.2

1. Split setting to several page.
2. Change waiting detect function parameters.

## Version 1.0.3

1. Add random offset to mimic human behavior.

## Version 1.0.4

1. Add disconnect button after connecting.

## Version 1.0.5

1. Add detect delay.
2. Handle the detect error and show message.
3. Catch win32 API error

## Version 1.0.6

1. Remove random offset of close AD function

## Version 1.0.7

1. Fix detect delay bug.

## Version 1.0.8

1. Show full traceback message while error occur.

## Version 1.0.9

1. Set option to restarting detect delay.

## Version 1.1.0

1. Add version check.
2. Fix restart app bugs.

## Version 1.2.0

1. Change party setting UI.

## Version 1.2.1

1. Fix action bug.

## Version 1.2.2

1. Fix action bug.

## Version 1.2.3

1. Change parameter type in function --- action.
2. Add load screenshot button.
3. Add ADB mode to specific using ip and port or device id.

## Version 1.2.4

1. Add StrictOrderMerge for Joker dice.
2. Add lateGame judgement.
3. Add new action loop for Joker dice.

## Version 1.2.5

1. Add result statistic
2. Add file dialog when saving the screenshot
3. Change init button to result result button

## Version 1.2.6

1. Fix joker bug
2. Fix result statistic bug

## Version 1.2.7

1. Fix misclick on report button
2. Fix init bug

## Version 1.2.8

1. Modify log message
2. Modify star detection algorithm

## Version 1.2.9

1. Use two screenshot to avoid detecting error on dice star

## Version 1.3.0

1. Finish Task 6 and add Stage 6
2. Stage 5 when summon 25 dices
3. Move old Stage 5 to Stage 6

## Version 1.3.1

1. Fix state error when stop detecting immediately after finish the game.

## Version 1.3.2

1. Auto add 'SolorX' to team list when 'Solor' in team list

## Version 1.3.3

1. Fix result bug

## Version 1.3.4

1. Remove Stage 6
2. Add requirements.txt

## Version 1.3.5

1. Modify the window size
2. Fix star detection bug

## Version 1.3.6

1. Add app freeze detection
2. Record the flags to ini file

## Version 1.3.7

1. Fix app freeze detection bug
2. Modify default value of freeze threshold

## Version 1.3.8

1. Add share party button to share the party information and copy the image to clipboard
2. Record result value to ini file

## Version 1.3.9

1. Revise Meteor's isMerge
2. Center the windows
3. Fix the bugs of Solar

## Version 1.3.10

1. Fix detect bug when dice is 7-star

## Version 1.3.11

1. Fix detect bug when dice is 7-star
2. Fix detect dice bug
3. Fix detect star bug when dice is Fire
4. Now the image space will be reserved at the beginning
5. Add test tab to test detecting the dices

## Version 1.4.0

1. Fix detect star bug when dice is 7-star
2. Fix detect star bug when dice is Charm
3. Speed up the screenshot
4. Add dice statistic in 1v1 mode
5. Fix screenshot width in setting tab

## Version 1.5.0

1. Add Cleanse dice image
2. Optimal Berserk, SolorX, and Squad dice image
3. Add detect number model
4. Fix screenshot bug
5. Add detect trophy chart
6. Fix detect dice star bug
7. Show error when screenshot failed
8. Modify window arrangement (Move buttons to detect tab)
9. Add checkBox to choose whether to add dice to chart
10. Modify default value of freeze threshold to 50
11. Record battle mode to file

## Version 1.5.1

1. Fix the bug of trophy's information

## Version 1.5.2

1. Add a threshold to detect the focus app
2. Add the version limitation to opencv
3. Fix the information data in the trophy chart
4. Store the detected failed image
5. Modify the merge order

## Version 1.5.3

1. Move all Joker Copy to same place
2. Change the merge rule of Joker
3. Add max growth restriction when doing joker copy
4. Remove Growth from list instead of swap when src_star>dice_level (strictOrderMerge)
5. Add error/* into gitignore

## Version 1.6.0

1. Add Arcade mode
2. Add focusThreshold
3. Update number detect model

## Version 1.6.1

1. Change weighted random function
2. Add change tab step to Arcade mode
3. Add share board button
4. Modify freeze function parameter
5. Add notify result function

## Version 1.6.2

1. Add try catch to line notify
2. Add new dice - Gravity
3. Add dice star detect mode
4. Add dice detect model

## Version 1.6.3

1. Add dev mode to save each extract image
2. Remove time delay during non-Waiting status
3. Arrange buttons

## Version 1.6.4

1. Add new dice - Typhoon
2. Fix Squad and Electric dice star detect

## Version 1.6.5

1. Fix Gun dice star detect bug
2. Add checkpoint to check the stage progress

## Version 1.7.0

1. Replacing the ADB low-level implementation
2. Fix lobby detect bug
3. Change screenshot function
4. Add screenshot image to UI

## Version 1.7.1

1. Fix Squad dice star bug
2. Add garbage collector

## Version 1.7.2

1. Add control to mirror screen
2. Change update function of mirror screen
3. Fix ADB ID bugs
4. Specify the version of sklearn

## Version 1.7.3

1. Add new dice: Infect and Lightning
2. Add cpu and memory usage
3. Update number detection model
4. Add another check point
5. Add wave detection
6. Fix trophy detection bug
7. Add screenshot delay
8. Modify action

## Version 1.8.0

1. Update action
2. Remove Sp

## Version 1.8.1

1. Update action
2. Fix detect trophy bug
3. Add new dice: Cowboy
4. Modify the task flow
5. Add some information: elapsed time & wave
6. Modify the screen location

## Version 1.9.0

1. Add updater
2. Add max_fps and bitrate to setting

## Version 1.10.0

1. Add icon
2. Board Dice Offset XY now can set as float type
3. Modify dashboard format
4. Fix load image bug
5. Add new dice detect mode
6. Add joker copy detecter
7. Add encouragement stage
8. Fix stage change bug
9. Modify the delay between stages
10. Fix detect AD bug
11. Update action to greedy

## Version 1.10.1

1. Add new dice (Angel, Cannon, Gear, Mafia, Sacrifice, and Target)
2. Fix the bug showing old version after updating to latest version

## Version 1.11.0

1. Rename dice (Squad -> Commando)
2. Add new dice (Jet)
3. Now can use browser to control the emulator
4. Add a setting to adjust the drag speed
5. Fix the bug that the dice star can be recognized greater than 7
6. Restart the app while waiting for a long time
7. Change auto play to default setting, add last game to stop the game

## Version 1.11.1

1. Fix the update bug

## Version 1.11.2

1. Fix the update bug

## Version 1.11.3

1. Fix detect lobby bug
2. Modify the joker copy limit

## Version 1.11.4

1. Fix the bot will halt when announcement/daily dialog pop up

## Version 1.11.5

1. Fix close button bug
2. Modify the right top corner distance function

## Version 1.11.6

1. Add new dice (Blizzard, EMP)
2. Fix trophy detect bug

## Version 1.12.0

1. Add new dice (Firework)
2. Add video recording feature
3. Add flip screen option
4. Add adaptive dice detect mode
5. Add encouragement mode
6. Modify valid joker algorithm
7. Modify joker copy algorithm
