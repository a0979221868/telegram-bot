# -*- coding: utf-8 -*-
import asyncio
import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
import nest_asyncio

# 配置
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8424641311:AAG2fAmUNMt02yD8BAaQTuK4VleAmlMw9KQ')
RECEIVE_ADDRESS = os.environ.get('RECEIVE_ADDRESS', 'TV7bNa8iJDwUhS2MQL9EpfnVWiVHiMCe1e')

# 日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 存储用户会话
user_sessions = {}

# ========== 键盘定义 ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🧪 创建测试单", callback_data='order_test')],
        [InlineKeyboardButton("📊 创建1.1倍订单", callback_data='order_1.1x')],
        [InlineKeyboardButton("📈 创建1.5倍订单", callback_data='order_1.5x')],
        [InlineKeyboardButton("⭐️ 创建2.0倍高级订单", callback_data='order_2.0x')],
        [InlineKeyboardButton("👨‍💻 客服中心", callback_data='support')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== Flask 保持运行 ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== 命令处理 ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"✅ 您好 {user_name}，欢迎使用自助黑U兑换机器人\n\n点击下方按钮创建订单",
        reply_markup=get_main_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data

    if data == 'order_test':
        user_sessions[user_id] = {'step': 'address'}
        await query.edit_message_text("📝 请输入您的TRC20收款地址：")
    elif data == 'support':
        await query.edit_message_text("👨‍💻 客服：@Yong255")
    elif data == 'cancel':
        await query.edit_message_text("已取消", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in user_sessions:
        await update.message.reply_text(
            f"✅ 订单创建成功！\n\n您的地址：{text}\n请转账到：{RECEIVE_ADDRESS}\n\n转账后联系客服 @Yong255"
        )
        del user_sessions[user_id]
    else:
        await update.message.reply_text("请先点 /start 开始", reply_markup=get_main_keyboard())

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 机器人启动中...")
    await application.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    
    # 啟動 Flask
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 啟動機器人
    asyncio.run(main())
