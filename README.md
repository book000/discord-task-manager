# discord-task-manager

Manage tasks in Discord.

## Features

- Make each message sent to the channel a "task"
- Give 🆕 reaction when posted
- When the task is completed, the user gives a ✅ reaction
- If the Owner (set in the config) has a 📝 reaction, register it with Todoist
- If the Owner gives a 📋 reaction, register it in the issue of GitHub [jaoafa/jao-Minecraft-Server](https://github.com/jaoafa/jao-Minecraft-Server).  
  At this time, if there is `repo:xxxx/xxxx` in the message, add it to the issue of the project.

## Configuration

Rewrite [config.sample.json](config.sample.json) and rename to `config.json`.

- `discord_token`: Discord Bot Token
- `discord_channel_id`: Discord channel ID for task management
- `owner_user_id`: ID of the user to treat as a post trigger reaction to Todoist and GitHub
- `todoist_apikey`: Todoist API Key
- `github_apikey`: GitHub API Key

## License

The license for this project is [MIT License](LICENSE).
