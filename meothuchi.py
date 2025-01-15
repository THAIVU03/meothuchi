from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import pandas as pd
import os

# Đường dẫn file dữ liệu
DATA_FILE = "expenses.csv"

# Khởi tạo file nếu chưa tồn tại
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "UserID", "Category", "Amount"]).to_csv(DATA_FILE, index=False)

# Hàm bắt đầu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🎉 Chào mừng bạn đến với Bot Quản Lý Chi Tiêu!\n"
        "Dùng các lệnh sau để bắt đầu:\n"
        "/add <số tiền (nghìn)> <danh mục> - Thêm chi tiêu.\n"
        "/view - Xem tổng chi tiêu.\n"
        "/reset - Xóa tất cả dữ liệu.\n"
        "/help - Xem hướng dẫn."
    )

# Hàm thêm chi tiêu
async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        args = context.args
        amount = float(args[0]) * 1000  # Chuyển từ nghìn sang đơn vị VNĐ
        category = " ".join(args[1:])
        if not category:
            category = "Khác"

        user_id = update.effective_user.id
        username = update.effective_user.full_name

        # Ghi dữ liệu vào file CSV
        data = pd.read_csv(DATA_FILE)
        new_entry = {
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "UserID": user_id,
            "Category": category,
            "Amount": amount
        }
        data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
        data.to_csv(DATA_FILE, index=False)

        await update.message.reply_text(
            f"✅ {username} đã thêm chi tiêu {amount:,.0f}đ cho danh mục '{category}'."
        )
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Sai cú pháp! Hãy dùng: /add <số tiền (nghìn)> <danh mục>")

# Hàm xem chi tiêu
async def view_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = pd.read_csv(DATA_FILE)
    if data.empty:
        await update.message.reply_text("💡 Hiện tại chưa có chi tiêu nào.")
    else:
        user_id = update.effective_user.id
        user_data = data[data["UserID"] == user_id]

        if user_data.empty:
            await update.message.reply_text("💡 Bạn chưa có chi tiêu nào.")
        else:
            summary = user_data.groupby("Category")["Amount"].sum()
            total = user_data["Amount"].sum()
            response = "📊 Tổng chi tiêu:\n" + "\n".join(
                [f"{cat}: {amt:,.0f}đ" for cat, amt in summary.items()]
            )
            response += f"\n\n💰 Tổng cộng: {total:,.0f}đ"
            await update.message.reply_text(response)

# Hàm xóa dữ liệu
async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    data = pd.read_csv(DATA_FILE)
    data = data[data["UserID"] != user_id]  # Xóa dữ liệu của người dùng hiện tại
    data.to_csv(DATA_FILE, index=False)
    await update.message.reply_text("🗑️ Dữ liệu chi tiêu của bạn đã được xóa.")

# Hàm trợ giúp
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/add <số tiền (nghìn)> <danh mục> - Thêm chi tiêu.\n"
        "/view - Xem tổng chi tiêu.\n"
        "/reset - Xóa tất cả dữ liệu.\n"
        "/help - Xem hướng dẫn."
    )

# Khởi chạy bot
def main():
    TOKEN = "8017990460:AAFxEWssjchDBukL8UGXUyBq_28Qp7ySjwM"  # Thay bằng token của bạn

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_expense))
    app.add_handler(CommandHandler("view", view_expenses))
    app.add_handler(CommandHandler("reset", reset_data))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot đang vào việc ...")
    app.run_polling()

if __name__ == "__main__":
    main()