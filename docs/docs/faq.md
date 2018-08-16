# Daysandbox Bot FAQ

## How to install bot?

See [Installation](index.md#installation) instructions

## How to check if bot works?

* First, check that bot has permissions to delete messages
* Now ask anybody to **join** your chat and post link to google.com

If message was deleted then bot works.

## Is it possible to make bot not delete posts from admin?

Admin can just wait for 24 hours and then post links. If you changed default safe time
from 24 hours to some bigger value then probably you are doing something wrong. If you
want to delete any link from anybody except admins then just use [@watchdog_robot](https://t.me/watchdog_robot)

## Bot does not deletes some spam

Bot deletes links only from **new** users. If user is in chat for more than 24 hours then bot will not
delete any message from such user. Also bot does not process any message from users that were in the chat
on the moment whent bot was added to the chat. This is because bot can't find out join time of old users, it
can do it only for new users that join the chat where bot works already.

## Bot does not work

It works. Every day @daysandbox_bot deletes about 60-70 thousand spam messages.

## How to support the project?

Write a publication about daysandbox to your blog or social network. That would be enough.

## Where to send bug report?

Use github issues: [github.com/lorien/daysandbox/issue](https://github.com/lorien/daysandbox_bot/issue)

## How to contact with author of daysandbox?

My email is [lorien@lorien.name](mailto:lorien@lorien.name)

## Bot banned some user in my group by mistake

Bot **does not** ban anobydoy. There is no such feature in the bot.
