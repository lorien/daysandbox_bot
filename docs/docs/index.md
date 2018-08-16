# Daysandbox Bot Documentation

daysandbox_bot is telegram bot that automatically deletes spam messages posted into your chat.

This bot uses simple but powerful method to detect spam. Message counts as spam if:

 * author of message joined chat in less than 24 hours
 * AND:
    * message contains link
    * OR message is forwarded from other chat

You can change safe time which is 24 hours by default.

## Installation

This instructions are specific too desktop telegram client. It could be a bit different on mobile client.

* You have to be admin of the chat
* Open your chat in telegram client
* Click on chat title (at the top of window)
* In the opened window click on the three dots icon (right to the label "Group Info")
* In the opened menu click on "Manage Group"
* In the opened window click on "Administrators"
* In the opened window click on "Add administator" (at the bottom of window)
* In the opened window enter "daysandbox_bot" (without quotes) in the search input element
* The search results will be refreshed and you'll see daysandbox_bot item with yellow pacman icon.
  The name of bot **MUST** be exactly **daysandbox_bot**.
  If you dot not see such name (on mobile client) then it is probably bug in telegram. Try desktop client.
* Click on that daysandbox_bot item
* In the opened window set "Delete messages" permission (checkbox should be blue color) and unset all other permissions
  (checkboxes should be red)
* Click "Save" 

## Feedback

Write me on [lorien@lorien.name](mailto:lorien@lorien.name)
