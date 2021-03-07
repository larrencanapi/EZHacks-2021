import discord
import os
import random
from keep_alive import keep_alive
from dataprep.connector import connect, info

client = discord.Client()

sing_words = ["sing" , "karaoke", "singing"] # when word is seen in chat will trigger bot 

starter_singing = [
  "Time to Sing?",
  "Let's Karaoke!",
  "Someone called Karaoke Bot?"
  ]

async def get_lyrics(song_name):
  #https://www.youtube.com/watch?v=
  print("get_lyrics")
  conn = connect('./musixmatch', _auth={'access_token':'musixmatchToken'}, _concurrency=3)
  track_id = await conn.query('track_matches', q_track=song_name)
  commontrack_id = track_id['commontrack_id']
  lyrics = await conn.query('track_lyrics',commontrack_id=commontrack_id[0])
  #print(lyrics['lyrics_body'][0])
  return lyrics['lyrics_body'][0]

@client.event
# ready to start when begin to be used
async def on_ready():      
  print('We have logged in as {0.user}'
  .format(client))

# Command Flow
# run command "$findLyric songName" in Discord
# Bot returns Top 5 Lyrics that best match
# users selects 1 out of the 5 
# Bot returns the user selected lyrics, URL, etc

async def get_song(song_name):
  prefix = 'https://www.youtube.com/watch?v='
  conn = connect('./youtube', _auth={'access_token':'youtubeToken'}, _concurrency=3)
  song_table = await conn.query('videos', q=song_name, part='snippet', _count=5)
  videoId = song_table['videoId'][0]
  return prefix + videoId
  
async def random_song_name():
  conn = connect('musixmatch', _auth={'access_token':'musixmatchToken'}, _concurrency=3)
  top_tracks = await conn.query('top_tracks', _count=50)
  rng_track = top_tracks.sample()
  print(rng_track['name'].to_string(index=0))
  return rng_track['name'].to_string(index=0)

  


async def quote_lyric(song_name):
  #print("get_lyrics")
  conn = connect('./musixmatch', _auth={'access_token':'musixmatchToken'}, _concurrency=3)
  track_id = await conn.query('track_matches', q_track=song_name)
  commontrack_id = track_id['commontrack_id']
  lyrics = await conn.query('track_lyrics',commontrack_id=commontrack_id[0])

  #print(lyrics['lyrics_body'][0])
  lyricArray = lyrics['lyrics_body'][0].split("\n")
  resultArray = list(filter(None, lyricArray))
  resultArray.pop()

  resultString = random.choice(resultArray)
  
  resultString = "\"" + resultString + "\"" + "\n"
  resultString = resultString + "  - " + song_name
  
  return resultString
  #return lyrics['lyrics_body'][0]

async def help_command():
  return "Bot Commands\n\n$song songname   - get a song from youtube\n$lyric songname    - get lyrics for a song\n$quote songname - quote a random lyric from the song\n"



@client.event
async def on_message(message):
  if message.author == client.user:    # if message is from the bot itself; it will do nothing
    return
  
  msg = message.content

  if msg.startswith('$hello'):   # when users use $hello will send message
    await message.channel.send('Hello!')

  """
  if msg.startswith('$lyric'):
    await message.channel.send('Hello! Respond Back')
    userInput = await client.wait_for('message')
    print(userInput.content)
    await message.channel.send(userInput.content)
  """
  
  if msg.startswith('$song'):
    userInput = msg.split("$song ", 1)[1]
    songString = await get_song(userInput)
    await message.channel.send(songString)
    
  if msg.startswith('$lyric'):
    userInput = msg.split("$lyric ", 1)[1]
    lyricString = await get_lyrics(userInput)
    await message.channel.send(lyricString)

  if msg.startswith('$quote'):
    userInput = msg.split("$quote ", 1)[1]
    lyricQuote = await quote_lyric(userInput)
    await message.channel.send(lyricQuote)

  if msg.startswith('$karaoke'):
    rng_song = await random_song_name()
    await message.channel.send(rng_song)
    songString = await get_song(rng_song)
    await message.channel.send(songString)
    lyricString = await get_lyrics(rng_song)
    await message.channel.send(lyricString)

  '''
  if msg.startswith('$karaoke'):
    userInput = msg.split("$quote ", 1)[1]
    rng_song = await random_song_name()
    songString = await get_song(rng_song)
    await message.channel.send(songString)
    lyricQuote = await quote_lyric(rng_song)
    await message.channel.send(lyricQuote)
  '''

  if msg.startswith('$help'):
    helpString = await help_command()
    await message.channel.send(helpString)
 
  if any(word in msg for word in sing_words):
    await  message.channel.send(random.choice(starter_singing))

    
    
keep_alive()    #keeps the bot running and not sleep
client.run(os.getenv('TOKEN'))    # password for bot.
