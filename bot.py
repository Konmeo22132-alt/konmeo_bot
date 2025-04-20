import discord
import openai
import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy token từ file .env
DISCORD_TOKEN = os.getenv('MTM2MzE1NjY1NjYwNjgxMDI5Mw.GuwTJH.PI79Eg6cZQS3AcokBtz4cVZgHAwgLwgEb9sLsw')
OPENAI_API_KEY = os.getenv('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')

# Thiết lập OpenAI API
openai.api_key = OPENAI_API_KEY

# Tạo client Discord
intents = discord.Intents.default()
intents.message_content = True  # Đảm bảo bot có thể đọc tin nhắn
client = discord.Client(intents=intents)

# Biến để lưu kênh được chỉ định
active_channel = None

# Khi bot sẵn sàng
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Khi có tin nhắn mới
@client.event
async def on_message(message):
    global active_channel

    # Nếu tin nhắn gửi từ bot thì bỏ qua
    if message.author == client.user:
        return

    # Xử lý lệnh .bot <kênh>
    if message.content.startswith('.bot'):
        # Kiểm tra và lưu kênh được chỉ định
        try:
            channel_name = message.content.split(' ')[1]
            channel = discord.utils.get(message.guild.text_channels, name=channel_name)
            if channel:
                active_channel = channel
                await message.channel.send(f'Bot sẽ chỉ hoạt động trong kênh {channel_name}.')
            else:
                await message.channel.send('Kênh không tồn tại.')
        except IndexError:
            await message.channel.send('Vui lòng cung cấp tên kênh.')

    # Nếu bot đang hoạt động trong kênh này, trả lời tin nhắn hoặc file txt/lua
    if active_channel and message.channel == active_channel:
        if message.content.endswith('.txt') or message.content.endswith('.lua'):
            await process_file(message)

        # Trả lời các tin nhắn trực tiếp
        elif message.content.startswith('!chat'):
            prompt = message.content[6:]  # Lấy câu hỏi từ tin nhắn

            # Gọi OpenAI để lấy phản hồi
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",  # Hoặc engine bạn muốn
                    prompt=prompt,
                    max_tokens=100,
                    temperature=0.7
                )

                bot_response = response.choices[0].text.strip()

                # Gửi phản hồi của bot vào Discord
                await message.channel.send(bot_response)

            except Exception as e:
                await message.channel.send(f'Error: {str(e)}')

# Xử lý file txt hoặc lua
async def process_file(message):
    try:
        # Tải file lên nếu có
        attachment = message.attachments[0]
        if attachment.filename.endswith('.txt') or attachment.filename.endswith('.lua'):
            file_content = await attachment.read()
            file_content = file_content.decode('utf-8')

            # Bot sẽ trả lời nội dung file
            await message.channel.send(f'File nội dung:\n{file_content}')
        else:
            await message.channel.send('Vui lòng gửi file .txt hoặc .lua.')
    except Exception as e:
        await message.channel.send(f'Error processing file: {str(e)}')

# Chạy bot
client.run(DISCORD_TOKEN)
