# android_automation

This repository is a library that I am writing to enable me to automate my android phone.

The android debug bridge (adb) is a debug tool that ships with the android operating system to enable pulling and pushing of files, sending touch events, sideloading apps and more.

I am using it to be able to view and control my phone remotely, and in some cases, fully automate it.

Included in this repository are two examples of using this library to automatically solve two different puzzle games

## Tents and Trees

The rules for this game are simple:
1) Every tree must be paired with an adjacent tent
2) No tents can be touching (diagonals included)
3) Every column and every row must have the correct number of tents as indicated in the margins

The program reads the screen continuously and parses the image using template matching (and other more sophisticated techniques) and feeds the result to a game-solving engine. The program solves the puzzle in less than a second, then it sends tap events to the phone to execute the solution.

Here is a video showing the execution of the AI when viewing the phone's screen.

<img src="https://github.com/tsierens/android_automation/blob/master/tents_and_trees/tents_and_trees_solved.gif" height="400" width="225">

## Connect Me

The rules for this game are simple:
1) Each tile can only move in specific ways:
    1) Tiles with a circle in the middle can be rotated
    1) Tiles with vertical arrows can move vertically
    1) Tiles with horizontal arrows can move horizontally
1) Tiles must have all links matching up with the links of other tiles

The program takes an image of the screen, and parses the image using template matching and feeds the result to a game-solving engine. The program once again solves the game in less than a second, then it plans on how to issue the commands to the phone, and then executes the solution.

Here is a video showing the execution of the AI when viewing the phone's screen

<img src="https://github.com/tsierens/android_automation/blob/master/connect_me/connect_me_solved.gif" height="400" width="225">
