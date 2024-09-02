import discord
from connect_four import ConnectBoard
from connect_four import number_emojis
from game_dict import game_dict
import utils
from config import TOKEN


intents = discord.Intents.all()

# 接続に必要なオブジェクトを生成
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)


# 起動時に動作する処理
@bot.event
async def on_ready():
    print(f'{bot.user} がDiscordに接続しました。')
    await tree.sync()


# /vsコマンドの動作
@tree.command(name='vs', description='対戦相手を選択') 
async def vs(interaction: discord.Interaction, opponent: discord.Member, width: int = 7, height: int = 6, win_number: int = 4): 
    # コマンド実行したときの処理
    message_send = ""
    is_valid = True
    if opponent.bot:
        is_valid = False
        message_send = "Botとは対戦できません"
    if opponent.id == interaction.user.id:
        is_valid = False
        message_send = "自分自身とは対戦できません"
    if (is_host_playing := interaction.user.id in game_dict) or opponent.id in game_dict:
        is_valid = False
        message_send = ("あなた" if is_host_playing else "対戦相手") + "はすでに対戦中です"
    
    if not is_valid:
        embed = discord.Embed(title="エラー", description=message_send, color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    game = ConnectBoard(interaction.user, opponent, width, height, win_number)
    game_dict[interaction.user.id] = game
    game_dict[opponent.id] = game
    message_send = f"<@{opponent.id}>\n対戦を受けますか？\nボードサイズ: 横: {width} x 縦: {height}\n勝利条件: {win_number}\n\n🆗: 受ける\n🆖: 拒否する"
    embed = discord.Embed(title="コネクト・フォー", description=message_send, color=0x9FE2BF)
    await interaction.response.send_message(embed=embed)
    msg: discord.Message = await interaction.original_response()
    await msg.add_reaction("🆗")
    await msg.add_reaction("🆖")
    game.msg = msg

# /surrenderコマンドの動作
@tree.command(name='surrender', description='降参する')
async def surrender(interaction: discord.Interaction):
    game = game_dict[interaction.user.id]
    is_valid = True
    if interaction.user.id not in game_dict:
        is_valid = False
    if not game.is_started or game.is_finished:
        is_valid = False
    
    if not is_valid:
        embed = discord.Embed(title="エラー", description="対戦中ではありません", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.send_message("** **")
    msg = await interaction.original_response()
    await msg.delete()
    win_player_id = game.host_id if interaction.user.id == game.opponent_id else game.opponent_id
    message_send = f"<@{interaction.user.id}>が降参しました\n" + game.get_text().replace("その場所には置けません\n", "") + f"\n勝者: {game.get_color(win_player_id)}<@{win_player_id}>"
    embed = discord.Embed(title="コネクト・フォー", description = message_send, color=0x9FE2BF)
    game.is_finished = True
    await game.msg.edit(embed=embed)
    for emoji in list(number_emojis.values()):
        await game.msg.remove_reaction(emoji, bot.user)
    del game_dict[game.host_id]
    del game_dict[game.opponent_id]
    
# リアクションが追加されたときの処理
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if user.bot:
        return
    if user.id not in game_dict:
        return
    game = game_dict[user.id]
    if game.is_finished:
        return
    if reaction.message.id == game.msg.id:
        # 対戦の確認
        if not game.is_started:
            if reaction.emoji == '🆖':
                await reaction.remove(user)
                if user.id != game.opponent_id:
                    return
                for emoji in ["🆗", "🆖"]:
                    await reaction.message.remove_reaction(emoji, bot.user)
                embed = discord.Embed(title="コネクト・フォー", description="対戦をキャンセルしました", color=0x9FE2BF)
                await reaction.message.edit(embed=embed)
                del game_dict[game_dict[user.id].host_id]
                del game_dict[user.id]
                return

            elif reaction.emoji == '🆗':
                await reaction.remove(user)
                if user.id != game.opponent_id:
                    return
                for emoji in ["🆗", "🆖"]:
                    await reaction.message.remove_reaction(emoji, bot.user)

                game.is_started = True
                message_send = f"対戦を開始します\n{game.get_color(game.turn_user_id)}<@{game.turn_user_id}>のターンです\n" + game.get_text()
                embed = discord.Embed(title="コネクト・フォー", description=message_send, color=0x9FE2BF)
                await reaction.message.edit(embed=embed)
                for i in range(game.width):
                    await reaction.message.add_reaction(f"{number_emojis[i+1]}")
                return

        # ゲーム中の処理
        else:
            if reaction.emoji in list(number_emojis.values())[0:game.width]:
                if user.id != game.turn_user_id:
                    await reaction.remove(user)
                    return
                emoji_number = utils.get_key_from_value(number_emojis, reaction.emoji)
                if game.turn_user_id == game.host_id:
                    game.my_turn(emoji_number)
                    
                    game.change_turn()
                    message_send = (f"{game.get_color(game.turn_user_id)}<@{game.turn_user_id}>のターンです\n" if not game.is_finished else "") + game.get_text()
                    embed = discord.Embed(title="コネクト・フォー", description=message_send, color=0x9FE2BF)
                    await reaction.message.edit(embed=embed)
                
                else:
                    game.your_turn(emoji_number)
                    game.change_turn()
                    message_send = (f"{game.get_color(game.turn_user_id)}<@{game.turn_user_id}>のターンです\n" if not game.is_finished else "") + game.get_text()
                    embed = discord.Embed(title="コネクト・フォー", description=message_send, color=0x9FE2BF)
                    await reaction.message.edit(embed=embed)
                
                if game.is_finished:
                    for emoji in list(number_emojis.values()):
                        await reaction.message.remove_reaction(emoji, bot.user)
                    del game_dict[game.host_id]
                    del game_dict[game.opponent_id]
        await reaction.remove(user)
                

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)
