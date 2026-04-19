import discord


# =====================
# 👑 ADMIN CHECK (CORE)
# =====================
def is_admin(bot, user: discord.Member):

    try:
        role_id = bot.brain.role("ADMIN_ROLE")

        if not role_id:
            return False

        return any(r.id == int(role_id) for r in user.roles)

    except Exception as e:
        print("[PERMISSION ERROR]", e)
        return False


# =====================
# 🚫 ADMIN ONLY GUARD
# =====================
async def admin_only(interaction: discord.Interaction):

    if not isinstance(interaction.user, discord.Member):
        return False

    if is_admin(interaction.client, interaction.user):
        return True

    await interaction.response.send_message(
        "❌ คุณไม่มีสิทธิ์ใช้ฟีเจอร์นี้",
        ephemeral=True
    )

    return False


# =====================
# 🔒 REQUIRE ADMIN (SHORT ALIAS)
# =====================
async def require_admin(interaction: discord.Interaction):
    return await admin_only(interaction)


# =====================
# 👁️ VIEW VISIBILITY (FIXED)
# =====================
def hide_for_non_admin(bot, user: discord.Member):

    try:
        # True = show
        return is_admin(bot, user)
    except:
        return False


# =====================
# 🎫 TICKET LIMIT (FIXED)
# =====================
def can_open_ticket(bot, user_id):

    try:
        cur = bot.mem.conn.cursor()

        # FIX: your schema = order_id, channel_id
        cur.execute(
            "SELECT COUNT(*) FROM tickets WHERE channel_id=?",
            (str(user_id),)
        )

        count = cur.fetchone()[0]

        return count == 0

    except Exception as e:
        print("[PERMISSION ERROR] ticket check:", e)
        return False
