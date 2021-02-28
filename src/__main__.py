import discord
import json
import todoist

from github import Github
from github.GithubException import UnknownObjectException, GithubException
from todoist.api import SyncError

client: discord.Client = discord.Client()

botUserId: int = -1

with open("config.json", "r") as f:
    config = json.load(f)
    TOKEN = config["discord_token"]
    ChannelId: int = int(config["discord_channel_id"])
    OwnerUserId: int = int(config["owner_user_id"])
    TodoistAPIKEY = config["todoist_apikey"]
    GitHubAPIKEY = config["github_apikey"]

api = todoist.TodoistAPI(TodoistAPIKEY)
api.sync()

full_name = api.state["user"]["full_name"]
print("Todoist Login complete: {}".format(full_name))

g = Github(GitHubAPIKEY)
print("GitHub Login complete: {}".format(g.get_user().name))


def is_repository_exists(repo: str):
    """
    リポジトリが存在するかどうか

    :param repo: リポジトリ名 e.g. jaoafa/jaoafa/jao-Minecraft-Server
    :return: boolean
    """
    print("is_repository_exists", repo)
    try:
        g.get_repo(repo)
        return True
    except UnknownObjectException as e:
        return False


@client.event
async def on_ready():
    global botUserId
    botUser = client.user
    print("Discord Login complete: {}#{}".format(botUser.name, botUser.discriminator))
    botUserId = int(botUser.id)


@client.event
async def on_message(message: discord.Message):
    """
    新しいメッセージを受信したときに発火

    ・システムが勝手に作るピン止め通知メッセージを削除する
    ・指定チャンネルからのメッセージかつBot以外のメッセージの場合、ピン止めを行い:new:リアクションを付与する
    """
    # システムによるピン通知メッセージを削除
    if message.type == discord.MessageType.pins_add and message.author.id == botUserId:
        await message.delete()
        return  # ピンメッセージの場合ここで終了

    if message.author.bot:
        return  # Botからの送信の場合除外

    if message.channel.id != ChannelId:
        return  # TODOチャンネル以外からのメッセージの場合除外

    await message.add_reaction("🆕")
    try:
        await message.pin()
    except discord.HTTPException as e:
        await message.reply("Failed to pin", delete_after=10)
        print(e)
        return


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """
    メッセージにリアクションが追加された場合に発火

    ・ユーザーが:white_check_mark:をつけた場合、タスクが完了したものとしてピン止めを解除する。
    →タスク完了時はBotも:white_check_mark:をつける
    ・Owner(コンフィグで指定)が:pencil:をリアクションした場合、Todoistに追加する
    ・Ownerが:clipboard:をリアクションした場合、GitHub jaoafa/jao-Minecraft-ServerのIssueに登録する。
    →この際、メッセージ内に issue:xxxx/xxxx があればそのプロジェクトのIssueに追加する
    """
    if payload.channel_id != ChannelId:
        return

    channel: discord.TextChannel = client.get_channel(ChannelId)

    message_id = payload.message_id
    message: discord.Message = await channel.fetch_message(message_id)

    # ユーザーが:white_check_mark:をつけた場合、タスクが完了したものとしてピン止めを解除する。
    if payload.emoji.name == "✅":
        await message.unpin()
        await message.add_reaction("✅")
        await message.remove_reaction("🆕", discord.Object(botUserId))

    # Ownerが:pencil:をリアクションした場合、Todoistに追加する
    if payload.emoji.name == "📝" and payload.user_id == OwnerUserId:
        content: str = message.content
        contents: list[str] = content.split(" ")
        contents = list(filter(lambda s: not s.startswith("repo:"), contents))

        try:
            api.items.add(" ".join(contents))
            api.commit()

            await message.add_reaction("📝")
        except SyncError as e:
            await message.reply("Todoistに追加できませんでした。", delete_after=10)
            print(e)

    # Ownerが:clipboard:をリアクションした場合、GitHub jaoafa/jao-Minecraft-ServerのIssueに登録する。
    if payload.emoji.name == "📋" and payload.user_id == OwnerUserId:
        content: str = message.content
        contents: list[str] = content.split(" ")
        repo = list(map(lambda s: s.split(":")[1], filter(lambda s: s.startswith("repo:"), contents)))
        contents = list(filter(lambda s: not s.startswith("repo:"), contents))

        issue_name = "jaoafa/jao-Minecraft-Server"
        if len(repo) >= 1 and "/" not in repo[0] and is_repository_exists("jaoafa/{}".format(repo[0])):
            issue_name = "jaoafa/{}".format(repo[0])
        elif len(repo) >= 1 and "/" not in repo[0] and is_repository_exists("book000/{}".format(repo[0])):
            issue_name = "book000/{}".format(repo[0])
        elif len(repo) >= 1 and "/" not in repo[0]:
            await message.reply(
                "リポジトリがjaoafaオーガナイゼーション・book000ユーザーに見つかりませんでした。({})".format(repo[0]),
                delete_after=10
            )
            return
        elif len(repo) >= 1:
            if is_repository_exists(repo[0]):
                issue_name = repo[0]
            else:
                await message.reply("リポジトリが見つかりませんでした。({})".format(repo[0]), delete_after=10)
                return

        title: str = content.split("\n")[0]
        try:
            g.get_repo(issue_name).create_issue(
                title,
                "## Contents\n"
                "```\n"
                "{}\n"
                "```\n"
                "## Message URL\n"
                "{}".format(
                    " ".join(contents),
                    message.jump_url
                )
            )

            await message.add_reaction("📋")
        except GithubException as e:
            print(e)
            await message.reply("リポジトリにIssueを投稿できませんでした。", delete_after=10)

if __name__ == "__main__":
    client.run(TOKEN)
