# Boomby

## Setting up
Check the [requirements.txt](https://github.com/Eragonaz/Boomby/blob/master/requirements.txt) for dependencies required and how to install them.


### 1) Install dependencies:
`python -m pip install -r requirements.txt`

Install ffmpeg from their official [website](https://ffmpeg.org/download.html) and add the `bin` folder to your `$(PATH)`.


### 2) Create `bot_token.py` file

Create a new file `bot_token.py` and add the following in the file:\
`str_token = 'YOUR_BOT_TOKEN_HERE'`\

Ensure to replace YOUR_BOT_TOKEN_HERE with your bot's token.\
Ensure that the file in the [src](https://github.com/Eragonaz/Boomby/blob/master/src/) directory (same directory as [main.py](https://github.com/Eragonaz/Boomby/blob/master/src/main.py) 

---
## Commands

#### `!join` - Boomby will join the voice-channel that you're currently connected to.
###### Alias - `!j`

#### `!disconnect` - Boomby will disconnect from the current voice-channel its connected to.
###### Alias -`!d`

#### `!play [search words/URL]` - Plays or adds the music. (Plays if there's nothing in queue)
###### Alias - `!p`

#### `!queue` - Boomby will list out current playing song  and up-next in queue songs.
###### Alias - `!q`

#### `!remove [queue_index]` - Removes the song at the queue index from the queue. Use `!queue` to determine its queue index.
###### Alias - `!rm`

#### `!skip` - Skips the currently playing song and plays the next one in queue.
###### Alias - `!s`

#### `!pause` - Pauses the currently playing song.
###### Alias - `!ps`

#### `!resume` - Resumes the currently paused song.
###### Alias - `!rs` 

#### `!stop` - Stops the currently playing song and clears the queue as well.
###### Alias - `!st`
---
