## This is obsolete repository

This repository contains a deprecated snapshot of bot's source base. I **keep** maintaining bot, I just closed its sources.

Check out full list of my bots here: [tgdev.io](https://tgdev.io)

Use telegram groups to ask questions or share your thougts:

* [@tgdev_en](https://t.me/tgdev_en) - English speaking group
* [@tgdev_ru](https://t.me/tgdev_ru) - Russian speaking group

## About DaySandBox Bot

This bot implements simple anti-spam technique - it deletes all posts which:
1. contains link or mentions @username or been forwarded from somewhere
2. AND posted by the user who has joined the group less than 24 hours ago

This bot does not ban anybody, it only deletes messages by the rules listed above. The idea is that in these 24 hours the spamer would be banned anyway for posting spam to other groups that are not protected by this bot.


## Usage

1. Add [@daysandbox_bot](https://t.me/daysandbox_bot) to your group.
2. Go to group settings / users list / promote user to admin
3. Enable only one item: Delete messages
4. Click SAVE button
5. Enjoy!

To get more help submit `/help` command to the bot.
