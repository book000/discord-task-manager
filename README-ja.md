# discord-task-manager

Discord でタスクを管理する。

## Features

- チャンネルに送信されたメッセージひとつひとつを「タスク」とする
- 投稿された際に🆕リアクションを付与する
- タスクが完了した際、ユーザーは✅リアクションをつける
- Owner（コンフィグで設定）が📝リアクションをつけた場合、Todoistへ登録する
- Ownerが📋リアクションをつけた場合、GitHub [jaoafa/jao-Minecraft-Server](https://github.com/jaoafa/jao-Minecraft-Server) のIssueに登録する。  
  この際、メッセージ内に `repo:xxxx/xxxx` があればそのプロジェクトのIssueに追加する

## Configuration

`config.sample.json` を `config.json` に名前を変更したうえで編集してください。

- `discord_token`: Discord Bot のトークン
- `discord_channel_id`: タスク管理を行う Discord チャンネル ID
- `owner_user_id`: Todoist と GitHub への投稿トリガーリアクションとして扱うユーザーのID
- `todoist_apikey`: Todoist の API Key
- `github_apikey`: GitHub の API Key

## License

このプロジェクトのライセンスは [MIT License](LICENSE) です。
