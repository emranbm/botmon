# BotMon
A monitoring system for Telegram bots.  

## Usage
1. Make your bot respond to the command `/botmoncheck`. (The response can be any text.)
2. Infrom your bot's username to [@thebotmon_bot](https://t.me/thebotmon_bot) at Telegram.
3. Done! BotMon will periodically (every minute) send `/botmoncheck` to your bot and if it doesn't reply for consecutive 5 minutes, BotMon will send an alert to you!

## FAQ
### BotMon itself is a bot! how it is monitored to be up itself?!
BotMon2 bot is developed to monitor BotMon; and BotMon3 monitors BotMon2, and so on!  
LOL, just kidding!  
Actually, BotMon sends regular heartbeats to me, and if I don't get such heartbeats for a while, it indicates a *passive alert*! i.e. I'm addicted to recieving BotMon heartbeats, on a regular basis!  

### How much it costs?
BotMon is curently free and I'm doing my best to keep it free.
