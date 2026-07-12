# gatito

## Minimalistic discord bot: personal notes, reminders, daily messages and duolingo style streaks

## Note taking under 3 seconds with reminders
Use this bot to write down your reminders in less than 3 seconds. Example:

```!nota My note here sabado```

And there, I scheduled my note for next Saturday (Sábado in portuguese) and I know I will get reminders for `My note here` on Friday night and on Saturday morning.
All on Discord, that you always check! Some more commands:

- You can list all the notes: `!lista`
- Cancel a note by ID: `!cancelar 4`
- And ask for help if you ever forget how it works: `!ajuda`

## Duolingo style streaks

I can keep track of my music studying streak:

```!streak music```

And I will be keeping a streak: with streak freezes every 5 days and a timeout if I slack off too much 


## Send custom messages

You can use the HTTP API to send custom messages:
```
curl -X POST -H "Content-Type: application/json" -d '{"message": "This is my test message"}' http://127.0.0.1:5000/message
```